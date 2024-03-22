import psycopg2
import json
import constants
import dbutils
import gmailutils

# Load rules from JSON file
def load_rules_from_json(file_path):
    print('Loading rules')
    with open(file_path, 'r') as file:
        rules_json = json.load(file)
    print('Loaded rules successfully\n')
    return rules_json

# Create and run SELECT query for each rule and perform actions
def process_rules(service, cursor, rules):
    print('Processing rules')
    for rule in rules:
        select_query = generate_select_query(rule)
        cursor.execute(select_query)
        rows = cursor.fetchall()
        actions = rule.get('actions', [])
        for row in rows:
            print(row)
            apply_actions(service, cursor, row, actions)
    print('Processed rules successfully\n')

# Generate SELECT query based on rule conditions and predicate for each rule
def generate_select_query(rule):
    print(f'Generating select_query for {rule}')
    select_fields = set()
    where_conditions = []
    conditions = rule['conditions']
    rule_conditions = []
    field_map = {
        'From' : 'sender',
        'To' : 'recipient'
    }

    for condition in conditions:
        field_name = condition['field']
        field_name = field_map.get(field_name, field_name)
        select_fields.add(field_name)
        predicate = condition['predicate']
        value = condition['value']
        rule_conditions.append(generate_where_condition(field_name, predicate, value))
    
    rule_combination = rule.get('predicate', 'any')
    if rule_combination == 'any':
        where_conditions.append('(' + ' OR '.join(rule_conditions) + ')')
    elif rule_combination == 'all':
        where_conditions.append('(' + ' AND '.join(rule_conditions) + ')')

    select_fields_with_id = ['id'] + list(select_fields)
    select_query = f"SELECT {', '.join(select_fields_with_id)} FROM {constants.TABLE_NAME}"
    if where_conditions:
        select_query += " WHERE " + " AND ".join(where_conditions)
    print(f'Generated {select_query}\n')
    return select_query

# Convert rules json condition to psql condition
def generate_where_condition(field_name, predicate, value):
    if predicate == 'contains':
        return f"{field_name} LIKE '%{value}%'"
    elif predicate == 'not_contains':
        return f"{field_name} NOT LIKE '%{value}%'"
    elif predicate == 'equals':
        return f"{field_name} = '{value}'"
    elif predicate == 'not_equals':
        return f"{field_name} != '{value}'"
    elif predicate == 'less_than' and field_name == 'received_at':
        return f"{field_name} >= CURRENT_DATE - INTERVAL '{value}'"
    elif predicate == 'greater_than' and field_name == 'received_at':
        return f"{field_name} < CURRENT_DATE - INTERVAL '{value}'"

# Apply mark or move actions to emails in both db and gmail        
def apply_actions(service, cursor, row, actions):
    email_id = row[0]
    print(f"Applying actions for {email_id}")
    for action in actions:
        action_type = action['type']
        action_value = action['value']
        if action_type == 'mark':
            # dbutils.mark_email_in_db(cursor, email_id, action_value)
            gmailutils.mark_email_in_gmail(service, email_id, action_value)
        elif action_type == 'move':
            # dbutils.move_email_in_db(cursor, email_id, action_value)
            gmailutils.add_label_to_email(service, email_id, action_value)
    print(f"Applied actions for {email_id} successfully\n")
