import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.security import verify_password

hash_val = "$bcrypt-sha256$v=2,t=2b,r=12$HXSIleurlXY/t.7VASrhuu$5EYXWvqQ1owQ86SyjdqMqfkzKi/O2Oe"

variations = set()

names = ["shrinath", "Shrinath", "SHRINATH", "rajput", "Rajput", "RAJPUT", "shrinathrajput", "ShrinathRajput", "Shrinath_Rajput", "rajputshrinath"]
seps = ["@", "#", "$", "%", "&", "*", "_", "-", "!", ".", ""]
nums = ["123456", "123", "1234", "12345", "12345678", "123456789", "349", "03", "33", "2026", "2025", "2024", "2023", "9699510445", "9699", "0445", "1", "12", "01", "007", ""]

for n in names:
    for s in seps:
        for num in nums:
            variations.add(f"{n}{s}{num}")
            variations.add(f"{num}{s}{n}")
            if s:
                variations.add(f"{n}{num}{s}")

print(f"Generated {len(variations)} variations to test against hash...")

# Let's test them in batches
matches = []
for i, v in enumerate(variations):
    if i % 100 == 0:
        print(f"Testing {i}/{len(variations)}...")
    try:
        if verify_password(v, hash_val):
            print(f"\n>>> FOUND MATCH: '{v}' <<<\n")
            matches.append(v)
            break
    except Exception as e:
        pass

print("Done. Matches:", matches)
