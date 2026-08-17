import json
import os
from pathlib import Path
from urllib import error as urllib_error
from urllib import request as urllib_request
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / '.env')
key = os.getenv('FAST_TO_SMS_API_KEY')

payloads = [
    {
        'name': 'bulkV2 message route',
        'url': 'https://www.fast2sms.com/dev/bulkV2',
        'body': {
            'sender_id': 'FSTSMS',
            'message': 'Test OTP message from backend',
            'language': 'english',
            'route': 'q',
            'numbers': '919876543210',
        },
    },
    {
        'name': 'bulkV2 OTP route',
        'url': 'https://www.fast2sms.com/dev/otp',
        'body': {
            'numbers': '919876543210',
            'variables_values': '123456',
            'sender_id': 'FSTSMS',
            'route': 'otp',
            'language': 'english',
            'flash': 0,
        },
    },
]

for item in payloads:
    print('===', item['name'], '===')
    data = json.dumps(item['body']).encode('utf-8')
    req = urllib_request.Request(
        item['url'],
        data=data,
        headers={'Content-Type': 'application/json', 'authorization': key},
        method='POST',
    )
    try:
        with urllib_request.urlopen(req, timeout=25) as response:
            print('status', response.status)
            print(response.read().decode('utf-8', 'ignore'))
    except urllib_error.HTTPError as exc:
        print('http_error', exc.code)
        print(exc.read().decode('utf-8', 'ignore'))
    except Exception as exc:
        print('err', type(exc).__name__, exc)
