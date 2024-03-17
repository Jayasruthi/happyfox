USERNAME = "jayasruthivr"
PASSWORD = "postgres"
HOST = "localhost"
PORT = "5432"
DB_NAME = "jayasruthivr"
DB_URL = f"postgres://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"
TABLE_NAME = "emails"

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CREDS_FILE = "credentials.json"

RULES_FILE = "rules.json"
