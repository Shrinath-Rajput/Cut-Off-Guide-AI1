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


from datetime import datetime

@router.post("/predict-percentile", response_model=PercentilePredictResponse)
async def predict_percentile_endpoint(request: PercentilePredictRequest, db=Depends(get_db)):
    """
    ML-Powered Multi-Exam Percentile Predictor.
    Predicts monotonic percentile, confidence score, rank, performance category,
    and categorized Dream/Likely/Safe college recommendations.
    Supports MHT-CET PCM, MHT-CET PCB, JEE Main, and JEE Advanced.
    """
    try:
        prediction = predict_percentile(
            exam=request.exam,
            marks=request.marks,
            shift=request.shift or "Morning",
            session=request.session or 1,
            difficulty_level=request.difficulty_level or "Medium",
            category=request.category or "General",
            year=request.year or 2026,
        )

        # Async logging to MongoDB predictions collection
        if db is not None:
            try:
                await db["predictions"].insert_one({
                    "user_id": request.user_id or "anonymous",
                    "exam": prediction["exam"],
                    "marks": prediction["marks"],
                    "predicted_percentile": prediction["predicted_percentile"],
                    "predicted_rank": prediction.get("predicted_rank"),
                    "predicted_air": prediction.get("predicted_air"),
                    "confidence": prediction.get("confidence"),
                    "confidence_level": prediction.get("confidence_level"),
                    "performance_category": prediction.get("performance_category"),
                    "shift": request.shift,
                    "session": request.session,
                    "difficulty_level": request.difficulty_level,
                    "timestamp": datetime.utcnow().isoformat(),
                })
            except Exception as db_err:
                print(f"[CutoffsRoute] Warning: MongoDB prediction logging error: {db_err}")

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
