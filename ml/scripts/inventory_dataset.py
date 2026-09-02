import os
from pathlib import Path
import pandas as pd

ROOT = Path(r'D:\e drive\old data 1 E drive\Fourise Project\Cut_off_Guide\Cut_Off_Project\Cut_Off_Project\DataSet')

all_csvs = sorted(p for p in ROOT.rglob('*.csv'))
print(f'TOTAL_CSV_FILES={len(all_csvs)}')

rows = []
for p in all_csvs:
    try:
        df = pd.read_csv(p)
        rows.append({
            'file': str(p.relative_to(ROOT)),
            'rows': len(df),
            'cols': list(df.columns),
            'missing': int(df.isna().sum().sum()),
            'dups': int(df.duplicated().sum()),
            'exam_values': list(df['Exam'].dropna().unique()[:10]) if 'Exam' in df.columns else [],
            'course_values': list(df['Course Name'].dropna().unique()[:10]) if 'Course Name' in df.columns else [],
            'branch_values': list(df['Branch Name'].dropna().unique()[:10]) if 'Branch Name' in df.columns else [],
            'college_values': list(df['College Name'].dropna().unique()[:10]) if 'College Name' in df.columns else [],
            'category_values': list(df['Category'].dropna().unique()[:10]) if 'Category' in df.columns else [],
            'percentile_present': 'Percentile' in df.columns,
            'score_present': 'Score' in df.columns,
            'cutoff_rank_present': 'Cutoff Rank' in df.columns,
            'merit_present': 'Merit' in df.columns,
        })
    except Exception as e:
        print(f'ERROR_FILE={p.relative_to(ROOT)}::{type(e).__name__}:{e}')

print('FILE_SUMMARY')
for r in rows[:20]:
    print(r['file'], r['rows'], r['cols'][:12], 'missing=', r['missing'], 'dups=', r['dups'])

# Combined summary across all csvs
all_df = []
for p in all_csvs:
    try:
        df = pd.read_csv(p)
        all_df.append(df)
    except Exception:
        pass
combined = pd.concat(all_df, ignore_index=True, sort=False)
print('COMBINED_ROWS=', len(combined))
print('COMBINED_COLS=', list(combined.columns))
print('MISSING_BY_COLUMN=')
print(combined.isna().sum().head(20).to_string())
print('DUPLICATE_ROWS=', int(combined.duplicated().sum()))
for c in ['Exam', 'Course Name', 'Branch Name', 'College Name', 'Category', 'Seat Type', 'Year', 'Round', 'cap_round', 'Status']:
    if c in combined.columns:
        vals = combined[c].dropna().astype(str).str.strip()
        print(f'{c}_UNIQUE={vals.nunique()}')
        print(vals.head(10).tolist())

for c in ['Percentile', 'Score', 'Cutoff Rank', 'Merit']:
    if c in combined.columns:
        s = pd.to_numeric(combined[c], errors='coerce')
        print(f'{c}_MIN={s.min()}')
        print(f'{c}_MAX={s.max()}')
        print(f'{c}_MEAN={s.mean()}')
        print(f'{c}_NULL={s.isna().sum()}')
