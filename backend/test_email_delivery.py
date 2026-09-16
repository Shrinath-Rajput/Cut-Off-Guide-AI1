import os
from dotenv import load_dotenv
load_dotenv("C:\\Users\\HP\\Cut-Off-Guide-AI1\\backend\\.env")

from app.services.email_service import send_contact_email
import logging
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    try:
        scenarios = [
            ("Rahul", "rahul@gmail.com", "Test Gmail"),
            ("Priya", "priya@yahoo.com", "Test Yahoo"),
            ("Test User", "testuser@outlook.com", "Test Outlook")
        ]
        for i, (name, test_email, subject) in enumerate(scenarios, 1):
            print(f"\n--- TEST {i}: Logged-in user email: {test_email} ---")
            send_contact_email(
                name=name,
                user_email=test_email,
                subject=subject,
                message_body="Testing contact form."
            )
            print(f"Email {i} sending executed successfully.")
    except Exception as e:
        print(f"Error occurred: {e}")
