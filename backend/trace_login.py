import sys
sys.path.insert(0, r"D:\e drive\old data 1 E drive\Fourise Project\Cut_off_Guide\backend")

print("=== Tracing USER login imports ===")

print("1. Importing app.schemas.user...")
try:
    from app.schemas.user import UserLogin
    print("   OK: schemas.user imported")
except Exception as e:
    import traceback
    print("   FAILED: %s: %s" % (type(e).__name__, e))
    traceback.print_exc()

print("2. Importing app.services.auth_service...")
try:
    from app.services.auth_service import normalize_phone, send_otp_sms, verify_otp_sms
    print("   OK: auth_service imported")
except Exception as e:
    import traceback
    print("   FAILED: %s: %s" % (type(e).__name__, e))
    traceback.print_exc()

print("3. Importing app.routes.admin (track_analytics_event)...")
try:
    from app.routes.admin import track_analytics_event
    print("   OK: admin routes imported")
except Exception as e:
    import traceback
    print("   FAILED: %s: %s" % (type(e).__name__, e))
    traceback.print_exc()

print("")
print("=== Checking root-level config _client state via import chain ===")

print("4. Checking if app/__init__.py triggers root config sync client...")
print("   (app package was already imported above)")
try:
    import config
    print("   root config._client = %s" % config._client)
    if config._client is None:
        print("   Sync client NOT yet instantiated (lazy init)")
    else:
        print("   Sync client ALREADY instantiated!")
except Exception as e:
    import traceback
    print("   FAILED: %s: %s" % (type(e).__name__, e))
    traceback.print_exc()

print("")
print("=== DB mismatch check ===")
import asyncio
from app.core.database import connect_to_mongo, get_db

async def check():
    await connect_to_mongo()
    db_motor = get_db()
    motor_users = await db_motor["users"].find({}).to_list(length=10000)
    
    import config as root_config
    sync_db = root_config.get_db()
    sync_users = list(sync_db["users"].find({}))
    
    motor_emails = set(u.get("email", "").lower() for u in motor_users if u.get("email"))
    sync_emails = set(u.get("email", "").lower() for u in sync_users if u.get("email"))
    
    print("Motor (cutoffgrid) users: %d" % len(motor_users))
    for u in motor_users:
        print("  - %s (%s) role=%s pw_hash=%s" % (
            u.get("email"), u.get("uid"), u.get("role"),
            bool(u.get("passwordHash") or u.get("password_hash"))
        ))
    print("")
    print("Sync (cutoff_db) users: %d" % len(sync_users))
    for u in sync_users:
        print("  - %s (%s) role=%s pw_hash=%s" % (
            u.get("email"), u.get("uid"), u.get("role"),
            bool(u.get("passwordHash") or u.get("password_hash"))
        ))
    
    only_motor = motor_emails - sync_emails
    only_sync = sync_emails - motor_emails
    print("")
    print("Only in Motor (cutoffgrid): %s" % only_motor)
    print("Only in Sync (cutoff_db): %s" % only_sync)

asyncio.run(check())
