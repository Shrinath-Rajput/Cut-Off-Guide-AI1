import asyncio
from datetime import datetime, timezone

from bson import ObjectId
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash
from app.routes import admin, super_admin
from app.routes.auth import login
from app.schemas.user import UserLogin


class FakeCollection:
    def __init__(self, docs=None):
        self.docs = docs or []

    async def find_one(self, query):
        if '$or' in query:
            for condition in query['$or']:
                match = await self.find_one(condition)
                if match:
                    return match
            return None
        for doc in self.docs:
            if query.get('email') and doc.get('email') == query.get('email'):
                return doc
            if query.get('phone') and doc.get('phone') == query.get('phone'):
                return doc
            if query.get('role') and doc.get('role') == query.get('role'):
                return doc
            if query.get('uid') and doc.get('uid') == query.get('uid'):
                return doc
            if query.get('username') and doc.get('username') == query.get('username'):
                return doc
        return None

    async def insert_one(self, doc):
        self.docs.append(doc)

        class Result:
            inserted_id = "fake-id"

        return Result()

    async def update_one(self, filter_doc, update):
        for doc in self.docs:
            if filter_doc.get('_id') and doc.get('_id') == filter_doc.get('_id'):
                doc.update(update.get('$set', {}))
                return type('Result', (), {'matched_count': 1})()
        return type('Result', (), {'matched_count': 0})()

    async def find(self, query=None):
        return self

    async def to_list(self, length=10000):
        return list(self.docs)


class FakeDB(dict):
    def __init__(self):
        super().__init__()
        self['users'] = FakeCollection()

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    @property
    def users(self):
        return self['users']


class FakeUserDB(FakeDB):
    def __init__(self):
        super().__init__()
        self['users'].docs = [{
            "_id": "admin-1",
            "uid": "admin-1",
            "email": "admin@example.com",
            "role": "ADMIN",
            "passwordHash": get_password_hash("Admin@123"),
            "provider": "password",
            "name": "Admin User",
            "phone": "9876543210",
            "isActive": True,
        }, {
            "_id": "super-admin-1",
            "uid": "super-admin-1",
            "email": "fourise@gmail.com",
            "role": "SUPER_ADMIN",
            "passwordHash": get_password_hash("SuperAdmin@2026!"),
            "provider": "password",
            "name": "Super Admin",
            "phone": "9699510445",
            "isActive": True,
        }]

    async def list_collection_names(self):
        return ["users"]


def test_super_admin_routes_are_registered():
    client = TestClient(app)
    login_response = client.post('/api/admin/super-admin/login', json={"email": "fourise@gmail.com", "password": "wrong"})
    dashboard_response = client.get('/api/admin/super-admin/dashboard')
    assert login_response.status_code == 503
    assert dashboard_response.status_code == 401
    assert dashboard_response.json()["detail"] == "Not authenticated"


def test_super_admin_token_and_role():
    token = create_access_token("super-admin-1", role="SUPER_ADMIN")
    assert token
    payload = admin._safe_decode_token(token)
    assert payload["role"] == "SUPER_ADMIN"
    assert payload["sub"] == "super-admin-1"


def test_ensure_super_admin_creates_super_admin_user():
    db = FakeDB()
    asyncio.run(admin.ensure_super_admin_account(db))
    user = db.users.docs[0]
    assert user["role"] == "SUPER_ADMIN"
    assert user["email"] == "fourise@gmail.com"
    assert user["phone"] == "9699510445"


def test_login_preserves_existing_admin_credentials():
    db = FakeUserDB()
    result = asyncio.run(login(UserLogin(username="admin@example.com", password="Admin@123"), db))
    assert result["status"] == "success"
    assert result["user"]["role"] == "ADMIN"
    assert result["token"]


def test_login_accepts_super_admin_credentials():
    original_email = settings.SUPER_ADMIN_EMAIL
    original_password = settings.SUPER_ADMIN_PASSWORD
    settings.SUPER_ADMIN_EMAIL = "fourise@gmail.com"
    settings.SUPER_ADMIN_PASSWORD = "SuperAdmin@2026!"

    try:
        db = FakeUserDB()
        result = asyncio.run(login(UserLogin(username="fourise@gmail.com", password="SuperAdmin@2026!"), db))
        assert result["status"] == "success"
        assert result["user"]["role"] == "SUPER_ADMIN"
        assert result["token"]
    finally:
        settings.SUPER_ADMIN_EMAIL = original_email
        settings.SUPER_ADMIN_PASSWORD = original_password


def test_login_accepts_configured_super_admin_from_env_before_db_lookup():
    original_email = settings.SUPER_ADMIN_EMAIL
    original_password = settings.SUPER_ADMIN_PASSWORD
    settings.SUPER_ADMIN_EMAIL = "fourise@gmail.com"
    settings.SUPER_ADMIN_PASSWORD = "CompanySecret@123"

    try:
        db = FakeDB()
        result = asyncio.run(login(UserLogin(username="fourise@gmail.com", password="CompanySecret@123"), db))
        assert result["status"] == "success"
        assert result["user"]["role"] == "SUPER_ADMIN"
        assert result["token"]
    finally:
        settings.SUPER_ADMIN_EMAIL = original_email
        settings.SUPER_ADMIN_PASSWORD = original_password


def test_super_admin_dashboard_serializes_mongo_values():
    user_id = ObjectId("64f000000000000000000001")
    college_id = ObjectId("64f000000000000000000002")

    class DashboardCollection:
        async def count_documents(self, query=None):
            return 1

        def find(self, query=None, *args, **kwargs):
            class Cursor:
                def sort(self, *args, **kwargs):
                    return self

                def limit(self, *args, **kwargs):
                    return self

                async def to_list(self, length=None):
                    return [{
                        "_id": user_id,
                        "uid": "user-1",
                        "name": "Alice",
                        "email": "alice@example.com",
                        "createdAt": datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc),
                        "role": "USER",
                        "isActive": True,
                    }]
            return Cursor()

        def aggregate(self, pipeline):
            class Cursor:
                async def to_list(self, length=None):
                    return [{"_id": college_id, "count": 3}, {"_id": "college-2", "count": 1}]
            return Cursor()

    class DashboardDB(dict):
        def __init__(self):
            self["users"] = DashboardCollection()
            self["colleges"] = DashboardCollection()
            self["analytics_events"] = DashboardCollection()

        async def list_collection_names(self):
            return []

    dashboard = asyncio.run(admin.get_super_admin_dashboard_secure({"role": "SUPER_ADMIN"}, DashboardDB()))

    assert dashboard["data"]["mostSearchedColleges"][0]["_id"] == str(college_id)
    assert dashboard["data"]["recentUsers"][0]["id"] == str(user_id)
    assert dashboard["data"]["recentUsers"][0]["createdAt"].endswith("+00:00")


def test_super_admin_dashboard_route_handles_week_window_when_day_is_less_than_7(monkeypatch):
    class FrozenDateTime:
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc)

    monkeypatch.setattr(super_admin, "datetime", FrozenDateTime)

    class DashboardCollection:
        async def count_documents(self, query=None):
            return 1 if query and query.get("eventType") in {"COLLEGE_SEARCH", "COLLEGE_VIEW"} else 2

        def find(self, query=None, *args, **kwargs):
            class Cursor:
                def sort(self, *args, **kwargs):
                    return self

                def limit(self, *args, **kwargs):
                    return self

                async def to_list(self, length=None):
                    return [{
                        "_id": ObjectId("64f000000000000000000001"),
                        "uid": "user-1",
                        "name": "Alice",
                        "email": "alice@example.com",
                        "createdAt": datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc),
                        "role": "USER",
                        "isActive": True,
                    }, {
                        "_id": ObjectId("64f000000000000000000002"),
                        "uid": "user-2",
                        "name": "Bob",
                        "email": "bob@example.com",
                        "createdAt": datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc),
                        "role": "ADMIN",
                        "isActive": True,
                    }]
            return Cursor()

        def aggregate(self, pipeline):
            class Cursor:
                async def to_list(self, length=None):
                    return [{"_id": "college-1", "count": 3}]
            return Cursor()

    class DashboardDB(dict):
        def __init__(self):
            self["users"] = DashboardCollection()
            self["colleges"] = DashboardCollection()
            self["analytics_events"] = DashboardCollection()

    dashboard = asyncio.run(super_admin.get_super_admin_dashboard({"role": "SUPER_ADMIN"}, DashboardDB()))

    assert dashboard["status"] == "success"
    assert dashboard["data"]["summary"]["totalUsers"] == 2
    assert dashboard["data"]["summary"]["totalColleges"] == 2
    assert dashboard["data"]["mostSearchedColleges"][0]["_id"] == "college-1"


def test_super_admin_dashboard_returns_zero_data_when_collections_are_empty(monkeypatch):
    class FrozenDateTime:
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc)

    monkeypatch.setattr(admin, "datetime", FrozenDateTime)

    class EmptyDashboardCollection:
        async def count_documents(self, query=None):
            return 0

        def find(self, query=None, *args, **kwargs):
            class Cursor:
                def sort(self, *args, **kwargs):
                    return self

                def limit(self, *args, **kwargs):
                    return self

                async def to_list(self, length=None):
                    return []
            return Cursor()

        def aggregate(self, pipeline):
            class Cursor:
                async def to_list(self, length=None):
                    return []
            return Cursor()

    class EmptyDashboardDB(dict):
        def __init__(self):
            self["users"] = EmptyDashboardCollection()
            self["colleges"] = EmptyDashboardCollection()
            self["analytics_events"] = EmptyDashboardCollection()

        async def list_collection_names(self):
            return []

    dashboard = asyncio.run(admin.get_super_admin_dashboard_secure({"role": "SUPER_ADMIN"}, EmptyDashboardDB()))

    assert dashboard["status"] == "success"
    assert dashboard["data"]["summary"]["totalUsers"] == 0
    assert dashboard["data"]["summary"]["totalColleges"] == 0
    assert dashboard["data"]["summary"]["totalCollegeSearches"] == 0
    assert dashboard["data"]["summary"]["totalCollegeVisits"] == 0
    assert dashboard["data"]["mostSearchedColleges"] == []
    assert dashboard["data"]["mostVisitedColleges"] == []
    assert dashboard["data"]["recentSearches"] == []
    assert dashboard["data"]["recentCollegeVisits"] == []
    assert dashboard["data"]["recentActivity"] == []
    assert dashboard["data"]["recentUsers"] == []
