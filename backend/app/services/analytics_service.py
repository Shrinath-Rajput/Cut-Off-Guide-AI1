from datetime import datetime, timezone
from typing import Any, Dict, Optional


async def track_analytics_event(
    db,
    event_type: str,
    user_id: Optional[str] = None,
    college_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None,
):
    if db is None:
        return None

    event = {
        "eventType": event_type,
        "timestamp": timestamp or datetime.now(timezone.utc),
    }
    if user_id:
        event["userId"] = str(user_id)
    if college_id:
        event["collegeId"] = str(college_id)
    if metadata:
        event["metadata"] = metadata

    try:
        await db["analytics_events"].insert_one(event)
    except Exception:
        return None
    return event
