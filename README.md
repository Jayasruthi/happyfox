## About
This project consists of simple scripts to fetch emails using the Gmail API, store them in a PostgreSQL database, and run rules on the stored emails.

## Prerequisites
### Gmail Client Setup
To use the Gmail API, you need to set up a Gmail API client. Follow the [instructions provided by Google](https://developers.google.com/gmail/api/quickstart/python) to create a new project in the Google Cloud Console, enable the Gmail API, and create credentials (OAuth 2.0 client ID) for your project. Save the credentials file (`credentials.json`) to your project directory.

### PostgreSQL Setup
Ensure that you have PostgreSQL installed on your system or [set up a PostgreSQL database](https://www.postgresqltutorial.com/postgresql-getting-started/install-postgresql-macos/) instance. Create a new database and configure access credentials (username, password). Update the database connection details (host, port, database name, username, password) in `constants.py`.

### Rules Setup
Define the rules for processing emails in a JSON file. The file should have a list of rules, each rule should have a set of conditions with an overall predicate and a set of actions. See the provided example rules file for reference.
The following rule formats are supported:
  * Fields: From, To, Subject, Body, Received_At
  * Predicates: Contains, Not Contains, Equals, Not Equals, Less than n days, Greater than n days
  * Actions: Mark as read or unread, Move to a specific folder

Rules are run in sequential order. Later rules override results of previous rules.

## Execution
* Clone or download the project repository to your local machine.
* Set up the Gmail API client and save `credentials.json` to your project directory.
* Configure the PostgreSQL connection details in `constants.py`.
* Define rules for processing emails in a file, and update the path in constants.py.
* Run `python3 processemails.py`. You will be prompted to login with Gmail when running the script for the first time.
* Verify database and table was created in PSQL console. You can configure the table name in constants.py
* Check logs and Gmail console to verify rules were applied correctly.

## Implementation
### gmailutils.py
* Configurable constants for Gmail authentication, PostgreSQL connection, and Table creation
* Fetches the first 100 emails in modify mode
* Handles new label creation, marking emails as read or unread, and applying labels
### ruleprocessor.py
* Optimized select query generation based on conditions and predicates instead running every rule on all emails
* Handles mapping for field names to column names, and converts conditions to correct PSQL syntax
### dbutils.py
* Contains all functions to perform database operations – table creation and storing emails in the table
* Gracefully handles errors during table row creation
### processemails.py
* Main script that uses above three scripts to fetch emails, store in database and apply actions to emails based on rules
 
## Future Work
* Improve error handling such as adding a validation checker for rules.json
* Enhance rule engine to support more complex conditions and actions
* Implement scheduling and automation for periodic email fetching and processing
* Improve test coverage
