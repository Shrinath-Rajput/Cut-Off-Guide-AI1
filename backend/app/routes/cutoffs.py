from fastapi import APIRouter, Depends, HTTPException, status
from app.core.database import get_db
from app.schemas.cutoff import (
    CutoffSearchRequest,
    CutoffResult,
    PercentilePredictRequest,
    PercentilePredictResponse,
    CollegePredictLLMRequest,
    CollegePredictLLMResponse,
)
from app.services.cutoff_service import search_cutoffs, predict_colleges_with_llm
from app.services.percentile_predictor import predict_percentile

router = APIRouter(prefix="/api/cutoffs", tags=["Cutoffs"])


@router.post("/search", response_model=CutoffResult)
async def search_cutoffs_endpoint(request: CutoffSearchRequest, db=Depends(get_db)):
    result = await search_cutoffs(db, request)
    return result


@router.post("/predict-percentile", response_model=PercentilePredictResponse)
async def predict_percentile_endpoint(request: PercentilePredictRequest):
    """
    ML-Powered Percentile Predictor.
    Predicts monotonic percentile, confidence interval, and estimated rank
    for MHT-CET (max 200), JEE Main (max 300), or JEE Advanced (max 360).
    """
    try:
        prediction = predict_percentile(exam=request.exam, marks=request.marks)
        return PercentilePredictResponse(**prediction)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Percentile prediction failed: {exc}",
        )


@router.post("/predict-colleges-llm", response_model=CollegePredictLLMResponse)
async def predict_colleges_llm_endpoint(
    request: CollegePredictLLMRequest,
    db=Depends(get_db),
):
    """
    LLM-Powered College Recommendation Engine.
    Categorizes institutions into Safe, Target, and Ambitious tiers
    based on predicted percentile, category, preferred location, CAP round, and courses.
    """
    try:
        result = await predict_colleges_with_llm(db, request)
        return result
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"College prediction failed: {exc}",
        )
