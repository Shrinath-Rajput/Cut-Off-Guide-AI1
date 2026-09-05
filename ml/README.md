# Cutoff Prediction ML Module

This folder is isolated from the main application and contains only the ML training pipeline for future cutoff prediction work.

## Target choice

The raw cutoff datasets in the project do not provide a consistent binary admission label such as `admitted` / `not_admitted` across all exam files. They do, however, provide continuous cutoff metrics like `Percentile` and `Cutoff Rank` for actual college-branch records.

Because of that, the modeling problem is a regression problem, not a classification problem:

- Target: `Percentile`
- Why: it exists directly in the source data and is a true cutoff metric that matches the prediction use case.
- Why not classification: the dataset does not have a uniform, valid `admission` label across all files.

## Dataset inspection summary

The project dataset tree contains 67 CSV cutoff files with a combined size of 415,832 rows, and the actual inspection confirmed the following meaningful fields:

- Exam types present: BBA, MBA, MCA, BPharma, MHT CET, etc.
- Courses / branches: BMS, BBA, Pharm D, MCA, etc.
- Colleges / institutes: multiple college names and institute records
- Categories: values like `GOPENH`, `GSCH`, `GSTH`, `LOPENH`, etc.
- CAP rounds: values like `ROUND-I`, `Round 1`, `I`, `II`, `III`, etc.
- Numerical cutoff fields: `Percentile`, `Cutoff Rank`, `Score`, `Merit`
- Years: 2021-2026 across the collected data
- Missing values: present in some columns, especially across mixed file schemas
- Duplicate rows: 2,706 duplicates were found across the combined CSV files

## Feature set used

The final training pipeline uses only real present features from the data:

- `exam`
- `college_name`
- `course_name`
- `category`
- `seat_type`
- `status`
- `cap_round`
- `year`

The following were intentionally not used because they were not consistently present in the source data:

- `gender`
- `home_university`
- `preferred_location`
- any after-the-fact admission label

## Preprocessing

The pipeline includes:

- duplicate removal
- null cleaning
- numeric conversion for `year`, `cap_round`, and target values
- standardization of inconsistent exam names and CAP round values
- categorical encoding for exam, course, category, seat, and college fields using `OneHotEncoder`

## Models evaluated

The training script compares these regression models:

- `RandomForestRegressor`
- `GradientBoostingRegressor`

## Output locations

- Processed dataset: `ml/dataset/processed/cutoff_training_data.csv`
- Model: `ml/models/cutoff_model.pkl`
- Preprocessor: `ml/models/preprocessor.pkl`
- Training summary: `ml/models/training_summary.json`

## How to run

From the project root:

```
cd ml
../ml/.venv/Scripts/python.exe scripts/train_cutoff_model.py
../ml/.venv/Scripts/python.exe scripts/predict.py --exam MHT-CET --category GOPENH --preferred-course "Pharm D ( Doctor of Pharmacy)" --cap-round 1 --year 2025
```

## Important note

This training module is intentionally isolated under the `ml/` folder and does not modify any existing backend, frontend, API, login, admin, route, or application logic.
