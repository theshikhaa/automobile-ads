from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
import json

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from core.config import (
    MAX_LOG_SIZE,
    MODEL_PATH,
    PREDICTION_LOG_PATH,
    PSI_THRESHOLD,
    REFERENCE_DATA_PATH,
    SHAP_BACKGROUND_SIZE,
)
from schemas.automobile import AutomobileInput
from services.feature_engineering import add_engineered_features

FEATURE_ORDER = list(AutomobileInput.model_fields.keys())
NUMERIC_FEATURES = [
    name
    for name, field in AutomobileInput.model_fields.items()
    if field.annotation is float
]
CATEGORICAL_FEATURES = [
    name
    for name, field in AutomobileInput.model_fields.items()
    if field.annotation is str
]


class PredictionService:
    def __init__(self) -> None:
        self.model = joblib.load(MODEL_PATH)
        self.preprocessor = self.model.named_steps["preprocessor"]
        self.regressor = self.model.named_steps["model"]
        self.transformed_feature_names = list(self.preprocessor.get_feature_names_out())
        self.categories = self._extract_categories()
        self.reference_df = self._load_reference()
        self._log_lock = Lock()
        self.prediction_log = self._load_log()
        self._shap_explainer = None
        self._shap_background = None
        self.global_shap = self._compute_global_shap()
        self.metrics = self._compute_metrics()

    def _extract_categories(self) -> dict[str, list[str]]:
        encoder = self.preprocessor.named_transformers_["cat"]
        cat_cols = self.preprocessor.transformers_[1][2]
        return {col: [str(v) for v in values] for col, values in zip(cat_cols, encoder.categories_)}

    def _load_reference(self) -> pd.DataFrame:
        if not Path(REFERENCE_DATA_PATH).exists():
            return pd.DataFrame()
        df = pd.read_csv(REFERENCE_DATA_PATH)
        missing = [col for col in FEATURE_ORDER if col not in df.columns]
        if missing:
            return pd.DataFrame()
        return df

    def _load_log(self) -> deque:
        path = Path(PREDICTION_LOG_PATH)
        if not path.exists():
            return deque(maxlen=MAX_LOG_SIZE)
        try:
            records = json.loads(path.read_text(encoding="utf-8"))
            return deque(records, maxlen=MAX_LOG_SIZE)
        except (json.JSONDecodeError, OSError):
            return deque(maxlen=MAX_LOG_SIZE)

    def _persist_log(self) -> None:
        Path(PREDICTION_LOG_PATH).parent.mkdir(parents=True, exist_ok=True)
        Path(PREDICTION_LOG_PATH).write_text(
            json.dumps(list(self.prediction_log), indent=2),
            encoding="utf-8",
        )

    def _frame_from_payload(self, data: dict) -> pd.DataFrame:
        return pd.DataFrame([data], columns=FEATURE_ORDER)

    def predict(self, data: dict) -> float:
        df = self._frame_from_payload(data)
        prediction = float(self.model.predict(df)[0])
        record = {
            **data,
            "predicted_price": round(prediction, 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        with self._log_lock:
            self.prediction_log.append(record)
            self._persist_log()
        return prediction

    def _get_shap_explainer(self):
        if self._shap_explainer is not None:
            return self._shap_explainer, self._shap_background

        if self.reference_df.empty:
            return None, None

        try:
            import shap
        except ImportError:
            return None, None

        background = self.reference_df[FEATURE_ORDER].head(SHAP_BACKGROUND_SIZE)
        transformed = self.preprocessor.transform(background)
        if hasattr(transformed, "toarray"):
            transformed = transformed.toarray()
        self._shap_background = transformed
        self._shap_explainer = shap.TreeExplainer(self.regressor)
        return self._shap_explainer, self._shap_background

    def _compute_global_shap(self) -> dict:
        if self.reference_df.empty:
            importances = self.regressor.feature_importances_
            ranked = sorted(
                zip(self.transformed_feature_names, importances),
                key=lambda item: item[1],
                reverse=True,
            )
            return {
                "source": "random_forest_feature_importance",
                "values": [
                    {"feature": name, "importance": round(float(value), 6)}
                    for name, value in ranked[:25]
                ],
            }

        explainer, background = self._get_shap_explainer()
        if explainer is None or background is None:
            importances = self.regressor.feature_importances_
            ranked = sorted(
                zip(self.transformed_feature_names, importances),
                key=lambda item: item[1],
                reverse=True,
            )
            return {
                "source": "random_forest_feature_importance",
                "values": [
                    {"feature": name, "importance": round(float(value), 6)}
                    for name, value in ranked[:25]
                ],
            }
        shap_values = np.array(explainer.shap_values(background))
        mean_abs = np.abs(shap_values).mean(axis=0)
        ranked = sorted(
            zip(self.transformed_feature_names, mean_abs),
            key=lambda item: item[1],
            reverse=True,
        )
        return {
            "source": "mean_abs_shap",
            "base_value": float(np.array(explainer.expected_value).reshape(-1)[0]),
            "values": [
                {"feature": name, "importance": round(float(value), 4)}
                for name, value in ranked[:25]
            ],
        }

    def explain(self, data: dict) -> dict:
        df = self._frame_from_payload(data)
        prediction = float(self.model.predict(df)[0])
        transformed = self.preprocessor.transform(df)
        if hasattr(transformed, "toarray"):
            transformed = transformed.toarray()

        explainer, _ = self._get_shap_explainer()
        if explainer is None:
            importances = self.regressor.feature_importances_
            contributions = sorted(
                [
                    {
                        "feature": name,
                        "shap_value": round(float(value) * 1000, 4),
                        "abs_shap": round(abs(float(value) * 1000), 4),
                    }
                    for name, value in zip(self.transformed_feature_names, importances)
                ],
                key=lambda item: item["abs_shap"],
                reverse=True,
            )
            top = contributions[:15]
            return {
                "predicted_price": round(prediction, 2),
                "base_value": None,
                "source": "random_forest_feature_importance",
                "top_contributions": top,
                "waterfall": {
                    "base_value": None,
                    "prediction": round(prediction, 2),
                    "steps": top,
                },
            }
        shap_values = np.array(explainer.shap_values(transformed))[0]
        expected = float(np.array(explainer.expected_value).reshape(-1)[0])

        contributions = sorted(
            [
                {
                    "feature": name,
                    "shap_value": round(float(value), 4),
                    "abs_shap": round(float(abs(value)), 4),
                }
                for name, value in zip(self.transformed_feature_names, shap_values)
            ],
            key=lambda item: item["abs_shap"],
            reverse=True,
        )
        top = contributions[:15]
        return {
            "predicted_price": round(prediction, 2),
            "base_value": round(expected, 2),
            "top_contributions": top,
            "waterfall": {
                "base_value": round(expected, 2),
                "prediction": round(prediction, 2),
                "steps": top,
            },
        }

    def _compute_metrics(self) -> dict:
        if self.reference_df.empty or "price" not in self.reference_df.columns:
            return {
                "available": False,
                "message": "Reference dataset with actual prices is required for metrics.",
            }

        features = self.reference_df[FEATURE_ORDER]
        y_true = self.reference_df["price"].astype(float)
        y_pred = self.model.predict(features)
        residuals = (y_true - y_pred).tolist()
        mae = float(mean_absolute_error(y_true, y_pred))
        rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
        r2 = float(r2_score(y_true, y_pred))
        mape = float(np.mean(np.abs((y_true - y_pred) / y_true)) * 100)

        residual_bins = pd.cut(pd.Series(residuals), bins=12)
        residual_hist = (
            residual_bins.value_counts()
            .sort_index()
            .rename_axis("bin")
            .reset_index(name="count")
        )
        residual_hist["bin"] = residual_hist["bin"].astype(str)

        pred_vs_actual = [
            {
                "actual": round(float(actual), 2),
                "predicted": round(float(pred), 2),
                "make": str(make),
            }
            for actual, pred, make in zip(
                y_true.head(80),
                y_pred[:80],
                self.reference_df["make"].head(80),
            )
        ]

        return {
            "available": True,
            "n_samples": int(len(y_true)),
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
            "r2": round(r2, 4),
            "mape": round(mape, 2),
            "mean_actual": round(float(y_true.mean()), 2),
            "mean_predicted": round(float(np.mean(y_pred)), 2),
            "residual_histogram": residual_hist.to_dict(orient="records"),
            "pred_vs_actual": pred_vs_actual,
            "note": "Metrics are computed on the UCI Automobile reference set after feature engineering.",
        }

    def _psi(self, expected: np.ndarray, actual: np.ndarray, bins: int = 10) -> float:
        expected = expected[np.isfinite(expected)]
        actual = actual[np.isfinite(actual)]
        if len(expected) < 10 or len(actual) < 5:
            return 0.0
        quantiles = np.linspace(0, 100, bins + 1)
        breaks = np.unique(np.percentile(expected, quantiles))
        if len(breaks) < 3:
            return 0.0
        expected_perc = np.histogram(expected, bins=breaks)[0] / len(expected)
        actual_perc = np.histogram(actual, bins=breaks)[0] / len(actual)
        expected_perc = np.clip(expected_perc, 1e-4, None)
        actual_perc = np.clip(actual_perc, 1e-4, None)
        return float(np.sum((actual_perc - expected_perc) * np.log(actual_perc / expected_perc)))

    def drift_report(self) -> dict:
        log_df = pd.DataFrame(list(self.prediction_log))
        if log_df.empty:
            return {
                "status": "insufficient_production_data",
                "message": "Make a few /predict calls first. Drift is measured against the UCI reference distribution.",
                "n_production": 0,
                "n_reference": int(len(self.reference_df)),
                "features": [],
            }

        features = []
        alerts = 0
        for col in NUMERIC_FEATURES:
            if col not in self.reference_df.columns or col not in log_df.columns:
                continue
            psi = self._psi(
                self.reference_df[col].astype(float).to_numpy(),
                log_df[col].astype(float).to_numpy(),
            )
            flag = "shift" if psi >= PSI_THRESHOLD else "stable"
            if flag == "shift":
                alerts += 1
            features.append(
                {
                    "feature": col,
                    "psi": round(psi, 4),
                    "status": flag,
                    "reference_mean": round(float(self.reference_df[col].mean()), 4),
                    "production_mean": round(float(log_df[col].mean()), 4),
                }
            )

        features.sort(key=lambda item: item["psi"], reverse=True)
        overall = "attention_required" if alerts else "stable"
        return {
            "status": overall,
            "threshold": PSI_THRESHOLD,
            "n_production": int(len(log_df)),
            "n_reference": int(len(self.reference_df)),
            "shifted_features": alerts,
            "features": features[:20],
        }

    def insights(self) -> dict:
        rf_importance = sorted(
            zip(self.transformed_feature_names, self.regressor.feature_importances_),
            key=lambda item: item[1],
            reverse=True,
        )
        price_by_body = []
        if not self.reference_df.empty and "price" in self.reference_df.columns:
            grouped = (
                self.reference_df.groupby("body_style")["price"]
                .mean()
                .sort_values(ascending=False)
            )
            price_by_body = [
                {"body_style": key, "avg_price": round(float(value), 2)}
                for key, value in grouped.items()
            ]

        price_by_make = []
        if not self.reference_df.empty and "price" in self.reference_df.columns:
            grouped = (
                self.reference_df.groupby("make")["price"]
                .mean()
                .sort_values(ascending=False)
                .head(10)
            )
            price_by_make = [
                {"make": key, "avg_price": round(float(value), 2)}
                for key, value in grouped.items()
            ]

        return {
            "model_type": type(self.regressor).__name__,
            "n_estimators": int(getattr(self.regressor, "n_estimators", 0)),
            "n_input_features": int(self.model.n_features_in_),
            "n_transformed_features": len(self.transformed_feature_names),
            "global_shap": self.global_shap,
            "random_forest_importance": [
                {"feature": name, "importance": round(float(value), 6)}
                for name, value in rf_importance[:20]
            ],
            "avg_price_by_body_style": price_by_body,
            "avg_price_by_make": price_by_make,
        }

    def schema(self) -> dict:
        defaults = self.sample_payload()
        fields = []
        for name in FEATURE_ORDER:
            if name in CATEGORICAL_FEATURES:
                fields.append(
                    {
                        "name": name,
                        "type": "categorical",
                        "options": self.categories.get(name, []),
                        "default": defaults[name],
                    }
                )
            else:
                fields.append(
                    {
                        "name": name,
                        "type": "numeric",
                        "default": defaults[name],
                    }
                )
        return {"fields": fields}

    def sample_payload(self) -> dict:
        if not self.reference_df.empty:
            row = self.reference_df.iloc[0]
            payload = {}
            for name in FEATURE_ORDER:
                value = row[name]
                payload[name] = float(value) if name in NUMERIC_FEATURES else str(value)
            return payload

        return {
            "symboling": 1,
            "normalized_losses": 122,
            "wheel_base": 98.4,
            "length": 173.2,
            "width": 65.6,
            "height": 53.0,
            "curb_weight": 2500,
            "engine_size": 130,
            "bore": 3.31,
            "stroke": 3.29,
            "compression_ratio": 9.0,
            "horsepower": 110,
            "peak_rpm": 5000,
            "city_mpg": 21,
            "highway_mpg": 27,
            "car_volume": 601900,
            "power_to_weight_ratio": 0.044,
            "average_mpg": 24.0,
            "engine_power_ratio": 0.846,
            "make": "toyota",
            "fuel_type": "gas",
            "aspiration": "std",
            "num_of_doors": "four",
            "body_style": "sedan",
            "drive_wheels": "fwd",
            "engine_location": "front",
            "engine_type": "ohc",
            "num_of_cylinders": "four",
            "fuel_system": "mpfi",
            "weight_category": "Medium",
            "fuel_efficiency_category": "Medium Efficiency",
            "engine_size_category": "Medium Engine",
            "horsepower_category": "Medium Power",
        }

    def enrich_payload(self, data: dict) -> dict:
        """Recompute derived volume, ratios, and bin labels from raw specs."""
        frame = add_engineered_features(pd.DataFrame([data]))
        row = frame.iloc[0].to_dict()
        payload = {}
        for name in FEATURE_ORDER:
            value = row[name]
            payload[name] = float(value) if name in NUMERIC_FEATURES else str(value)
        return payload

    def health(self) -> dict:
        return {
            "status": "healthy",
            "model_loaded": self.model is not None,
            "model_path": str(MODEL_PATH),
            "reference_rows": int(len(self.reference_df)),
            "logged_predictions": int(len(self.prediction_log)),
        }


prediction_service = PredictionService()
