import time
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.security import verify_password, get_password_hash

hash_val = "$bcrypt-sha256$v=2,t=2b,r=12$HXSIleurlXY/t.7VASrhuu$5EYXWvqQ1owQ86SyjdqMqfkzKi/O2Oe"

t0 = time.time()
res = verify_password("Shrinath@123456", hash_val)
t1 = time.time()
print(f"Result: {res}, Time: {t1-t0:.3f}s")
