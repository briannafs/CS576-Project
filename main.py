import os.path
import base64
from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def start_gmail_api():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w", encoding="utf-8") as token_file:
            token_file.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)

def send_test_email(service, to_email):
    message = EmailMessage()
    message["To"] = to_email
    message["From"] = "me"
    message["Subject"] = "Mailbox Project Test Email"
    message.set_content("This is a test from the mailbox detection project.")

    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode("utf-8")

    request_body = {"raw": encoded_message}

    response = (
        service.users()
        .messages()
        .send(userId="me", body=request_body)
        .execute()
    )

    return response

def main():
    recipient = input("Enter the email address to receive the test email: ").strip()

    service = start_gmail_api()
    result = send_test_email(service, recipient)

    print("Email sent successfully.")
    print(result)

if __name__ == "__main__":
    main()