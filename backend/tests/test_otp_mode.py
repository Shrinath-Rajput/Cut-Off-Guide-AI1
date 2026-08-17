import os
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

os.environ.setdefault("OTP_MODE", "development")

from app import create_app


class OtpModeTests(unittest.TestCase):
    def test_send_otp_in_development_mode_returns_success(self):
        import routes

        routes.OTP_MODE = "development"
        app = create_app()
        client = app.test_client()

        response = client.post(
            "/api/auth/send-otp",
            json={
                "name": "Test User",
                "email": "test@example.com",
                "phone": "+91 9876543210",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["status"], "success")
        self.assertIn("sessionId", payload)
        self.assertIn("dev_otp", payload)

    def test_send_otp_handles_fast2sms_provider_rejection_cleanly(self):
        import routes

        routes.OTP_MODE = "production"
        app = create_app()
        client = app.test_client()

        def make_http_error():
            error = HTTPError(
                url="https://www.fast2sms.com/dev/bulkV2",
                code=400,
                msg="Bad Request",
                hdrs=None,
                fp=None,
            )
            error.read = lambda: b'{"return":false,"status_code":416,"message":"You don\'t have sufficient wallet balance"}'
            return error

        with patch("routes.urllib_request.urlopen", side_effect=make_http_error()):
            response = client.post(
                "/api/auth/send-otp",
                json={
                    "name": "Test User",
                    "email": "test@example.com",
                    "phone": "+919699510445",
                },
            )

        self.assertEqual(response.status_code, 503)
        payload = response.get_json()
        self.assertEqual(payload["status"], "error")
        self.assertIn("Fast2SMS rejected the OTP request", payload["message"])

    def test_google_auth_rejects_invalid_firebase_token(self):
        import routes

        app = create_app()
        client = app.test_client()

        with patch.object(routes, "_verify_firebase_id_token", side_effect=ValueError("Invalid or expired Firebase ID token")):
            response = client.post(
                "/api/auth/google",
                json={"idToken": "not-a-real-firebase-id-token"},
            )

        self.assertEqual(response.status_code, 401)
        payload = response.get_json()
        self.assertEqual(payload["status"], "error")
        self.assertIn("Firebase", payload["message"])


if __name__ == "__main__":
    unittest.main()
