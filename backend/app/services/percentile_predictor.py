"""
ML Percentile Prediction Service
Provides high-speed monotonic marks-to-percentile prediction,
exam upper bound validation, and rank estimation.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np
import joblib

MODELS_DIR = Path(__file__).resolve().parent.parent / "ml" / "models"

# Exam Configuration Metadata
EXAM_METADATA = {
    "MHT-CET": {
        "max_marks": 200,
        "total_candidates": 420000,
        "rank_label": "State Merit Rank",
        "model_file": "mht_cet_model.joblib",
    },
    "JEE Main": {
        "max_marks": 300,
        "total_candidates": 1400000,
        "rank_label": "All India Rank (AIR)",
        "model_file": "jee_main_model.joblib",
    },
    "JEE Advanced": {
        "max_marks": 360,
        "total_candidates": 185000,
        "rank_label": "JEE Advanced AIR",
        "model_file": "jee_advanced_model.joblib",
    },
}

_MODEL_CACHE: Dict[str, Any] = {}


def normalize_exam_name(raw_name: str) -> str:
    cleaned = (raw_name or "").strip().lower().replace("-", " ").replace("_", " ")
    if "mht" in cleaned or "cet" in cleaned:
        return "MHT-CET"
    if "adv" in cleaned:
        return "JEE Advanced"
    if "jee" in cleaned:
        return "JEE Main"
    return raw_name.strip()


def get_exam_max_marks(exam_name: str) -> int:
    canonical = normalize_exam_name(exam_name)
    cfg = EXAM_METADATA.get(canonical)
    if not cfg:
        raise ValueError(f"Unsupported exam: '{exam_name}'. Supported exams: MHT-CET, JEE Main, JEE Advanced")
    return cfg["max_marks"]


def _load_model(canonical_exam: str):
    if canonical_exam in _MODEL_CACHE:
        return _MODEL_CACHE[canonical_exam]

    cfg = EXAM_METADATA.get(canonical_exam)
    if not cfg:
        return None

    model_path = MODELS_DIR / cfg["model_file"]
    if model_path.exists():
        try:
            package = joblib.load(model_path)
            model = package.get("model") if isinstance(package, dict) else package
            _MODEL_CACHE[canonical_exam] = model
            return model
        except Exception as e:
            print(f"[PercentilePredictor] Error loading {model_path}: {e}")

    return None


def _fallback_percentile(marks: float, max_marks: int) -> float:
    ratio = max(0.0, min(1.0, marks / max_marks))
    # Standard non-linear logistic-style curve matching exam distribution
    raw = 100.0 / (1.0 + np.exp(-7.5 * (ratio - 0.45)))
    # Anchor zero marks to 0.0 and max marks to 100.0
    zero_val = 100.0 / (1.0 + np.exp(-7.5 * (-0.45)))
    max_val = 100.0 / (1.0 + np.exp(-7.5 * (1.0 - 0.45)))
    scaled = (raw - zero_val) / (max_val - zero_val) * 100.0
    return float(np.clip(scaled, 0.0, 100.0))


def _calculate_performance_tier(percentile: float) -> str:
    if percentile >= 99.5:
        return "Elite Tier 1 (Top 0.5% - Dream Institutes)"
    if percentile >= 98.0:
        return "Top 2% - Premium Autonomous Institutes"
    if percentile >= 95.0:
        return "Top 5% - Highly Competitive Institutes"
    if percentile >= 90.0:
        return "Top 10% - Reputed State Engineering Colleges"
    if percentile >= 80.0:
        return "Top 20% - Established University Affiliated Colleges"
    if percentile >= 65.0:
        return "Above Average - Regional Engineering Colleges"
    if percentile >= 30.0:
        return "Foundation Tier - Affiliated & Private Colleges"
    return "Below 30%ile - Search for Private Colleges & Management Quota"


def predict_percentile(exam: str, marks: float) -> Dict[str, Any]:
    canonical_exam = normalize_exam_name(exam)
    if canonical_exam not in EXAM_METADATA:
        raise ValueError(
            f"Unsupported exam: '{exam}'. Choose from: MHT-CET, JEE Main, JEE Advanced"
        )

    cfg = EXAM_METADATA[canonical_exam]
    max_marks = cfg["max_marks"]

    # Strict boundary enforcement
    if marks < 0:
        raise ValueError("Marks cannot be negative.")
    if marks > max_marks:
        raise ValueError(
            f"Marks ({marks}) exceed maximum allowed marks ({max_marks}) for {canonical_exam}. "
            f"Please enter marks between 0 and {max_marks}."
        )

    # ML Inference
    model = _load_model(canonical_exam)
    if model is not None:
        try:
            preds = model.predict([marks])
            predicted_percentile = float(preds[0])
        except Exception as err:
            print(f"[PercentilePredictor] Inference fallback triggered: {err}")
            predicted_percentile = _fallback_percentile(marks, max_marks)
    else:
        predicted_percentile = _fallback_percentile(marks, max_marks)

    predicted_percentile = float(np.clip(predicted_percentile, 0.0, 100.0))
    rounded_percentile = round(predicted_percentile, 2)

    # Confidence Range (±0.35% realistic shift variance)
    range_min = max(0.0, round(predicted_percentile - 0.35, 2))
    range_max = min(100.0, round(predicted_percentile + 0.35, 2))
    percentile_range = f"{range_min:.2f}% – {range_max:.2f}%"

    # Estimated Rank
    total_candidates = cfg["total_candidates"]
    rank_fraction = max(0.00001, (100.0 - predicted_percentile) / 100.0)
    estimated_rank_num = max(1, int(round(rank_fraction * total_candidates)))
    estimated_rank = f"{cfg['rank_label']} ~{estimated_rank_num:,}"

    # Performance Tier
    tier = _calculate_performance_tier(predicted_percentile)

    # Advisory for less than 30 percentile
    advisory_message = None
    if predicted_percentile < 30.0:
        advisory_message = (
            "Your score is below 30 percentile, which is too low to apply for merit-based seats in government "
            "or top autonomous colleges through CAP rounds. Please search for private colleges, deemed universities, "
            "and institute-level / management quota seats to apply."
        )

    return {
        "exam": canonical_exam,
        "marks": round(marks, 2),
        "max_marks": max_marks,
        "predicted_percentile": rounded_percentile,
        "predicted_percentile_precise": round(predicted_percentile, 4),
        "percentile_range": percentile_range,
        "estimated_rank": estimated_rank,
        "estimated_rank_num": estimated_rank_num,
        "performance_tier": tier,
        "advisory_message": advisory_message,
    }
