# Create Group Admins

The group admin bulk operation allows you to create multiple group administrators efficiently using either CSV files or direct method calls.

## Description

Group admin creation enables you to set up individual group administrator accounts with various configurations including personal information and authentication details. This bulk operation creates multiple group administrators with their associated configuration in a single operation, supporting both CSV-based and programmatic approaches.

## Create from CSV

### Setup

1. **Get the template**: Find the bulk sheet template at [`group.admin.create.csv`](https://github.com/Fourteen-IP/mercury-ocip/tree/main/assets/bulk%20sheets)
2. **Fill in your data**: Use the template to define your group administrators

### CSV Format

The CSV template includes these columns:

| Column | Description | Required | Example |
|--------|-------------|----------|---------|
| `operation` | Operation type | Yes | `group.admin.create` |
| `serviceProviderId` | Service provider identifier | Yes | `"MyServiceProvider"` |
| `groupId` | Group identifier | Yes | `"SalesGroup"` |
| `userId` | Group administrator user identifier | Yes | `"admin@company.com"` |
| `firstName` | Administrator's first name | No | `"John"` |
| `lastName` | Administrator's last name | No | `"Doe"` |
| `password` | Administrator password | No | `"password123"` |
| `language` | Language | No | `"English"` |

### Defaults

To make group admin creation more user-friendly, many fields have sensible defaults that will be automatically applied if you don't specify them. This means you only need to provide the essential information, and the system will handle the rest.

**Group Admin Profile Defaults:**
- No defaults are currently configured for group admin creation
- All required fields must be explicitly provided

**Benefits of Explicit Configuration:**
- **Clear requirements**: You know exactly what information is needed
- **Flexible setup**: Configure only what you need for your specific use case
- **Consistent behaviour**: Explicit configuration ensures predictable admin setup across your organisation
- **Easy migration**: Existing group administrators can be recreated with their exact configuration

**Example - Minimal CSV:**
```csv
operation,serviceProviderId,groupId,userId,firstName,lastName,password,language
group.admin.create,MyServiceProvider,SalesGroup,admin@company.com,John,Doe,password123,English
```

This minimal example will create a group administrator with all required fields specified.

### Example CSV Data

```csv
operation,serviceProviderId,groupId,userId,firstName,lastName,password,language
group.admin.create,MyServiceProvider,SalesGroup,admin1@company.com,John,Doe,password123,English
group.admin.create,MyServiceProvider,SalesGroup,admin2@company.com,Jane,Smith,password456,English
```

### Usage

```python
from mercury_ocip import Client, Agent

# Initialize client
client = Client(
    host="your-broadworks-server.com",
    username="your-username",
    password="your-password"
)

# Get agent instance
agent = Agent.get_instance(client)

# Create group admins from CSV
results = agent.bulk.create_group_admin_from_csv(
    csv_path="path/to/your/group_admins.csv",
    dry_run=False  # Set to True to validate without creating
)

# Process results
for result in results:
    if result["success"]:
        print(f"✅ Created group admin: {result['data']['user_id']}")
    else:
        print(f"❌ Failed to create group admin: {result.get('response', 'Unknown error')}")
```

## Create from Data (Method Call in IDE)

> **Note:** This is a highlighted note
> When creating group administrators programmatically, you can omit any optional fields, but all required fields must be explicitly provided. The system will validate all required fields before processing.

When creating group administrators programmatically, you can omit any optional fields, but all required fields must be explicitly provided. The system will validate all required fields before processing.

For programmatic creation without CSV files:

```python
from mercury_ocip import Client, Agent

# Initialize client
client = Client(
    host="your-broadworks-server.com",
    username="your-username", 
    password="your-password"
)

# Get agent instance
agent = Agent.get_instance(client)

# Define group admin data
group_admin_data = [
    {
        "operation": "group.admin.create",
        "service_provider_id": "MyServiceProvider",
        "group_id": "SalesGroup",
        "user_id": "admin1@company.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "password123",
        "language": "English"
    },
    {
        "operation": "group.admin.create",
        "service_provider_id": "MyServiceProvider",
        "group_id": "SalesGroup",
        "user_id": "admin2@company.com",
        "first_name": "Jane",
        "last_name": "Smith",
        "password": "password456",
        "language": "English"
    }
]

# Create group admins from data
results = agent.bulk.create_group_admin_from_data(
    group_admin_data=group_admin_data,
    dry_run=False  # Set to True to validate without creating
)

# Process results
for result in results:
    if result["success"]:
        print(f"✅ Created group admin: {result['data']['user_id']}")
    else:
        print(f"❌ Failed to create group admin: {result.get('response', 'Unknown error')}")
```

## Dry Run Mode

Both methods support dry run mode for validation:

```python
# Validate data without creating group admins
results = agent.bulk.create_group_admin_from_csv(
    csv_path="path/to/your/group_admins.csv",
    dry_run=True
)
```

Dry run mode will:
- Parse and validate your data
- Check for required fields and data types
- Return validation results without making actual API calls

## Response Format

Both methods return a list of result dictionaries:

```python
[
    {
        "index": 0,
        "data": {...},  # Original data for this group admin
        "command": {...},  # Generated command object
        "response": "",  # API response (empty for dry run, error details if failed)
        "success": True,  # Whether the operation succeeded
        "detail": None  # Additional error details if failed
    },
    # ... more results
]
```

## Error Handling

The operation handles various error scenarios:

- **Validation errors**: Invalid data types or missing required fields
- **API errors**: BroadWorks server errors (duplicate admins, invalid groups, etc.)
- **Network errors**: Connection issues

Check the `success` field and `response` field in results for detailed error information. When `success` is `False`, the `response` field will contain the error details.

## Notes

- **Template location**: Find the bulk sheet template in [`group.admin.create.csv`](https://github.com/Fourteen-IP/mercury-ocip/tree/main/assets/bulk%20sheets)
- **Case conversion**: Column names are automatically converted from camelCase to snake_case
- **Required fields**: All required fields must be explicitly provided as no defaults are configured

