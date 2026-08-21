import urllib.request
import json
import urllib.error

req = urllib.request.Request(
    'http://127.0.0.1:5000/api/auth/login',
    method='OPTIONS',
    headers={
        'Origin': 'http://localhost:5173',
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type',
    }
)
with urllib.request.urlopen(req, timeout=5) as r:
    acao = r.headers.get('Access-Control-Allow-Origin', 'MISSING')
    acam = r.headers.get('Access-Control-Allow-Methods', 'MISSING')
    acah = r.headers.get('Access-Control-Allow-Headers', 'MISSING')
    print('[PREFLIGHT OPTIONS] HTTP', r.status)
    print('  Access-Control-Allow-Origin :', acao)
    print('  Access-Control-Allow-Methods:', acam[:80])
    print('  Access-Control-Allow-Headers:', acah[:80])

body = json.dumps({'username': 'nonexistent@x.com', 'password': 'anypass'}).encode()
req2 = urllib.request.Request(
    'http://127.0.0.1:5000/api/auth/login',
    data=body,
    method='POST',
    headers={
        'Origin': 'http://localhost:5173',
        'Content-Type': 'application/json',
    }
)
try:
    with urllib.request.urlopen(req2, timeout=5) as r2:
        print('[POST login] HTTP', r2.status)
        print('  Access-Control-Allow-Origin:', r2.headers.get('Access-Control-Allow-Origin', 'MISSING'))
except urllib.error.HTTPError as e:
    print('[POST login] HTTP', e.code, '(expected 401 for nonexistent user)')
    print('  Access-Control-Allow-Origin:', e.headers.get('Access-Control-Allow-Origin', 'MISSING'))
    raw = e.read().decode('utf-8', 'ignore')
    try:
        d = json.loads(raw)
        print('  Body detail:', d.get('detail'))
    except Exception:
        pass
