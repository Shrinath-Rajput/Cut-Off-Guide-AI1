import os
import json
from pathlib import Path
import pandas as pd

ROOT = Path(r'D:\e drive\old data 1 E drive\Fourise Project\Cut_off_Guide\Cut_Off_Project\Cut_Off_Project\DataSet')

csv_files = []
for path in ROOT.rglob('*'):
    if path.is_file() and path.suffix.lower() == '.csv':
        csv_files.append(path)

print(f'CSV_COUNT={len(csv_files)}')
for p in csv_files[:10]:
    rel = p.relative_to(ROOT)
    try:
        df = pd.read_csv(p)
        print(f'FILE={rel}')
        print('SHAPE=', df.shape)
        print('COLUMNS=', list(df.columns[:20]))
        print(df.head(3).to_dict(orient='records'))
        print('DTYPES=')
        print(df.dtypes.head(20).to_dict())
        print('---')
    except Exception as e:
        print('ERR', rel, type(e).__name__, e)

json_files = []
for path in ROOT.rglob('*'):
    if path.is_file() and path.suffix.lower() == '.json':
        json_files.append(path)

print(f'JSON_COUNT={len(json_files)}')
for p in json_files[:10]:
    rel = p.relative_to(ROOT)
    try:
        with open(p, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
        if isinstance(data, list):
            df = pd.DataFrame(data)
            print(f'FILE={rel}')
            print('SHAPE=', df.shape)
            print('COLUMNS=', list(df.columns[:20]))
            print(df.head(3).to_dict(orient='records'))
            print('DTYPES=')
            print(df.dtypes.head(20).to_dict())
        else:
            print(f'FILE={rel} TYPE={type(data).__name__}')
            if isinstance(data, dict):
                print('KEYS=', list(data.keys())[:10])
                for k,v in list(data.items())[:3]:
                    if isinstance(v, list):
                        print(k, 'len=', len(v), 'sample=', v[:2])
                    else:
                        print(k, type(v).__name__, v)
        print('---')
    except Exception as e:
        print('ERR', rel, type(e).__name__, e)
