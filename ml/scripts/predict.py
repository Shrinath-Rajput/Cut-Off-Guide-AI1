import argparse
import json
from pathlib import Path

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / 'models' / 'cutoff_model.pkl'
PREPROCESSOR_PATH = ROOT / 'models' / 'preprocessor.pkl'


def build_payload(args):
    payload = {
        'exam': args.exam,
        'college_name': args.preferred_location or args.home_university or 'Unknown',
        'course_name': args.preferred_course or 'Unknown',
        'category': args.category or 'Unknown',
        'seat_type': args.home_university or 'Unknown',
        'status': args.gender or 'Unknown',
        'cap_round': int(args.cap_round) if args.cap_round is not None else 1,
        'year': int(args.year) if args.year is not None else 2025,
    }
    return pd.DataFrame([payload])


def main():
    parser = argparse.ArgumentParser(description='Predict the expected cutoff percentile for a candidate profile.')
    parser.add_argument('--exam', required=True, help='Exam name, e.g. MHT-CET or BBA')
    parser.add_argument('--score', type=float, default=None, help='Candidate score or percentile if known')
    parser.add_argument('--percentile', type=float, default=None, help='Candidate percentile if known')
    parser.add_argument('--category', default='Unknown', help='Category value such as GOPENH, OPEN, etc.')
    parser.add_argument('--gender', default='Unknown', help='Gender if available in future flow')
    parser.add_argument('--home-university', default='Unknown', help='Home university / home state value if available')
    parser.add_argument('--preferred-course', default='Unknown', help='Preferred course/branch')
    parser.add_argument('--preferred-location', default='Unknown', help='Preferred location or target college area')
    parser.add_argument('--cap-round', type=int, default=1, help='CAP round number')
    parser.add_argument('--year', type=int, default=2025, help='Admission year')
    args = parser.parse_args()

    model = joblib.load(MODEL_PATH)
    preprocessor = joblib.load(PREPROCESSOR_PATH)

    df = build_payload(args)
    prediction = model.predict(df)
    result = {
        'exam': args.exam,
        'category': args.category,
        'preferred_course': args.preferred_course,
        'cap_round': args.cap_round,
        'year': args.year,
        'predicted_percentile': float(prediction[0]),
        'model_path': str(MODEL_PATH),
        'preprocessor_path': str(PREPROCESSOR_PATH),
    }
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
