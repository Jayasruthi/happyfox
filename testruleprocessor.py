import unittest
from unittest.mock import MagicMock, patch
from happyfox2 import generate_select_query, process_rules, apply_actions

# Define a mock cursor class for testing purposes
class MockCursor:
    def __init__(self):
        self.executed_queries = []

    def execute(self, query):
        self.executed_queries.append(query)

    def fetchall(self):
        return [{'id': 1, 'sender': 'test@example.com', 'recipient': 'user@example.com'}]

class TestRuleProcessor(unittest.TestCase):
    def test_generate_select_query(self):
        rule = {
            'conditions': [
                {'field': 'To', 'predicate': 'contains', 'value': 'example.com'}
            ]
        }
        expected_query = "SELECT recipient FROM emails WHERE (recipient CONTAINS 'example.com')"
        actual_query = generate_select_query(rule)
        self.assertEqual(actual_query, expected_query)

    def test_process_rules(self):
        cursor = MockCursor()
        mock_connection = MagicMock()
        cursor.connection = mock_connection

        rules = [
            {
                'conditions': [
                    {'field': 'To', 'predicate': 'contains', 'value': 'example.com'}
                ],
                'actions': [
                    {'type': 'mark', 'value': 'unread'}
                ]
            }
        ]
        process_rules(cursor, rules)
        self.assertEqual(len(cursor.executed_queries), 2)  

    def test_apply_actions(self):
        cursor = MockCursor()
        mock_connection = MagicMock()
        cursor.connection = mock_connection
        row = {'id': 1, 'sender': 'test@example.com', 'recipient': 'user@example.com', 'labels': ['READ']}
        actions = [
            {'type': 'mark', 'value': 'unread'}
        ]
        apply_actions(cursor, row, actions)
        self.assertEqual(len(cursor.executed_queries), 1)  # Ensure only one UPDATE query was executed

if __name__ == '__main__':
    unittest.main()
