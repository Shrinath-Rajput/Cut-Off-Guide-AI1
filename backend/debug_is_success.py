#!/usr/bin/env python
"""
Debug is_fast2sms_success logic
"""
import json

# Simulate the Fast2SMS response (with wallet error)
parsed_response = {
    'return': False,
    'status_code': 416,
    'message': "You don't have sufficient wallet balance"
}

# Simulate is_fast2sms_success logic
rejection_text = ' '.join(
    str(value)
    for value in [
        parsed_response.get('message'),
        parsed_response.get('status'),
        parsed_response.get('status_code'),
    ]
    if value is not None
).lower()

print("Parsed Response:", json.dumps(parsed_response, indent=2))
print("\nRejection Text:", repr(rejection_text))

rejection_markers = (
    'blocked',
    'dnd',
    'rejected',
    'invalid',
    'insufficient',
    'unauthorized',
    'authentication',
    'template',
    'sender',
    'not sent',
    'failed',
)

has_rejection = any(marker in rejection_text for marker in rejection_markers)
print("Has Rejection Marker:", has_rejection)
print("Markers found:", [m for m in rejection_markers if m in rejection_text])

# This should return False immediately if rejection marker is found
print("\n✅ is_fast2sms_success should return: False (due to rejection marker)")

# But let's check what happens if we continue...
status_code = 200  # HTTP status code returned by urllib
status_int = int(status_code)
print(f"\nHTTP Status Code: {status_code}")
print(f"Is 200-300 range: {200 <= status_int < 300}")

# Check for success indicators
return_value = parsed_response.get('return')
print(f"\nReturn Value from Fast2SMS: {return_value}")
print(f"Is Success (True/1/true): {return_value in (True, 'true', 'True', '1', 1)}")

print("\n" + "="*60)
print("The issue is that despite rejection_markers being found,")
print("the backend might not be calling is_fast2sms_success correctly.")
print("="*60)
