import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from datetime import datetime
import constants

# Authenticate with Gmail API using OAuth
def authenticate_with_gmail():
    print('Authenticating')
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", constants.SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                constants.CREDS_FILE, constants.SCOPES
            )
            creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
        token.write(creds.to_json())
    service = build("gmail", "v1", credentials=creds)
    print('Authenticated successfully\n')
    return service

# Fetch emails from Gmail Inbox
def fetch_emails(service):
    print('Getting emails')
    parsed_emails = []
    try:
        results = service.users().messages().list(userId="me").execute()
        messages = results.get("messages", [])
        if not messages:
            print("No emails found.")
            return
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            payload = msg['payload']
            headers = payload['headers']
            email_data = {
                'id': msg['id'],
                'sender': next(h['value'] for h in headers if h['name'] == 'From'),
                'recipient': next(h['value'] for h in headers if h['name'] == 'To'),
                'subject': next(h['value'] for h in headers if h['name'] == 'Subject'),
                'body': msg.get('snippet', ''),
                'received_at': datetime.fromtimestamp(float(msg['internalDate']) / 1000.0),
                'labels': msg['labelIds']
            }
            parsed_emails.append(email_data)
    except HttpError as error:
        print(f"An error occurred: {error}")
    print(f'Got {len(parsed_emails)} emails successfully\n')
    return parsed_emails

# Mark email as read or unread in the Gmail Inbox
def mark_email_in_gmail(service, email_id, value):
    print(f"Marking email {email_id} as {value} in gmail")
    try:
        if value.upper() == 'READ':
            service.users().messages().modify(userId='me', id=email_id, body={'removeLabelIds': ['UNREAD']}).execute()
        elif value.upper() == 'UNREAD':
            service.users().messages().modify(userId='me', id=email_id, body={'addLabelIds': ['UNREAD']}).execute()
        print(f"Marked email {email_id} as {value} successfully in gmail\n")
    except Exception as e:
        print(f"Error email {email_id} as {value}: {e}")


# Create a new lable in Gmail
def create_label(service, label_name):
    label = {'name': label_name}
    try:
        created_label = service.users().labels().create(userId='me', body=label).execute()
        return created_label
    except Exception as e:
        print(f"Error creating label: {e}")
        return None

# Add label to an email in Gmail
def add_label_to_email(service, email_id, label_name):
    print(f"Adding label {label_name} to email {email_id}")
    # Check if label exists
    labels = service.users().labels().list(userId='me').execute().get('labels', [])
    label_ids = [label['id'] for label in labels if label['name'] == label_name]
    
    if not label_ids:
        created_label = create_label(service, label_name)
        if created_label:
            label_id = created_label['id']
        else:
            return

    else:
        label_id = label_ids[0]
    
    # Add label to email
    try:
        service.users().messages().modify(userId='me', id=email_id, body={'addLabelIds': [label_id]}).execute()
        print(f"Added label '{label_name}' to email {email_id}")
    except Exception as e:
        print(f"Error adding label to email {email_id}: {e}")

# Change labels for email in the Gmail Inbox
def move_email_in_gmail(service, email_id, label):
    print(f"Moving email {email_id} to {label} in gmail")
    try:
        service.users().messages().modify(userId='me', id=email_id, body={'addLabelIds': [label]}).execute()
        print(f"Moved email {email_id} to {label} successfully\n")
    except Exception as e:
        print(f"Error moving email {email_id} to {label}: {e}")

