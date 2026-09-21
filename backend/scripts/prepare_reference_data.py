"""Build engineered reference.csv from the UCI Automobile dataset."""

from pathlib import Path
import sys
import urllib.request

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.config import DATA_DIR, RAW_DATA_PATH, REFERENCE_DATA_PATH
from services.feature_engineering import prepare_raw_dataframe

SOURCE_URL = "https://raw.githubusercontent.com/plotly/datasets/master/imports-85.csv"


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not RAW_DATA_PATH.exists():
        urllib.request.urlretrieve(SOURCE_URL, RAW_DATA_PATH)

    raw = pd.read_csv(RAW_DATA_PATH, na_values=["?", "NA"])
    prepared = prepare_raw_dataframe(raw)
    prepared = prepared.dropna(subset=["price", "horsepower", "bore", "stroke", "num_of_doors"])
    prepared["normalized_losses"] = prepared["normalized_losses"].fillna(
        prepared["normalized_losses"].median()
    )
    prepared.to_csv(REFERENCE_DATA_PATH, index=False)
    print(f"Wrote {len(prepared)} rows to {REFERENCE_DATA_PATH}")


if __name__ == "__main__":
    main()
