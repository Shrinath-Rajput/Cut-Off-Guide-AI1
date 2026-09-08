import unittest
from unittest.mock import patch, MagicMock
from urllib.error import HTTPError
import io
import json

from fastapi import HTTPException
from app.services.auth_service import send_otp_sms, verify_otp_sms, _build_fast2sms_request, normalize_phone


class AuthServiceOtpTests(unittest.IsolatedAsyncioTestCase):

    def test_normalize_phone(self):
        self.assertEqual(normalize_phone("9699510445"), "9699510445")
        self.assertEqual(normalize_phone("+91 9699510445"), "9699510445")
        self.assertEqual(normalize_phone("09699510445"), "9699510445")
        self.assertEqual(normalize_phone("919699510445"), "9699510445")
        with self.assertRaises(HTTPException):
            normalize_phone("12345")

    def test_build_fast2sms_request_normalizes_to_10_digits(self):
        params = _build_fast2sms_request("919699510445", "test message", otp=123456)
        self.assertEqual(params["numbers"], "9699510445")
        self.assertEqual(len(params["numbers"]), 10)

    async def test_send_otp_provider_key_disabled_raises_http_exception(self):
        err_body = b'{"return":false,"status_code":413,"message":"Invalid Authentication, Authorization Key Disabled"}'
        err_fp = io.BytesIO(err_body)
        err = HTTPError(
            url="https://www.fast2sms.com/dev/bulkV2",
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=err_fp
        )

        with patch("urllib.request.urlopen", side_effect=err):
            with self.assertRaises(HTTPException) as ctx:
                await send_otp_sms("9699510445", db=None)
            self.assertEqual(ctx.exception.status_code, 502)
            self.assertIn("SMS gateway authorization failed", ctx.exception.detail)

    async def test_send_otp_provider_rejection_raises_http_exception(self):
        body = b'{"return": false, "message": ["Invalid numbers parameter"]}'
        mock_resp = io.BytesIO(body)
        mock_resp.status = 200

        with patch("urllib.request.urlopen", return_value=mock_resp):
            with self.assertRaises(HTTPException) as ctx:
                await send_otp_sms("9699510445", db=None)
            self.assertEqual(ctx.exception.status_code, 502)
            self.assertIn("SMS API Error", ctx.exception.detail)

    async def test_send_otp_success_stores_and_verifies_otp(self):
        body = b'{"return": true, "status_code": 200, "request_id": "req_success_123"}'
        mock_resp = io.BytesIO(body)
        mock_resp.status = 200

        sent_otp = None
        import app.services.auth_service as s
        orig_store = s._store_otp
        async def wrap_store(phone, otp, db, session_id=None):
            nonlocal sent_otp
            sent_otp = otp
            return await orig_store(phone, otp, db, session_id)
        s._store_otp = wrap_store

        try:
            with patch("urllib.request.urlopen", return_value=mock_resp):
                result = await send_otp_sms("9699510445", db=None)
        finally:
            s._store_otp = orig_store

        self.assertIn("session_id", result)
        self.assertEqual(result.get("provider_request_id"), "req_success_123")
        session_id = result["session_id"]

        # Wrong OTP fails
        is_wrong_valid = await verify_otp_sms("9699510445", "000000", session_id, db=None)
        self.assertFalse(is_wrong_valid)

        # Correct OTP succeeds
        is_correct_valid = await verify_otp_sms("9699510445", str(sent_otp), session_id, db=None)
        self.assertTrue(is_correct_valid)

        # Replay fails
        is_replay_valid = await verify_otp_sms("9699510445", str(sent_otp), session_id, db=None)
        self.assertFalse(is_replay_valid)


if __name__ == "__main__":
    unittest.main()
