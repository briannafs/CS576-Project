import os.path
import base64
import time
import RPi.GPIO as GPIO
from hx711 import HX711
import pandas as pd
from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

#Set up GPIO mode
GPIO.setmode(GPIO.BCM)

#Initialize HX711
hx = HX711(dout_pin=6, pd_sck_pin=5)
hx.reset()

#Scale ratio used for calibration
SCALE_RATIO = -370

hx.set_scale_ratio(SCALE_RATIO)
err = hx.zero()
if err:
    raise ValueError("Zeroing was unsuccessful")

#Set mail detection threshold in grams
THRESHOLD_GRAMS = 25

#Track last state to detect changes
last_state = False

#Read weight from HX711
def get_weight():
    weight = hx.get_weight_mean(20)
    if weight is False:
        raise RuntimeError("HX711 reading failed")
    return abs(weight)

#Start Gmail API and handle authentication
def start_gmail_api():
    creds = None

    #Check if token.json exists for stored credentials
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    #If no valid credentials, start authentication flow
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

#Send email using Gmail API
def send_email(service, to_email, weight, content, status):
    message = EmailMessage()
    message["To"] = to_email
    message["From"] = "me"
    message["Subject"] = f"Mailbox Alert: {status}"
    message.set_content(
        f"{content}\n\nMeasured weight: {weight:.2f}g"
    )

    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode("utf-8")

    request_body = {"raw": encoded_message}

    return (
        service.users()
        .messages()
        .send(userId="me", body=request_body)
        .execute()
    )

#Set up CSV for logging results
df = pd.DataFrame(columns=["Total time taken (s)", "Weight (g)", "Status"])
df.to_csv("output.csv", index=True)

#Log results to previously created CSV
def csv_setup(total_time, weight, status):
    row = pd.DataFrame([[total_time, weight, status]], columns=["Total time taken (s)", "Weight (g)", "Status"])
    row.to_csv("output.csv", mode="a", header=False, index=True)

def main():
    global last_state
    #Set recipient email address
    #recipient = input("Enter the email address to receive alerts: ").strip()
    recipient = "mailboxdetection@gmail.com"
    service = start_gmail_api()

    print("Monitoring for new mail...")

    mail_removed = False

    while True:
        #Get current weight
        weight = get_weight()
        mail_present = weight >= THRESHOLD_GRAMS

        print(f"Weight: {weight:.2f} g")
        #Check if mail is detected and it was not present in the last state
        if mail_present and not last_state:

            #Start timer to measure email sending time
            start = time.perf_counter()

            #Define email contents, status, and time to send then log
            content = "New mail detected in the mailbox!"
            status = "Mail Detected"
            result = send_email(service, recipient, weight, content, status)
            print(f"Email sent successfully.\n\n{result}")
            end = time.perf_counter()
            total_time = end - start
            csv_setup(total_time, weight, status)
            print(f"Time taken to send email: {total_time:.2f} seconds")
        
        if weight >= THRESHOLD_GRAMS:
            mail_removed = True

        #Check for removal of mail then log
        if mail_removed and weight < THRESHOLD_GRAMS:
            content = "Mail removed from mailbox!"
            status = "Mail Removed"
            result = send_email(service, recipient, weight, content, status)
            mail_removed = False
            csv_setup(total_time, weight, status)
            print(f"Email sent successfully.\n\n{result}")

        last_state = mail_present

        time.sleep(2)

if __name__ == "__main__":
    try:
        main()
    finally:
        GPIO.cleanup()