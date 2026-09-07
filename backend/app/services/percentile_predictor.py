"""
CutoffGrid Multi-Exam ML Percentile & Rank Prediction Service
Supports MHT-CET PCM, MHT-CET PCB, JEE Main, and JEE Advanced.
Calculates high-precision predicted percentile, confidence scores,
performance categories, merit ranks/AIR, and categorized college recommendations.
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
import numpy as np
import pandas as pd
from scipy.interpolate import PchipInterpolator
import joblib

MODELS_DIR = Path(__file__).resolve().parent.parent / "ml" / "models"

# Supported Canonical Exam Types
EXAM_METADATA = {
    "MHT-CET PCM": {
        "canonical": "MHT-CET PCM",
        "aliases": ["mht-cet pcm", "mht cet pcm", "mht-cet", "mht cet", "cet pcm", "pcm"],
        "max_marks": 200,
        "base_candidates": 420000,
        "rank_label": "State Merit Rank",
        "rank_key": "predicted_rank",
        "model_file": "mht_cet_pcm_model.joblib",
    },
    "MHT-CET PCB": {
        "canonical": "MHT-CET PCB",
        "aliases": ["mht-cet pcb", "mht cet pcb", "cet pcb", "pcb"],
        "max_marks": 200,
        "base_candidates": 330000,
        "rank_label": "State Merit Rank",
        "rank_key": "predicted_rank",
        "model_file": "mht_cet_pcb_model.joblib",
    },
    "JEE Main": {
        "canonical": "JEE Main",
        "aliases": ["jee main", "jee-main", "jee", "jee mains", "mains"],
        "max_marks": 300,
        "base_candidates": 1400000,
        "rank_label": "All India Rank (AIR / CRL)",
        "rank_key": "predicted_rank",
        "model_file": "jee_main_model.joblib",
    },
    "JEE Advanced": {
        "canonical": "JEE Advanced",
        "aliases": ["jee advanced", "jee-advanced", "jee adv", "adv", "advanced"],
        "max_marks": 360,
        "base_candidates": 185000,
        "rank_label": "JEE Advanced AIR",
        "rank_key": "predicted_air",
        "model_file": "jee_advanced_model.joblib",
    },
}

_MODEL_CACHE: Dict[str, Any] = {}
_INTERPOLATOR_CACHE: Dict[str, Any] = {}

DIFFICULTY_MAP = {"Easy": 1.0, "Medium": 2.0, "Hard": 3.0, "Very Hard": 3.5}
SHIFT_MAP = {"Morning": 1.0, "Afternoon": 2.0, "Paper 1 + Paper 2": 1.5}


def normalize_exam_name(raw_name: str) -> str:
    cleaned = (raw_name or "").strip().lower()
    for canonical, meta in EXAM_METADATA.items():
        if cleaned == canonical.lower():
            return canonical
        for alias in meta["aliases"]:
            if alias in cleaned:
                return canonical
    return "MHT-CET PCM"


def _load_model_package(canonical_exam: str) -> Optional[Dict[str, Any]]:
    if canonical_exam in _MODEL_CACHE:
        return _MODEL_CACHE[canonical_exam]

    meta = EXAM_METADATA.get(canonical_exam)
    if not meta:
        return None

    model_path = MODELS_DIR / meta["model_file"]
    if model_path.exists():
        try:
            package = joblib.load(model_path)
            _MODEL_CACHE[canonical_exam] = package
            return package
        except Exception as e:
            print(f"[PercentilePredictor] Error loading model package {model_path}: {e}")

    return None


def _get_anchor_interpolator(canonical_exam: str, package: Optional[Dict[str, Any]] = None):
    if canonical_exam in _INTERPOLATOR_CACHE:
        return _INTERPOLATOR_CACHE[canonical_exam]

    anchors = None
    if package and "metadata" in package:
        meta_dict = package["metadata"]
        if "yearly_anchors" in meta_dict and meta_dict["yearly_anchors"]:
            latest_year = max(meta_dict["yearly_anchors"].keys())
            anchors = meta_dict["yearly_anchors"][latest_year]
        elif "anchors" in meta_dict:
            anchors = meta_dict["anchors"]

    if not anchors:
        meta = EXAM_METADATA.get(canonical_exam, EXAM_METADATA["MHT-CET PCM"])
        max_m = meta["max_marks"]
        anchors = [(0, 0.0), (max_m * 0.25, 25.0), (max_m * 0.5, 75.0), (max_m * 0.75, 96.0), (max_m, 100.0)]

    # Sort anchors ascending by marks
    anchors = sorted(anchors, key=lambda x: x[0])
    marks = np.array([a[0] for a in anchors], dtype=float)
    pcts = np.array([a[1] for a in anchors], dtype=float)
    interpolator = PchipInterpolator(marks, pcts)
    _INTERPOLATOR_CACHE[canonical_exam] = interpolator
    return interpolator


def calculate_performance_category(percentile: float) -> str:
    """
    Categorizes the student into the 6 standard performance tiers:
    - Outstanding (99+ Percentile)
    - Excellent (95–99 Percentile)
    - Very Good (85–95 Percentile)
    - Good (70–85 Percentile)
    - Average (50–70 Percentile)
    - Needs Improvement (Below 50 Percentile)
    """
    if percentile >= 99.0:
        return "Outstanding"
    if percentile >= 95.0:
        return "Excellent"
    if percentile >= 85.0:
        return "Very Good"
    if percentile >= 70.0:
        return "Good"
    if percentile >= 50.0:
        return "Average"
    return "Needs Improvement"


def calculate_confidence_score(
    marks: float,
    max_marks: int,
    difficulty: str,
    shift: str,
    mae: float = 0.035,
) -> Dict[str, Any]:
    """
    Multi-factor Confidence Score System:
    1. Prediction Stability: High in middle and top marks regions where candidate density is dense.
    2. Dataset Similarity: Distance from boundary extremities (0 or max).
    3. Historical Variance: Impact of shift and difficulty variations.
    4. Model Confidence: Calibrated MAE validation accuracy.
    """
    normalized = marks / max(1.0, max_marks)

    # Base confidence: 98.5%
    base_confidence = 98.5

    # Density & distribution stability penalty (slightly lower at extreme boundaries)
    if normalized < 0.05 or normalized > 0.98:
        stability_penalty = 2.2
    elif normalized < 0.15 or normalized > 0.92:
        stability_penalty = 1.2
    else:
        stability_penalty = 0.4

    # Difficulty variance impact
    diff_penalty = 0.8 if difficulty in ["Hard", "Very Hard"] else 0.4

    # Shift variance impact
    shift_penalty = 0.3 if shift in ["Afternoon", "Paper 1 + Paper 2"] else 0.2

    # MAE penalty
    mae_penalty = min(2.0, mae * 10.0)

    calculated = base_confidence - (stability_penalty + diff_penalty + shift_penalty + mae_penalty)
    confidence = float(np.clip(round(calculated, 1), 80.0, 99.4))

    if confidence >= 95.0:
        confidence_level = "High Confidence"
    elif confidence >= 88.0:
        confidence_level = "Medium Confidence"
    else:
        confidence_level = "Low Confidence"

    return {
        "confidence": confidence,
        "confidence_level": confidence_level,
    }


def get_recommended_colleges_for_percentile(
    exam: str,
    percentile: float,
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Provides curated Dream, Likely, and Safe college recommendations
    tailored to the student's predicted percentile and entrance exam.
    """
    is_jee = "JEE" in exam

    if is_jee:
        # JEE Main / Advanced College Tiers
        if percentile >= 99.0:
            dream = [
                {"name": "NIT Trichy", "branch": "Computer Science & Engineering", "cutoff": 99.85, "chance": "25%"},
                {"name": "NIT Surathkal", "branch": "Information Technology", "cutoff": 99.70, "chance": "38%"},
                {"name": "IIT Bombay (if Adv)", "branch": "Electrical Engineering", "cutoff": 99.65, "chance": "42%"},
            ]
            likely = [
                {"name": "VNIT Nagpur", "branch": "Computer Science & Engineering", "cutoff": 99.20, "chance": "74%"},
                {"name": "NIT Warangal", "branch": "Electronics & Communication", "cutoff": 99.30, "chance": "68%"},
                {"name": "IIIT Allahabad", "branch": "Information Technology", "cutoff": 99.15, "chance": "78%"},
            ]
            safe = [
                {"name": "IIIT Nagpur", "branch": "Artificial Intelligence & Data Science", "cutoff": 98.40, "chance": "92%"},
                {"name": "NIT Rourkela", "branch": "Electrical Engineering", "cutoff": 98.60, "chance": "89%"},
                {"name": "IIIT Pune", "branch": "Computer Science & Engineering", "cutoff": 98.20, "chance": "94%"},
            ]
        elif percentile >= 95.0:
            dream = [
                {"name": "VNIT Nagpur", "branch": "Computer Science & Engineering", "cutoff": 99.20, "chance": "30%"},
                {"name": "IIIT Pune", "branch": "Computer Science & Engineering", "cutoff": 98.20, "chance": "45%"},
            ]
            likely = [
                {"name": "IIIT Nagpur", "branch": "Computer Science & Engineering", "cutoff": 96.80, "chance": "72%"},
                {"name": "NIT Raipur", "branch": "Information Technology", "cutoff": 96.50, "chance": "76%"},
            ]
            safe = [
                {"name": "IIIT Bhagalpur", "branch": "CSE / AI", "cutoff": 94.20, "chance": "90%"},
                {"name": "NIT Silchar", "branch": "Electrical Engineering", "cutoff": 94.80, "chance": "88%"},
            ]
        elif percentile >= 85.0:
            dream = [
                {"name": "IIIT Nagpur", "branch": "Electronics & Telecommunication", "cutoff": 94.50, "chance": "35%"},
            ]
            likely = [
                {"name": "GFTIs (Assam Univ, Tezpur Univ)", "branch": "Computer Science", "cutoff": 88.50, "chance": "70%"},
            ]
            safe = [
                {"name": "Top State Autonomous (All India Quota)", "branch": "Electronics & Telecomm", "cutoff": 82.0, "chance": "92%"},
            ]
        else:
            dream = [{"name": "State Reputed Autonomous (All India)", "branch": "Core Engineering", "cutoff": 78.0, "chance": "40%"}]
            likely = [{"name": "Private Tier-2 Engineering", "branch": "Computer Science & IT", "cutoff": 68.0, "chance": "75%"}]
            safe = [{"name": "Private / Deemed University", "branch": "Engineering Branches", "cutoff": 50.0, "chance": "95%"}]
    else:
        # MHT-CET PCM & PCB College Tiers (Maharashtra)
        if percentile >= 99.0:
            dream = [
                {"name": "COEP Technological University, Pune", "branch": "Computer Engineering", "cutoff": 99.88, "chance": "28%"},
                {"name": "VJTI, Mumbai", "branch": "Computer Engineering", "cutoff": 99.82, "chance": "35%"},
                {"name": "SPIT, Mumbai", "branch": "Computer Science & Engineering", "cutoff": 99.55, "chance": "44%"},
            ]
            likely = [
                {"name": "PICT, Pune", "branch": "Computer Engineering", "cutoff": 99.30, "chance": "72%"},
                {"name": "COEP Pune", "branch": "Artificial Intelligence & Robotics", "cutoff": 99.35, "chance": "68%"},
                {"name": "VIT Pune", "branch": "Artificial Intelligence & Data Science", "cutoff": 98.90, "chance": "82%"},
            ]
            safe = [
                {"name": "PCCOE, Pune", "branch": "Computer Engineering", "cutoff": 98.40, "chance": "92%"},
                {"name": "Walchand College of Engineering, Sangli", "branch": "Information Technology", "cutoff": 98.10, "chance": "90%"},
                {"name": "VIIT Pune", "branch": "Computer Engineering", "cutoff": 97.90, "chance": "95%"},
            ]
        elif percentile >= 95.0:
            dream = [
                {"name": "PICT, Pune", "branch": "Computer Engineering", "cutoff": 99.30, "chance": "32%"},
                {"name": "VIT Pune", "branch": "Computer Engineering", "cutoff": 98.85, "chance": "42%"},
            ]
            likely = [
                {"name": "PCCOE, Pune", "branch": "Artificial Intelligence & ML", "cutoff": 97.20, "chance": "74%"},
                {"name": "D.J. Sanghvi College of Engg, Mumbai", "branch": "Information Technology", "cutoff": 96.90, "chance": "70%"},
                {"name": "Government College of Engg, Aurangabad", "branch": "Computer Science", "cutoff": 96.20, "chance": "78%"},
            ]
            safe = [
                {"name": "MIT Academy of Engineering, Alandi", "branch": "Computer Engineering", "cutoff": 94.10, "chance": "92%"},
                {"name": "Thadomal Shahani Engg College, Mumbai", "branch": "Artificial Intelligence", "cutoff": 94.50, "chance": "89%"},
                {"name": "AISSMS COE, Pune", "branch": "Computer Engineering", "cutoff": 93.80, "chance": "94%"},
            ]
        elif percentile >= 85.0:
            dream = [
                {"name": "PCCOE, Pune", "branch": "Electronics & Telecomm", "cutoff": 92.50, "chance": "35%"},
                {"name": "VIT Pune", "branch": "Mechanical Engineering", "cutoff": 91.20, "chance": "45%"},
            ]
            likely = [
                {"name": "Sinhgad College of Engineering, Pune", "branch": "Computer Engineering", "cutoff": 88.60, "chance": "75%"},
                {"name": "DY Patil College of Engineering, Akurdi", "branch": "Artificial Intelligence & DS", "cutoff": 87.80, "chance": "72%"},
            ]
            safe = [
                {"name": "JSPM Imperial College, Pune", "branch": "Computer Engineering", "cutoff": 82.40, "chance": "92%"},
                {"name": "Modern Education Society's COE, Pune", "branch": "Information Technology", "cutoff": 83.10, "chance": "90%"},
            ]
        elif percentile >= 70.0:
            dream = [{"name": "Sinhgad COE, Pune", "branch": "Information Technology", "cutoff": 84.0, "chance": "35%"}]
            likely = [{"name": "DY Patil Institute of Tech, Pimpri", "branch": "E&TC Engineering", "cutoff": 74.5, "chance": "74%"}]
            safe = [{"name": "Zeal College of Engineering, Pune", "branch": "Computer Engineering", "cutoff": 68.2, "chance": "91%"}]
        elif percentile >= 50.0:
            dream = [{"name": "Regional University Affiliated Colleges", "branch": "Core / IT Branches", "cutoff": 65.0, "chance": "40%"}]
            likely = [{"name": "Emerging Autonomous Institutes", "branch": "Mechanical / Civil / Electrical", "cutoff": 54.0, "chance": "75%"}]
            safe = [{"name": "Private Engineering Colleges", "branch": "All Engineering Streams", "cutoff": 45.0, "chance": "95%"}]
        else:
            dream = [{"name": "Private Autonomous Institutes", "branch": "Core Engineering Streams", "cutoff": 48.0, "chance": "35%"}]
            likely = [{"name": "Private Engineering Colleges", "branch": "Available Branches", "cutoff": 35.0, "chance": "75%"}]
            safe = [{"name": "Deemed / Private Universities & Management Seats", "branch": "Engineering & Technology", "cutoff": 20.0, "chance": "98%"}]

    return {
        "dream": dream,
        "likely": likely,
        "safe": safe,
    }


def predict_percentile(
    exam: str,
    marks: float,
    shift: str = "Morning",
    session: int = 1,
    difficulty_level: str = "Medium",
    category: str = "General",
    year: int = 2026,
) -> Dict[str, Any]:
    """
    Main Multi-Exam Percentile Prediction Engine.
    Executes ML inference, rank calculation, confidence estimation,
    performance tier assignment, and college recommendations.
    """
    canonical_exam = normalize_exam_name(exam)
    meta = EXAM_METADATA.get(canonical_exam, EXAM_METADATA["MHT-CET PCM"])
    max_marks = meta["max_marks"]

    # Boundary verification
    if marks < 0:
        raise ValueError("Marks cannot be negative.")
    if marks > max_marks:
        raise ValueError(
            f"Marks ({marks}) exceed maximum allowed marks ({max_marks}) for {canonical_exam}. "
            f"Please enter marks between 0 and {max_marks}."
        )

    package = _load_model_package(canonical_exam)
    interpolator = _get_anchor_interpolator(canonical_exam, package)

    # Feature Engineering
    m_clamped = float(np.clip(marks, 0.0, max_marks))
    normalized_marks = round(m_clamped / max_marks, 4)
    base_historical_pct = float(interpolator(m_clamped))

    diff_numeric = DIFFICULTY_MAP.get(difficulty_level, 2.0)
    shift_numeric = SHIFT_MAP.get(shift, 1.0)
    historical_std = 0.25
    yearly_growth = 1.0 + 0.03 * (year - 2018)

    # Run ML Model Inference
    predicted_percentile = None
    mae = 0.14

    if package and "model" in package:
        try:
            model = package["model"]
            mae = package.get("metrics", {}).get("mae", 0.14)
            cols = package.get("feature_cols", [
                "marks",
                "normalized_marks",
                "historical_avg_percentile",
                "difficulty_numeric",
                "shift_numeric",
                "year",
            ])

            row_data = {
                "marks": m_clamped,
                "normalized_marks": normalized_marks,
                "historical_avg_percentile": base_historical_pct,
                "difficulty_numeric": diff_numeric,
                "shift_numeric": shift_numeric,
                "year": year,
            }
            # Optional extra fields for forward compatibility
            if "session" in cols:
                row_data["session"] = session
            if "historical_std" in cols:
                row_data["historical_std"] = historical_std
            if "yearly_growth" in cols:
                row_data["yearly_growth"] = yearly_growth

            feature_df = pd.DataFrame([row_data])[cols]

            preds = model.predict(feature_df)
            predicted_percentile = float(preds[0])
        except Exception as err:
            print(f"[PercentilePredictor] Inference error on {canonical_exam}: {err}")
            predicted_percentile = base_historical_pct
    else:
        predicted_percentile = base_historical_pct

    # Physical boundary enforcement
    if m_clamped <= 0:
        predicted_percentile = 0.0
    elif m_clamped >= max_marks:
        predicted_percentile = 100.0
    else:
        predicted_percentile = float(np.clip(predicted_percentile, 0.01, 99.999))

    rounded_percentile = round(predicted_percentile, 2)

    # Confidence calculation
    conf_info = calculate_confidence_score(
        marks=m_clamped,
        max_marks=max_marks,
        difficulty=difficulty_level,
        shift=shift,
        mae=mae,
    )

    # Confidence Interval (±0.35% variance)
    range_min = max(0.0, round(predicted_percentile - 0.35, 2))
    range_max = min(100.0, round(predicted_percentile + 0.35, 2))
    percentile_range = f"{range_min:.2f}% – {range_max:.2f}%"

    # Rank estimation
    total_candidates = meta["base_candidates"]
    rank_fraction = max(0.000005, (100.0 - predicted_percentile) / 100.0)
    estimated_rank_num = max(1, int(round(rank_fraction * total_candidates)))

    # Performance Category
    performance_category = calculate_performance_category(predicted_percentile)

    # College Recommendations
    colleges = get_recommended_colleges_for_percentile(canonical_exam, predicted_percentile)

    # Advisory for low scores (<30 percentile)
    advisory_message = None
    if predicted_percentile < 30.0:
        advisory_message = (
            "Your predicted score is below 30 percentile, which is below the general cutoff for merit seats in "
            "government or top autonomous colleges through CAP rounds. We recommend focusing on private institutes, "
            "deemed universities, and institute-level / management quota seats."
        )

    res = {
        "exam": canonical_exam,
        "marks": round(m_clamped, 2),
        "max_marks": max_marks,
        "predicted_percentile": rounded_percentile,
        "predicted_percentile_precise": round(predicted_percentile, 4),
        "percentile_range": percentile_range,
        "estimated_rank": f"{meta['rank_label']} ~{estimated_rank_num:,}",
        "predicted_rank": estimated_rank_num,
        "predicted_air": estimated_rank_num,
        "confidence": conf_info["confidence"],
        "confidence_level": conf_info["confidence_level"],
        "performance_category": performance_category,
        "college_recommendations": colleges,
        "advisory_message": advisory_message,
        "difficulty_level": difficulty_level,
        "shift": shift,
        "session": session,
    }

    return res
