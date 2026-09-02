from datetime import datetime
from pathlib import Path

import joblib
import pandas as pd

from app.schemas.cutoff import CutoffSearchRequest, CutoffResult

ROOT = Path(__file__).resolve().parents[3]
MODEL_PATH = ROOT / "ml" / "models" / "cutoff_model.pkl"
PREPROCESSOR_PATH = ROOT / "ml" / "models" / "preprocessor.pkl"


def _normalize_text(value, default="Unknown"):
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _normalize_exam_name(value):
    text = _normalize_text(value, "Unknown")
    normalized = text.strip()
    upper = normalized.upper()

    if upper in {"JEE MAIN", "JEE-MAIN", "JEE MAIN 2025"}:
        return "JEE Main"
    if upper in {"JEE ADVANCED", "JEE-ADVANCED"}:
        return "JEE Advanced"
    if upper in {"MHT-CET", "MHT CET", "MH CET"}:
        return "MHT-CET"
    if upper in {"B.PHARM CET", "B PHARM CET", "BPHARM CET", "B-PHARM"}:
        return "B.Pharm CET"
    if upper in {"D.PHARM CET", "D PHARM CET", "DPHARM CET", "D-PHARM"}:
        return "D.Pharm CET"
    return normalized


def _normalize_course_name(value):
    text = _normalize_text(value, "Unknown")
    normalized = text.strip()
    lower = normalized.lower().replace("&", " and ")

    if lower in {"cse", "computer science and engineering", "computer science engineering"}:
        return "Computer Science and Engineering"
    if lower in {"it", "information technology"}:
        return "Information Technology"
    if lower in {"ece", "electronics and telecommunication", "electronics and telecommunication engg", "electronics and telecom"}:
        return "Electronics and Telecommunication Engg"
    if lower in {"mechanical", "mechanical engineering"}:
        return "Mechanical Engineering"
    if lower in {"civil", "civil engineering"}:
        return "Civil Engineering"
    if lower in {"electrical", "electrical engineering"}:
        return "Electrical Engineering"
    if lower in {"chemical", "chemical engineering"}:
        return "Chemical Engineering"
    if lower in {"ai/ml", "ai ml", "artificial intelligence and machine learning", "artificial intelligence and data science", "aids"}:
        return "Artificial Intelligence and Machine Learning"
    if lower in {"data science", "ds"}:
        return "Artificial Intelligence and Data Science"
    if lower in {"b pharm", "b.pharm", "pharmacy"}:
        return "Pharmacy"
    if lower in {"mbbs", "bds", "bams", "bhms"}:
        return "MBBS"
    return normalized


def _normalize_category(value):
    text = _normalize_text(value, "Unknown")
    normalized = text.strip()
    upper = normalized.upper().replace(" ", "")

    aliases = {
        "OPEN": "GOPENH",
        "OPEN/GENERAL": "GOPENH",
        "GENERAL": "GOPENH",
        "OBC": "GOBCH",
        "OBC": "GOBCH",
        "SC": "GSCH",
        "ST": "GSTH",
        "EWS": "EWS",
        "PWD": "PWDOPENH",
        "PWDOPEN": "PWDOPENH",
        "MINORITY": "LOPENH",
        "DEFENCE": "DEFOPENS",
        "DEFENCE/EX-SERVICEMEN": "DEFOPENS",
        "NT-B": "GNT1H",
        "NTC": "GNT2H",
        "NTD": "GNT3H",
        "SBC": "GOBCH",
        "KASHMIRIMIGRANT": "GOPENH",
    }
    return aliases.get(upper, normalized)


def _normalize_seat_type(university, location):
    university_text = _normalize_text(university, "")
    location_text = _normalize_text(location, "")
    if not university_text and not location_text:
        return "Home University"

    combined = f"{university_text} {location_text}".lower()
    if "other" in combined or "outside" in combined:
        return "Other Than Home University"
    if "home university" in combined or "university" in combined or "pune" in combined or "mumbai" in combined:
        return "Home University"
    return "State Level"


def _normalize_status(value):
    text = _normalize_text(value, "Un-Aided")
    normalized = text.strip()
    lower = normalized.lower()
    if lower in {"government", "government aided", "government-aided"}:
        return "Government"
    if lower in {"un-aided", "private", "un aided"}:
        return "Un-Aided"
    if "autonomous" in lower:
        return "Un-Aided Autonomous"
    if "department" in lower:
        return "University Department"
    return "Un-Aided"


def _parse_round(value):
    if value is None:
        return 1
    if isinstance(value, (int, float)):
        return int(value)
    text = str(value).strip().upper().replace("ROUND", "").replace(" ", "")
    digits = "".join(ch for ch in text if ch.isdigit())
    if digits:
        return int(digits)
    return 1


def _coerce_float(value, default=0.0):
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _build_model_input(request: CutoffSearchRequest) -> pd.DataFrame:
    if request is None:
        raise ValueError("Prediction request is required.")

    status_source = request.gender or request.university or request.location or "Un-Aided"

    feature_df = pd.DataFrame([{
        "exam": _normalize_exam_name(request.exam),
        "course_name": _normalize_course_name(request.course),
        "category": _normalize_category(request.category),
        "seat_type": _normalize_seat_type(request.university, request.location),
        "status": _normalize_status(status_source),
        "cap_round": _parse_round(request.round),
        "year": datetime.now().year,
    }])
    return feature_df[["exam", "course_name", "category", "seat_type", "status", "cap_round", "year"]]


def _load_ml_artifacts():
    if not MODEL_PATH.exists() or not PREPROCESSOR_PATH.exists():
        raise FileNotFoundError(f"ML model artifacts not found: {MODEL_PATH} and {PREPROCESSOR_PATH}")

    model = joblib.load(MODEL_PATH)
    preprocessor = joblib.load(PREPROCESSOR_PATH)
    return model, preprocessor


def _predict_percentile(request: CutoffSearchRequest) -> float:
    model, preprocessor = _load_ml_artifacts()
    feature_df = _build_model_input(request)
    feature_columns = ["exam", "course_name", "category", "seat_type", "status", "cap_round", "year"]
    X = feature_df[feature_columns]

    if hasattr(model, "named_steps"):
        estimator = model.named_steps.get("model")
        if estimator is not None:
            transformed = preprocessor.transform(X)
            pred = estimator.predict(transformed)
        else:
            pred = model.predict(X)
    else:
        transformed = preprocessor.transform(X)
        pred = model.predict(transformed)

    percentile = float(pred[0])
    if percentile < 0:
        percentile = 0.0
    if percentile > 100:
        percentile = 100.0
    return percentile


async def search_cutoffs(db, search_request: CutoffSearchRequest) -> CutoffResult:
    try:
        percentile = _predict_percentile(search_request)
    except Exception as exc:
        raise ValueError(f"ML prediction failed: {exc}") from exc

    rank_est = int(max(1, (100 - percentile) * 1200))
    course_name = _normalize_text(search_request.course, "selected course")
    suggestion = (
        f"Model estimate for {course_name}: "
        f"historical cutoff band around {percentile:.2f}%ile"
    )

    return CutoffResult(
        cutoff=f"{percentile:.2f}%ile",
        rank=f"AIR ~{rank_est:,}",
        suggestion=suggestion,
    )
