import dbutils
import gmailutils
import ruleprocessor
import constants
import psycopg2

if __name__ == "__main__":
    conn = psycopg2.connect(constants.DB_URL)
    cursor = conn.cursor()
    gmail_service = gmailutils.authenticate_with_gmail()
    fetched_emails = gmailutils.fetch_emails(gmail_service)
    dbutils.create_table(cursor)
    dbutils.store_emails_in_database(cursor, fetched_emails)
    rules = ruleprocessor.load_rules_from_json(constants.RULES_FILE)
    ruleprocessor.process_rules(gmail_service, cursor, rules)
    conn.close()