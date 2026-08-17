import json, urllib.request, urllib.error
url = 'http://127.0.0.1:5000/api/auth/send-otp'
data = json.dumps({"name":"Test User","email":"test@example.com","phone":"9876543210"}).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={'Content-Type':'application/json'})
try:
    resp = urllib.request.urlopen(req, timeout=30)
    print('STATUS', resp.status)
    print(resp.read().decode())
except urllib.error.HTTPError as e:
    print('HTTPERR', e.code, e.read().decode())
except Exception as e:
    print('ERR', e)
