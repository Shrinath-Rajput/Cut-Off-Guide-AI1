import os
import unittest

import routes as r
from routes import (
    build_fast2sms_bulk_request,
    build_otp_sms_message,
    format_fast2sms_error_message,
    is_fast2sms_success,
    SMS_LANGUAGE,
    SMS_FLASH,
    SMS_SENDER_ID,
    SMS_TEMPLATE_ID,
    SMS_ENTITY_ID,
)


class Fast2SMSHelperTests(unittest.TestCase):
    def test_build_otp_sms_message_contains_otp_and_expiry(self):
        message = build_otp_sms_message("123456")
        self.assertIn("123456", message)
        self.assertIn("5 minutes", message)

    def test_build_fast2sms_bulk_request_transactional_uses_message_field(self):
        """For route 'q' / 'dlt' / 't' / 'p' payload uses free-form 'message'."""
        old_route = r.SMS_ROUTE
        old_tpl = r.SMS_TEMPLATE_ID
        old_ent = r.SMS_ENTITY_ID
        try:
            r.SMS_ROUTE = "q"
            r.SMS_TEMPLATE_ID = "tpl" if SMS_TEMPLATE_ID else ""
            r.SMS_ENTITY_ID = "ent" if SMS_ENTITY_ID else ""

            params = build_fast2sms_bulk_request("919876543210", "Hello OTP")
            self.assertEqual(params["numbers"], "919876543210")
            self.assertEqual(params["message"], "Hello OTP")
            self.assertIn("sender_id", params)
            self.assertEqual(params["sender_id"], SMS_SENDER_ID)
            self.assertEqual(params["route"], "q")
            self.assertEqual(params["language"], SMS_LANGUAGE)
            self.assertEqual(params["flash"], SMS_FLASH)
            if r.SMS_TEMPLATE_ID:
                self.assertIn("template_id", params)
                self.assertEqual(params["template_id"], "tpl")
            else:
                self.assertNotIn("template_id", params)
            if r.SMS_ENTITY_ID:
                self.assertIn("entity_id", params)
                self.assertEqual(params["entity_id"], "ent")
            else:
                self.assertNotIn("entity_id", params)
            self.assertNotIn("variables_values", params)
        finally:
            r.SMS_ROUTE = old_route
            r.SMS_TEMPLATE_ID = old_tpl
            r.SMS_ENTITY_ID = old_ent

    def test_build_fast2sms_bulk_request_otp_route_uses_variables_values(self):
        """For route 'otp' payload uses numeric variables_values, no message."""
        old_route = r.SMS_ROUTE
        old_tpl = r.SMS_TEMPLATE_ID
        old_ent = r.SMS_ENTITY_ID
        try:
            r.SMS_ROUTE = "otp"
            r.SMS_TEMPLATE_ID = "1701000000000000001"
            r.SMS_ENTITY_ID = ""

            params = build_fast2sms_bulk_request("919876543210", "ignored message", otp=987654)
            self.assertEqual(params["numbers"], "919876543210")
            self.assertEqual(params["route"], "otp")
            self.assertEqual(params["sender_id"], SMS_SENDER_ID)
            self.assertEqual(params["variables_values"], "987654")
            self.assertEqual(params["template_id"], "1701000000000000001")
            self.assertNotIn("message", params)
            self.assertNotIn("language", params)
            self.assertNotIn("flash", params)
        finally:
            r.SMS_ROUTE = old_route
            r.SMS_TEMPLATE_ID = old_tpl
            r.SMS_ENTITY_ID = old_ent

    def test_fast2sms_success_payload_is_recognized(self):
        payload = {"return": True, "request_id": "ABC123", "message": ["SMS sent successfully."]}
        self.assertTrue(is_fast2sms_success(payload, 200, None))

    def test_fast2sms_dnd_error_is_formatted_cleanly(self):
        payload = {"return": False, "status_code": 427, "message": "Number blocked in Fast2SMS DND list"}
        formatted = format_fast2sms_error_message(payload)
        self.assertIn("Fast2SMS", formatted)
        self.assertIn("DND", formatted)
        self.assertIn("427", formatted)

    def test_fast2sms_requires_dlt_config_in_production(self):
        old_mode = r.OTP_MODE
        old_route = r.SMS_ROUTE
        old_template = r.SMS_TEMPLATE_ID
        old_entity = r.SMS_ENTITY_ID
        old_key = r.FAST_TO_SMS_API_KEY

        try:
            r.OTP_MODE = "production"
            r.SMS_ROUTE = "q"
            r.SMS_TEMPLATE_ID = ""
            r.SMS_ENTITY_ID = ""
            r.FAST_TO_SMS_API_KEY = "dummy-key"

            with self.assertRaises(RuntimeError):
                r.validate_fast2sms_production_config()
        finally:
            r.OTP_MODE = old_mode
            r.SMS_ROUTE = old_route
            r.SMS_TEMPLATE_ID = old_template
            r.SMS_ENTITY_ID = old_entity
            r.FAST_TO_SMS_API_KEY = old_key


if __name__ == "__main__":
    unittest.main()
