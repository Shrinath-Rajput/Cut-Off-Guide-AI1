import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder

ROOT = Path(__file__).resolve().parents[1]
DATASET_ROOT = Path(r'D:\e drive\old data 1 E drive\Fourise Project\Cut_off_Guide\Cut_Off_Project\Cut_Off_Project\DataSet')
PROCESSED_DIR = ROOT / 'dataset' / 'processed'
MODELS_DIR = ROOT / 'models'

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)


def normalize_text(value):
    if pd.isna(value):
        return None
    text = str(value).strip()
    return text if text else None


def parse_cap_round(value):
    if pd.isna(value):
        return np.nan
    text = str(value).strip().upper()
    if not text:
        return np.nan
    if text.startswith('ROUND-'):
        digits = ''.join(ch for ch in text if ch.isdigit())
        return int(digits) if digits else np.nan
    if text in {'I', 'II', 'III', 'IV', 'V'}:
        return {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5}[text]
    digits = ''.join(ch for ch in text if ch.isdigit())
    return int(digits) if digits else np.nan


def normalize_exam_name(value):
    text = normalize_text(value)
    if text is None:
        return 'Unknown'
    upper = text.upper()
    if 'MHT' in upper or 'CET' in upper:
        if 'PHARM' in upper:
            return 'MHT-CET-Pharmacy'
        if 'ENGG' in upper or 'ENGINEERING' in upper:
            return 'MHT-CET-Engineering'
        return 'MHT-CET'
    if 'BBA' in upper:
        return 'BBA'
    if 'MBA' in upper:
        return 'MBA'
    if 'MCA' in upper:
        return 'MCA'
    return text


def read_candidate_csvs():
    folders = [
        DATASET_ROOT / 'BPharma',
        DATASET_ROOT / 'MHT CET Enggineering',
        DATASET_ROOT / 'BBA',
        DATASET_ROOT / 'MBA',
        DATASET_ROOT / 'MCA',
    ]
    files = []
    for folder in folders:
        if not folder.exists():
            continue
        for path in sorted(folder.rglob('*.csv')):
            if path.is_file():
                files.append(path)
    return files


def standardize_row_file(df):
    out = df.copy()
    cols = [str(c).strip() for c in out.columns]
    out.columns = cols

    mapping = {
        'exam': {'exam', 'exam name'},
        'course_name': {'branch name', 'course name', 'programme name'},
        'category': {'category'},
        'seat_type': {'seat type', 'type'},
        'status': {'status'},
        'cap_round': {'round', 'cap round', 'cap_round'},
        'year': {'year'},
        'percentile': {'percentile'},
        'cutoff_rank': {'cutoff rank'},
        'score': {'score', 'merit'},
    }

    result = {}
    for key, aliases in mapping.items():
        match = None
        for col in cols:
            if str(col).strip().lower() in aliases:
                match = col
                break
        if match is None:
            result[key] = pd.Series([np.nan] * len(out), index=out.index)
        else:
            result[key] = out[match].copy()

    if 'percentile' not in out.columns.map(str).str.lower().tolist() and 'score' in out.columns.map(str).str.lower().tolist():
        result['percentile'] = pd.to_numeric(result['score'], errors='coerce')

    frame = pd.DataFrame({
        'exam': result['exam'],
        'course_name': result['course_name'],
        'category': result['category'],
        'seat_type': result['seat_type'],
        'status': result['status'],
        'cap_round': result['cap_round'],
        'year': result['year'],
        'percentile': result['percentile'],
        'cutoff_rank': result['cutoff_rank'],
        'score': result['score'],
    })

    return frame


def build_training_data():
    frames = []
    for path in read_candidate_csvs():
        try:
            df = pd.read_csv(path, low_memory=False)
        except Exception:
            continue
        if df.empty:
            continue
        frames.append(standardize_row_file(df))

    if not frames:
        raise FileNotFoundError(f'No usable cutoff CSV files found under {DATASET_ROOT}')

    combined = pd.concat(frames, ignore_index=True, sort=False)
    combined['exam'] = combined['exam'].map(normalize_exam_name)
    combined['course_name'] = combined['course_name'].map(normalize_text)
    combined['category'] = combined['category'].map(normalize_text)
    combined['seat_type'] = combined['seat_type'].map(normalize_text)
    combined['status'] = combined['status'].map(normalize_text)
    combined['cap_round'] = combined['cap_round'].apply(parse_cap_round)
    combined['year'] = pd.to_numeric(combined['year'], errors='coerce')
    combined['percentile'] = pd.to_numeric(combined['percentile'], errors='coerce')
    combined['cutoff_rank'] = pd.to_numeric(combined['cutoff_rank'], errors='coerce')
    combined['score'] = pd.to_numeric(combined['score'], errors='coerce')

    combined = combined.drop_duplicates()
    combined = combined.dropna(subset=['exam', 'course_name', 'category', 'cap_round', 'year', 'percentile'])
    combined = combined[combined['percentile'].between(0, 100)].copy()
    combined = combined.reset_index(drop=True)
    return combined


def evaluate_models(df):
    feature_cols = ['exam', 'course_name', 'category', 'seat_type', 'status', 'cap_round', 'year']
    target_col = 'percentile'

    X = df[feature_cols]
    y = df[target_col]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    cat_features = [col for col in feature_cols if X[col].dtype == 'object']
    preprocessor = ColumnTransformer([
        ('ordinal', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1), cat_features),
    ], remainder='drop')

    models = {
        'RandomForestRegressor': RandomForestRegressor(n_estimators=250, random_state=42, min_samples_leaf=2),
        'GradientBoostingRegressor': GradientBoostingRegressor(random_state=42),
    }

    results = []
    for model_name, model in models.items():
        pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('model', model),
        ])
        pipeline.fit(X_train, y_train)
        preds = pipeline.predict(X_test)
        mae = mean_absolute_error(y_test, preds)
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        r2 = r2_score(y_test, preds)
        results.append({
            'model_name': model_name,
            'mae': float(mae),
            'rmse': float(rmse),
            'r2': float(r2),
        })

    best = max(results, key=lambda item: item['r2'])
    final_model = models[best['model_name']]
    final_pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('model', final_model),
    ])
    final_pipeline.fit(X, y)

    joblib.dump(final_pipeline, MODELS_DIR / 'cutoff_model.pkl')
    joblib.dump(preprocessor, MODELS_DIR / 'preprocessor.pkl')

    processed_path = PROCESSED_DIR / 'cutoff_training_data.csv'
    df.to_csv(processed_path, index=False)

    summary = {
        'dataset_rows': int(len(df)),
        'important_columns': feature_cols + ['score', 'cutoff_rank'],
        'feature_columns': feature_cols,
        'target_column': target_col,
        'target_type': 'regression',
        'reason': 'The source data contains real cutoff percentile values across multiple exam files but no consistent binary admission flag. Regression on Percentile is the valid target for this dataset.',
        'model_results': results,
        'best_model': best,
        'processed_file': str(processed_path),
        'model_file': str(MODELS_DIR / 'cutoff_model.pkl'),
        'preprocessor_file': str(MODELS_DIR / 'preprocessor.pkl')
    }

    with (MODELS_DIR / 'training_summary.json').open('w', encoding='utf-8') as fh:
        json.dump(summary, fh, indent=2)

    return summary


if __name__ == '__main__':
    df = build_training_data()
    summary = evaluate_models(df)
    print('TRAINING_ROWS=', summary['dataset_rows'])
    print('TARGET=', summary['target_column'])
    print('BEST_MODEL=', summary['best_model']['model_name'])
    print('BEST_R2=', round(summary['best_model']['r2'], 6))
    print('BEST_MAE=', round(summary['best_model']['mae'], 6))
    print('BEST_RMSE=', round(summary['best_model']['rmse'], 6))
    print('MODEL_PATH=', summary['model_file'])
    print('PREPROCESSOR_PATH=', summary['preprocessor_file'])
    print('PROCESSED_FILE=', summary['processed_file'])
