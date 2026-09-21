from pydantic import BaseModel


class AutomobileInput(BaseModel):
    symboling: float
    normalized_losses: float
    wheel_base: float
    length: float
    width: float
    height: float
    curb_weight: float
    engine_size: float
    bore: float
    stroke: float
    compression_ratio: float
    horsepower: float
    peak_rpm: float
    city_mpg: float
    highway_mpg: float
    car_volume: float
    power_to_weight_ratio: float
    average_mpg: float
    engine_power_ratio: float
    make: str
    fuel_type: str
    aspiration: str
    num_of_doors: str
    body_style: str
    drive_wheels: str
    engine_location: str
    engine_type: str
    num_of_cylinders: str
    fuel_system: str
    weight_category: str
    fuel_efficiency_category: str
    engine_size_category: str
    horsepower_category: str


class PredictResponse(BaseModel):
    success: bool = True
    predicted_price: float
    currency: str = "USD"


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool = True
    detail: str | None = None
