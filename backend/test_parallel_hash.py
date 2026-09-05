import sys
import concurrent.futures
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.security import verify_password

hash_val = "$bcrypt-sha256$v=2,t=2b,r=12$HXSIleurlXY/t.7VASrhuu$5EYXWvqQ1owQ86SyjdqMqfkzKi/O2Oe"

variations = set()

names = ["shrinath", "Shrinath", "SHRINATH", "rajput", "Rajput", "RAJPUT", "shrinathrajput", "ShrinathRajput", "Shrinath_Rajput", "rajputshrinath", "Shrinath_rajput", "shrinath_Rajput"]
seps = ["@", "#", "$", "%", "&", "*", "_", "-", "!", ".", ""]
nums = ["123456", "123", "1234", "12345", "12345678", "123456789", "349", "03", "33", "2026", "2025", "2024", "2023", "9699510445", "9699", "0445", "1", "12", "01", "007", ""]

for n in names:
    for s in seps:
        for num in nums:
            variations.add(f"{n}{s}{num}")
            variations.add(f"{num}{s}{n}")
            if s:
                variations.add(f"{n}{num}{s}")

var_list = list(variations)
print(f"Testing {len(var_list)} variations with 8 workers...", flush=True)

def check_pwd(p):
    try:
        if verify_password(p, hash_val):
            return p
    except Exception:
        pass
    return None

found = None
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
    results = executor.map(check_pwd, var_list)
    for res in results:
        if res:
            found = res
            print(f">>> FOUND MATCH: '{found}' <<<", flush=True)
            break

if not found:
    print("No match found in generated variations.", flush=True)
