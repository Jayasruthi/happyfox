import psycopg2
import constants

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

# Update email row as read or unread in the database
def mark_email_in_db(cursor, email_id, value):
    print(f"Marking email {email_id} as {value} in db")
    try:
        if value.upper() == 'READ':
            cursor.execute(f"UPDATE {constants.TABLE_NAME} SET labels = array_remove(labels, 'UNREAD') WHERE id = '{email_id}'")
        elif value.upper() == 'UNREAD':
            cursor.execute(f"UPDATE {constants.TABLE_NAME} SET labels = array_append(labels, 'UNREAD') WHERE id = '{email_id}'")
        cursor.connection.commit()
    except psycopg2.Error as error:
        print(f"An error occurred while updating row {email_id}: {error}")
    print(f"Marked email {email_id} as {value} in db successfully\n")

# Update labels for email row in the database
def move_email_in_db(cursor, email_id, value):
    print(f"Moving email {email_id} to {value} in db")
    try:
        cursor.execute(f"UPDATE {constants.TABLE_NAME} SET labels = array_append(labels, '{value}') WHERE id = '{email_id}'")
        cursor.connection.commit()
    except psycopg2.Error as error:
        print(f"An error occurred while updating row {email_id}: {error}")
    print(f"Moved email {email_id} to {value} in db successfully\n")


