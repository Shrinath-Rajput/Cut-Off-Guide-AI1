from fastapi import APIRouter, Depends
from typing import Union
from app.core.database import get_db
from app.schemas.prediction import PredictionRequest, PredictionResponse, InsufficientDataResponse
from app.services.prediction_service import get_cutoff_prediction

router = APIRouter(prefix="/api/prediction", tags=["Prediction"])

@router.post("/", response_model=Union[PredictionResponse, InsufficientDataResponse])
async def create_prediction(request: PredictionRequest, db = Depends(get_db)):
    result = await get_cutoff_prediction(db, request)
    return result
