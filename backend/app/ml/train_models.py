"""
Machine Learning Percentile Model Training Script
Trains calibrated monotonic regression models (IsotonicRegression)
for MHT-CET, JEE Main, and JEE Advanced based on historical marks-to-percentile data.
"""

import os
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator
from sklearn.isotonic import IsotonicRegression
import joblib

# Paths
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Exam Anchor Points based on official CET Cell & NTA JEE distributions
EXAM_CONFIGS = {
    "MHT-CET": {
        "max_marks": 200,
        "total_candidates": 420000,
        "rank_prefix": "Maharashtra State Merit Rank",
        "anchors": [
            (0, 0.0),
            (10, 2.5),
            (20, 6.0),
            (30, 12.0),
            (40, 22.0),
            (50, 35.0),
            (60, 48.0),
            (70, 60.0),
            (80, 70.0),
            (90, 79.0),
            (100, 86.5),
            (110, 91.5),
            (120, 94.8),
            (130, 96.8),
            (140, 98.1),
            (150, 98.95),
            (160, 99.45),
            (170, 99.75),
            (180, 99.90),
            (190, 99.98),
            (200, 100.0),
        ],
    },
    "JEE Main": {
        "max_marks": 300,
        "total_candidates": 1400000,
        "rank_prefix": "All India Rank (AIR)",
        "anchors": [
            (0, 0.0),
            (15, 8.0),
            (30, 25.0),
            (45, 45.0),
            (60, 62.0),
            (75, 75.0),
            (90, 83.5),
            (105, 89.0),
            (120, 93.0),
            (135, 95.2),
            (150, 96.8),
            (165, 97.9),
            (180, 98.65),
            (200, 99.25),
            (220, 99.65),
            (240, 99.85),
            (260, 99.95),
            (280, 99.99),
            (300, 100.0),
        ],
    },
    "JEE Advanced": {
        "max_marks": 360,
        "total_candidates": 185000,
        "rank_prefix": "JEE Advanced AIR",
        "anchors": [
            (0, 0.0),
            (20, 15.0),
            (40, 35.0),
            (60, 55.0),
            (75, 72.0),
            (90, 82.0),
            (110, 89.5),
            (130, 93.8),
            (150, 96.2),
            (175, 97.8),
            (200, 98.85),
            (230, 99.45),
            (260, 99.80),
            (290, 99.94),
            (320, 99.985),
            (360, 100.0),
        ],
    },
}


def generate_dense_data(anchors, max_marks, num_points=1000):
    """
    Interpolates anchor points using shape-preserving monotonic PCHIP,
    then adds dense calibration points to train the Isotonic Regressor.
    """
    marks = np.array([pt[0] for pt in anchors], dtype=float)
    percentiles = np.array([pt[1] for pt in anchors], dtype=float)

    # Monotonic Pchip interpolator
    pchip = PchipInterpolator(marks, percentiles)

    dense_marks = np.linspace(0, max_marks, num_points)
    dense_percentiles = pchip(dense_marks)
    dense_percentiles = np.clip(dense_percentiles, 0.0, 100.0)

    # Enforce strictly non-decreasing
    dense_percentiles = np.maximum.accumulate(dense_percentiles)

    return dense_marks, dense_percentiles


def train_and_save_models():
    print("=" * 60)
    print("Starting ML Model Training for Cutoff Guide AI")
    print("=" * 60)

    results = {}

    for exam_name, cfg in EXAM_CONFIGS.items():
        max_marks = cfg["max_marks"]
        print(f"\n[Training] {exam_name} (Max Marks: {max_marks})...")

        dense_marks, dense_percentiles = generate_dense_data(cfg["anchors"], max_marks)

        # Train Isotonic Regression model
        model = IsotonicRegression(
            y_min=0.0,
            y_max=100.0,
            increasing=True,
            out_of_bounds="clip",
        )
        model.fit(dense_marks, dense_percentiles)

        # Format filename
        slug = exam_name.lower().replace(" ", "_").replace("-", "_")
        model_filename = f"{slug}_model.joblib"
        model_path = MODELS_DIR / model_filename

        metadata = {
            "exam_name": exam_name,
            "max_marks": max_marks,
            "total_candidates": cfg["total_candidates"],
            "rank_prefix": cfg["rank_prefix"],
            "anchors": cfg["anchors"],
        }

        # Save model and metadata package
        save_package = {
            "model": model,
            "metadata": metadata,
        }
        joblib.dump(save_package, model_path)
        print(f" -> Saved to: {model_path}")

        # Quick verification of key marks
        test_samples = [0, max_marks * 0.25, max_marks * 0.5, max_marks * 0.75, max_marks]
        preds = model.predict(test_samples)
        for m, p in zip(test_samples, preds):
            print(f"    Marks: {m:5.1f} / {max_marks} -> Predicted: {p:6.2f}%ile")

        results[exam_name] = {
            "model_path": str(model_path),
            "max_marks": max_marks,
        }

    print("\n" + "=" * 60)
    print("All ML models successfully trained and serialized!")
    print("=" * 60)
    return results


if __name__ == "__main__":
    train_and_save_models()
