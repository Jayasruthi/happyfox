import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import psycopg2
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

# Create table to store email data
def create_table(cursor):
    print('Creating table')
    try:
        command = f"""CREATE TABLE IF NOT EXISTS {constants.TABLE_NAME} (
            id TEXT PRIMARY KEY,
            sender TEXT,
            recipient TEXT,
            subject TEXT,
            body TEXT,
            received_at TIMESTAMP,
            labels TEXT[]
        )"""
        cursor.execute(command)
        cursor.connection.commit()
    except psycopg2.Error as error:
        print(f"An error occurred: {error}")
    print('Table created successfully\n')

# Store fetched emails into the database
def store_emails_in_database(cursor, emails):
    print('Storing emails')
    rows_count = 0;
    for email_data in emails:
        try:
            cursor.execute("""INSERT INTO {} (id, sender, recipient, subject, body, received_at, labels)
                VALUES (%s, %s, %s, %s, %s, %s, %s)""".format(constants.TABLE_NAME),
                (email_data['id'], email_data['sender'], email_data['recipient'],
                email_data['subject'], email_data['body'], email_data['received_at'],
                email_data['labels']))
            rows_count += 1
            cursor.connection.commit()
        except psycopg2.Error as error:
            print(f"An error occurred while inserting row {email_data['id']}: {error}")
            cursor.connection.rollback()
            continue
    print(f'Stored {rows_count} emails successfully\n')

if __name__ == "__main__":
    conn = psycopg2.connect(constants.DB_URL)
    cursor = conn.cursor()
    gmail_service = authenticate_with_gmail()
    fetched_emails = fetch_emails(gmail_service)
    create_table(cursor)
    store_emails_in_database(cursor, fetched_emails)
    conn.close()

