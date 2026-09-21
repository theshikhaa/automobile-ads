# Responsible AI Checklist

This document is the Responsible AI report for the Automobile Price Prediction system (Experiments 6–7). The model estimates used-car prices from vehicle specifications. It does not identify people, but price systems can still affect buyers, sellers, insurers, and dealers.

## 1. Purpose and intended use

| Item | Status | Notes |
| --- | --- | --- |
| Problem statement is documented | Yes | Predict automobile list/market price from UCI Automobile-style features. |
| Intended users are named | Yes | Students, analysts, and demo users of the dashboard and API. |
| Out-of-scope uses are named | Yes | Not for loan underwriting, insurance pricing, automated purchasing, or legally binding valuations. |
| Human review is required for high-impact decisions | Yes | API responses are decision-support only. |

**Allowed:** academic demonstration, portfolio, exploratory pricing research.  
**Not allowed:** silent automation of credit, insurance, or consumer offers without a human in the loop.

## 2. Fairness

The training data is the UCI Automobile dataset (imports-85). It is small, 1980s-era, and skewed toward certain makes (especially Toyota). Price differences by make, body style, and engine size are expected physically, but they can also encode market bias.

| Check | Status | Evidence / action |
| --- | --- | --- |
| Sensitive personal attributes (race, gender, religion, income) are not model inputs | Pass | Features are vehicle specs only. |
| Protected-class proxies were reviewed | Watch | `make` can correlate with geography and brand prestige; do not treat it as a fairness-neutral field. |
| Group performance by `make` / `body_style` can be inspected | Pass | Dashboard Insights page shows average price by make and body style. |
| Disparate error monitoring | Partial | Reference metrics (MAE, RMSE, R², MAPE) are global. Slice-level error should be added before production. |
| No target leakage from identity | Pass | Target is vehicle `price`, not a person-level outcome. |
| Representation bias | Fail (dataset limit) | Luxury and rare makes have few rows; error will be higher for those groups. Documented, not “fixed” by oversampling in this lab. |

**Fairness rules for this project**

1. Do not use the model to set different prices for similar cars solely because of dealer or customer identity.
2. Treat `make` explanations in SHAP as market structure, not as a reason to discriminate against a buyer.
3. If this system were productionized, measure MAE by make, body style, and fuel type and set a maximum gap (for example, group MAE within 20% of overall MAE).

## 3. Privacy

| Check | Status | Notes |
| --- | --- | --- |
| No direct identifiers (name, email, phone, VIN, plate) | Pass | Request schema has none of these fields. |
| Training data is a public academic set | Pass | UCI Automobile / imports-85. |
| Logs do not store personal data | Pass | Prediction log stores vehicle features and predicted price only. |
| Retention | Pass (lab) | `data/prediction_log.json` is local, capped at 500 rows, and gitignored. |
| Data minimization | Pass | Only features required by the pipeline are collected. |
| Encryption in transit | Partial | Use HTTPS in any hosted deployment. Local Docker/HTTP is for development. |

**Do not** add customer names, VINs, or location to the payload. If a future version needs VIN decoding, hash or drop the identifier after feature extraction.

## 4. Consent

| Check | Status | Notes |
| --- | --- | --- |
| Users are told a model is making the estimate | Pass | Dashboard and API docs state this is a machine-learning estimate. |
| Users can decline | Pass | The service is opt-in: nothing is scored unless `/predict` or the form is submitted. |
| Training data consent | N/A / documented | UCI data is a public research dataset, not live customer data. |
| Logging consent | Pass (lab) | Dashboard copy states that submitted specs are stored locally for drift checks. Hosted deployments must show a consent notice before logging. |
| Right to delete lab logs | Pass | Delete `data/prediction_log.json` or restart with an empty log. |

**Consent text for the dashboard**

> This form sends vehicle specifications to a machine-learning model to estimate price. In this lab, the payload is stored locally so we can check data drift. Do not enter personal information. The estimate is not a professional appraisal.

## 5. Transparency and explainability

| Check | Status | Notes |
| --- | --- | --- |
| Model card / API docs | Pass | FastAPI `/docs` plus this file. |
| Local explanation | Pass | `POST /api/v1/explain` returns SHAP contributions. |
| Global explanation | Pass | Mean \|SHAP\| and Random Forest importances on `/api/v1/insights`. |
| Uncertainty communication | Partial | Point estimate only; residual plots on Metrics show spread. No prediction interval in v1. |
| Limitations disclosed | Pass | See section 8. |

## 6. Safety, security, and robustness

| Check | Status | Notes |
| --- | --- | --- |
| Input validation | Pass | Pydantic schema on `/predict` and `/explain`. |
| Unknown categories | Pass | `OneHotEncoder(handle_unknown="ignore")`. |
| Drift monitoring | Pass | Population Stability Index (PSI) on `/api/v1/drift`. Alert if PSI ≥ 0.20. |
| Health check | Pass | `/health` confirms the pickle loaded. |
| Secrets in repo | Pass | No API keys required for local inference. |
| Container isolation | Pass | Experiment 6 Dockerfile runs the API on port 8000. |
| Adversarial / garbage inputs | Partial | Numeric ranges are not strictly clipped; extreme values can produce unrealistic prices. |

## 7. Accountability

| Role | Responsibility |
| --- | --- |
| Student / author | Model training, API, dashboard, this checklist. |
| Course instructor | Academic evaluation only. |
| Future operator | Retrain on current market data, set drift alerts, keep a human appraiser for high-value cars. |

Versioning: model file `models/best_automobile_price_model.pkl` (sklearn `Pipeline` + `RandomForestRegressor`). API version is reported in OpenAPI as `1.1.0`.

## 8. Known limitations

- Training data is decades old. Absolute prices are not 2026 market prices.
- About 200 cars is not enough for stable luxury-make estimates.
- Engineered bins (`weight_category`, `fuel_efficiency_category`, and similar) are heuristic tertile-style cuts, not the original lab notebook cuts if those differed.
- SHAP explains the model, not causal physics.
- CORS is open (`allow_origins=["*"]`) for the student dashboard. Restrict origins before a public production API.

## 9. Sign-off checklist (lab)

- [x] Intended use and prohibited use documented
- [x] No personal data in features or logs
- [x] Fairness caveats for `make` and sparse groups documented
- [x] Consent copy on the dashboard
- [x] SHAP explanations available
- [x] Metrics and drift endpoints available
- [x] Model packaged in Docker
- [ ] Production owner named (not required for this course)

**Statement:** I will not present this model as an unbiased or legally sufficient valuation tool. It is an academic price estimator with public vehicle data, explainability, and drift checks.
