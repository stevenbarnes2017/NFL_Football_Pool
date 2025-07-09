import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("BREVO_API_KEY")

headers = {
    "accept": "application/json",
    "api-key": api_key,
    "content-type": "application/json"
}

data = {
    "sender": {"name": "Test App", "email": "youremail@example.com"},
    "to": [{"email": "youremail@example.com"}],
    "subject": "Test email from Brevo",
    "htmlContent": "<p>This is a test email from Brevo.</p>"
}

response = requests.post("https://api.brevo.com/v3/smtp/email", json=data, headers=headers)
print(response.status_code, response.text)