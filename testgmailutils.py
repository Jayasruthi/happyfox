import unittest
from unittest.mock import MagicMock, patch, ANY
import os

# Import functions to be tested
from gmailutils import (
    authenticate_with_gmail,
    fetch_emails,
    mark_email_in_gmail,
    create_label,
    add_label_to_email,
    move_email_in_gmail
)

# Define a test class
class TestEmailProcessing(unittest.TestCase):

    # Test fetch_emails function
    @patch('googleapiclient.discovery.build')
    def test_fetch_emails(self, mock_build):
        # Mock service
        mock_service = MagicMock()
        mock_service.users().messages().list().execute.return_value = {'messages': [{'id': '123', 'labelIds': ['INBOX']}]}
        mock_service.users().messages().get().execute.return_value = {
            'id': '123',
            'snippet': 'Test email',
            'payload': {'headers': [{'name': 'From', 'value': 'test@example.com'},{'name': 'To', 'value': 'testto@example.com'},{'name': 'Subject', 'value': 'Test'}]},
            'received_at': '2024-03-15 10:00:00',
            'internalDate' : 123456,
            'labelIds' : ['INBOX']

        }
        mock_build.return_value = mock_service
        
        # Call the function
        emails = fetch_emails(mock_service)
        
        # Assertions
        self.assertEqual(len(emails), 1)
        self.assertEqual(emails[0]['id'], '123')

    # Test mark_email_in_gmail function
    @patch('googleapiclient.discovery.build')
    def test_mark_email_in_gmail(self, mock_build):
        # Mock service
        mock_service = MagicMock()
        
        # Call the function
        mark_email_in_gmail(mock_service, '123', 'READ')
        
        # Assertions
        mock_service.users().messages().modify.assert_called_once_with(userId='me', id='123', body={'removeLabelIds': ['UNREAD']})

    # Test create_label function
    @patch('googleapiclient.discovery.build')
    def test_create_label(self, mock_build):
        # Mock service
        mock_service = MagicMock()
        mock_service.users().labels().create.return_value.execute.return_value = {'id': 'label-id'}
        
        # Call the function
        label = create_label(mock_service, 'TestLabel')
        
        # Assertions
        self.assertEqual(label['id'], 'label-id')

    # Test add_label_to_email function
    @patch('googleapiclient.discovery.build')
    def test_add_label_to_email(self, mock_build):
        # Mock service
        mock_service = MagicMock()
        
        # Call the function
        add_label_to_email(mock_service, '123', 'TestLabel')
        
        # Assertions
        mock_service.users().messages().modify.assert_called_once_with(userId='me', id='123', body=ANY)

    # Test move_email_in_gmail function
    @patch('googleapiclient.discovery.build')
    def test_move_email_in_gmail(self, mock_build):
        # Mock service
        mock_service = MagicMock()
        
        # Call the function
        move_email_in_gmail(mock_service, '123', 'TestLabel')
        
        # Assertions
        mock_service.users().messages().modify.assert_called_once_with(userId='me', id='123', body={'addLabelIds': ['TestLabel']})

# Define main function to run tests
if __name__ == '__main__':
    unittest.main()
