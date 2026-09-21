import numpy as np
import pandas as pd

CYLINDER_MAP = {
    "2": "two",
    "3": "three",
    "4": "four",
    "5": "five",
    "6": "six",
    "8": "eight",
    "12": "twelve",
    "two": "two",
    "three": "three",
    "four": "four",
    "five": "five",
    "six": "six",
    "eight": "eight",
    "twelve": "twelve",
}

COLUMN_MAP = {
    "normalized-losses": "normalized_losses",
    "fuel-type": "fuel_type",
    "num-of-doors": "num_of_doors",
    "body-style": "body_style",
    "drive-wheels": "drive_wheels",
    "engine-location": "engine_location",
    "wheel-base": "wheel_base",
    "curb-weight": "curb_weight",
    "engine-type": "engine_type",
    "num-of-cylinders": "num_of_cylinders",
    "engine-size": "engine_size",
    "fuel-system": "fuel_system",
    "compression-ratio": "compression_ratio",
    "peak-rpm": "peak_rpm",
    "city-mpg": "city_mpg",
    "highway-mpg": "highway_mpg",
}


def _to_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.replace("?", np.nan).replace("NA", np.nan), errors="coerce")


def weight_category(value: float) -> str:
    if value < 2200:
        return "Light"
    if value < 2800:
        return "Medium"
    return "Heavy"


def fuel_efficiency_category(value: float) -> str:
    if value >= 30:
        return "High Efficiency"
    if value >= 22:
        return "Medium Efficiency"
    return "Low Efficiency"


def engine_size_category(value: float) -> str:
    if value < 100:
        return "Small Engine"
    if value < 150:
        return "Medium Engine"
    return "Large Engine"


def horsepower_category(value: float) -> str:
    if value < 80:
        return "Low Power"
    if value < 120:
        return "Medium Power"
    return "High Power"


def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["car_volume"] = out["length"] * out["width"] * out["height"]
    out["power_to_weight_ratio"] = out["horsepower"] / out["curb_weight"]
    out["average_mpg"] = (out["city_mpg"] + out["highway_mpg"]) / 2
    out["engine_power_ratio"] = out["horsepower"] / out["engine_size"]
    out["weight_category"] = out["curb_weight"].apply(weight_category)
    out["fuel_efficiency_category"] = out["average_mpg"].apply(fuel_efficiency_category)
    out["engine_size_category"] = out["engine_size"].apply(engine_size_category)
    out["horsepower_category"] = out["horsepower"].apply(horsepower_category)
    return out


def prepare_raw_dataframe(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.rename(columns=COLUMN_MAP).copy()
    numeric_cols = [
        "symboling",
        "normalized_losses",
        "wheel_base",
        "length",
        "width",
        "height",
        "curb_weight",
        "engine_size",
        "bore",
        "stroke",
        "compression_ratio",
        "horsepower",
        "peak_rpm",
        "city_mpg",
        "highway_mpg",
    ]
    if "price" in df.columns:
        numeric_cols = numeric_cols + ["price"]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = _to_numeric(df[col])

    if "make" in df.columns:
        df["make"] = df["make"].replace({"peugeot": "peugot"})

    if "num_of_cylinders" in df.columns:
        df["num_of_cylinders"] = (
            df["num_of_cylinders"].astype(str).str.strip().str.lower().map(CYLINDER_MAP)
        )

    for col in ["num_of_doors", "fuel_type", "aspiration", "body_style", "drive_wheels"]:
        if col in df.columns:
            df[col] = df[col].replace("?", np.nan)

    df = add_engineered_features(df)
    return df
