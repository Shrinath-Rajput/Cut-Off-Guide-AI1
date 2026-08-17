#!/usr/bin/env python
import requests
import json

# Test in development mode
payload = {
    'name': 'Test User DEV',
    'email': 'test.dev@example.com',
    'phone': '+919876543210'
}

response = requests.post('http://localhost:5000/api/auth/send-otp', json=payload)
print('Status:', response.status_code)
result = response.json()
print('Response:')
print(json.dumps(result, indent=2))

if 'dev_otp' in result:
    otp = result['dev_otp']
    session_id = result['sessionId']
    print(f'\nDevelopment Mode - Test OTP: {otp}')
    print(f'Session ID: {session_id}')
    
    # Now test verification with this OTP
    print('\n' + '='*60)
    print('Testing OTP Verification...')
    print('='*60)
    
    verify_payload = {
        'name': payload['name'],
        'email': payload['email'],
        'phone': payload['phone'],
        'otp': otp,
        'sessionId': session_id,
    }
    
    verify_response = requests.post('http://localhost:5000/api/auth/verify-otp', json=verify_payload)
    print(f'Status: {verify_response.status_code}')
    verify_result = verify_response.json()
    print('Response:')
    print(json.dumps(verify_result, indent=2))
    
    if verify_response.status_code == 200:
        print('\n✅ OTP Verification Successful!')
        print(f'User: {verify_result.get("user", {}).get("name")}')
        print(f'Token: {verify_result.get("token", "N/A")}')
    else:
        print(f'\n❌ OTP Verification Failed')
