import pandas as pd
from services.feature_engineering import add_engineered_features


def test_feature_engineering():
    df = pd.DataFrame(
        {
            "length": [170.0],
            "width": [65.0],
            "height": [54.0],
            "horsepower": [100.0],
            "curb_weight": [2500.0],
            "city_mpg": [25.0],
            "highway_mpg": [30.0],
            "engine_size": [120.0],
        }
    )

    result = add_engineered_features(df)

    assert "car_volume" in result.columns
    assert "power_to_weight_ratio" in result.columns
    assert "average_mpg" in result.columns
    assert "engine_power_ratio" in result.columns

    assert result["average_mpg"].iloc[0] == 27.5