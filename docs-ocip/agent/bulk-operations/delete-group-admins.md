# Delete Group Admins

The group admin bulk operation allows you to delete multiple group administrators efficiently using either CSV files or direct method calls.

## Description

Group admin deletion enables you to remove individual group administrator accounts from the system. This bulk operation deletes multiple group administrators in a single operation, supporting both CSV-based and programmatic approaches.

## Delete from CSV

### Setup

1. **Get the template**: Find the bulk sheet template at [`group.admin.delete.csv`](https://github.com/Fourteen-IP/mercury-ocip/tree/main/assets/bulk%20sheets)
2. **Fill in your data**: Use the template to define which group administrators to delete

### CSV Format

The CSV template includes these columns:

| Column | Description | Required | Example |
|--------|-------------|----------|---------|
| `operation` | Operation type | Yes | `group.admin.delete` |
| `userId` | Group administrator user identifier | Yes | `"admin@company.com"` |

### Defaults

To make group admin deletion more user-friendly, many fields have sensible defaults that will be automatically applied if you don't specify them. This means you only need to provide the essential information, and the system will handle the rest.

**Group Admin Deletion Defaults:**
- No defaults are currently configured for group admin deletion
- All required fields must be explicitly provided

**Benefits of Explicit Configuration:**
- **Clear requirements**: You know exactly what information is needed
- **Flexible setup**: Configure only what you need for your specific use case
- **Consistent behaviour**: Explicit configuration ensures predictable admin deletion across your organisation
- **Easy migration**: Group administrators can be deleted with their exact identifier

**Example - Minimal CSV:**
```csv
operation,userId
group.admin.delete,admin@company.com
```

This minimal example will delete a group administrator with all required fields specified.

### Example CSV Data

```csv
operation,userId
group.admin.delete,admin1@company.com
group.admin.delete,admin2@company.com
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

# Delete group admins from CSV
results = agent.bulk.delete_group_admin_from_csv(
    csv_path="path/to/your/group_admins.csv",
    dry_run=False  # Set to True to validate without deleting
)

# Process results
for result in results:
    if result["success"]:
        print(f"✅ Deleted group admin: {result['data']['user_id']}")
    else:
        print(f"❌ Failed to delete group admin: {result.get('response', 'Unknown error')}")
```

## Delete from Data (Method Call in IDE)

> **Note:** This is a highlighted note
> When deleting group administrators programmatically, you can omit any optional fields, but all required fields must be explicitly provided. The system will validate all required fields before processing.

When deleting group administrators programmatically, you can omit any optional fields, but all required fields must be explicitly provided. The system will validate all required fields before processing.

For programmatic deletion without CSV files:

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
        "operation": "group.admin.delete",
        "user_id": "admin1@company.com"
    },
    {
        "operation": "group.admin.delete",
        "user_id": "admin2@company.com"
    }
]

# Delete group admins from data
results = agent.bulk.delete_group_admin_from_data(
    group_admin_data=group_admin_data,
    dry_run=False  # Set to True to validate without deleting
)

# Process results
for result in results:
    if result["success"]:
        print(f"✅ Deleted group admin: {result['data']['user_id']}")
    else:
        print(f"❌ Failed to delete group admin: {result.get('response', 'Unknown error')}")
```

## Dry Run Mode

Both methods support dry run mode for validation:

```python
# Validate data without deleting group admins
results = agent.bulk.delete_group_admin_from_csv(
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
- **API errors**: BroadWorks server errors (non-existent admins, invalid users, etc.)
- **Network errors**: Connection issues

Check the `success` field and `response` field in results for detailed error information. When `success` is `False`, the `response` field will contain the error details.

## Notes

- **Template location**: Find the bulk sheet template in [`group.admin.delete.csv`](https://github.com/Fourteen-IP/mercury-ocip/tree/main/assets/bulk%20sheets)
- **Case conversion**: Column names are automatically converted from camelCase to snake_case
- **Required fields**: All required fields must be explicitly provided as no defaults are configured

