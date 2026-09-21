from fastapi import APIRouter, HTTPException
from schemas.automobile import AutomobileInput
from services.prediction_service import prediction_service

router = APIRouter(prefix="/api/v1", tags=["Automobile Price"])


@router.post("/predict")
def predict_price(data: AutomobileInput):
    try:
        payload = prediction_service.enrich_payload(data.model_dump())
        prediction = prediction_service.predict(payload)
        return {
            "success": True,
            "predicted_price": round(prediction, 2),
            "currency": "USD",
            "input": payload,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/explain")
def explain_price(data: AutomobileInput):
    try:
        payload = prediction_service.enrich_payload(data.model_dump())
        return prediction_service.explain(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/metrics")
def model_metrics():
    return prediction_service.metrics


@router.get("/drift")
def drift_checks():
    return prediction_service.drift_report()


@router.get("/insights")
def model_insights():
    return prediction_service.insights()


@router.get("/schema")
def feature_schema():
    return prediction_service.schema()


@router.get("/sample")
def sample_request():
    return prediction_service.sample_payload()


@router.get("/health")
def api_health():
    return prediction_service.health()
