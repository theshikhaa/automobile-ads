from api.routes import router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.prediction_service import prediction_service

app = FastAPI(
    title="Automobile Price Prediction API",
    description="Exp 6–7 FastAPI service for predictions, SHAP explanations, metrics, and drift checks.",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "Automobile Price Prediction API is running",
        "docs": "/docs",
        "health": "/health",
        "predict": "/api/v1/predict",
        "explain": "/api/v1/explain",
        "metrics": "/api/v1/metrics",
        "drift": "/api/v1/drift",
        "insights": "/api/v1/insights",
    }


@app.get("/health")
def health():
    return prediction_service.health()
