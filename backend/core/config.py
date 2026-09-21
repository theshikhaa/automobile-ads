from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "models" / "best_automobile_price_model.pkl"
DATA_DIR = BASE_DIR / "data"
RAW_DATA_PATH = DATA_DIR / "imports-85.csv"
REFERENCE_DATA_PATH = DATA_DIR / "reference.csv"
PREDICTION_LOG_PATH = DATA_DIR / "prediction_log.json"
METRICS_CACHE_PATH = DATA_DIR / "model_metrics.json"

MAX_LOG_SIZE = 500
SHAP_BACKGROUND_SIZE = 80
PSI_THRESHOLD = 0.2
