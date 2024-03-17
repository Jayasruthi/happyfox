import unittest
from unittest.mock import MagicMock, patch
import json
import getemails, processrules

class TestEmailProcessing(unittest.TestCase):
    def setUp(self):
        # Mocking email data
        self.mock_emails = [
            {
                'id': '123456789',
                'sender': 'sender@example.com',
                'recipient': 'recipient@example.com',
                'subject': 'Test Subject',
                'body': 'Test Body',
                'received_at': '2024-03-15 10:00:00',
                'labels': ['UNREAD', 'INBOX']
            },
            # Add more mock emails as needed
        ]

        # Mocking PostgreSQL cursor
        self.mock_cursor = MagicMock()

        # Create a mock connection object and attach it to the mock cursor
        self.mock_connection = MagicMock()
        self.mock_cursor.connection = self.mock_connection

    @patch('getemails.authenticate_with_gmail')
    def test_fetch_emails(self, mock_fetch_emails):
        # Mocking fetch_emails_from_gmail function
        mock_fetch_emails.return_value = self.mock_emails

        # Call the function to fetch emails
        emails = getemails.authenticate_with_gmail()

        # Assert that the correct number of emails is fetched
        self.assertEqual(len(emails), len(self.mock_emails))

        # Assert that the fetched emails match the mock emails
        self.assertListEqual(emails, self.mock_emails)

    def test_store_emails_in_postgres(self):
        # Call the function to store emails in PostgreSQL
        getemails.store_emails_in_database(self.mock_cursor, self.mock_emails)

        # Assert that the execute method is called for each email
        self.assertEqual(self.mock_cursor.execute.call_count, len(self.mock_emails))

        # Assert that the commit method is called once
        self.mock_cursor.connection.commit.assert_called_once()


if __name__ == '__main__':
    unittest.main()
