# Create Call Pickup Groups

The call pickup groups bulk operation allows you to create multiple call pickup groups efficiently using either CSV files or direct method calls.

## Description

Call pickup groups enable users to answer calls for other users in their group. This bulk operation creates multiple pickup groups with their associated users in a single operation, supporting both CSV-based and programmatic approaches.

## Create from CSV

### Setup

1. **Get the template**: Find the bulk sheet template at [`pickup.group.create.csv`](https://github.com/Fourteen-IP/mercury-ocip/tree/main/assets/bulk%20sheets)
2. **Fill in your data**: Use the template to define your call pickup groups

### CSV Format

The CSV template includes these columns:

| Column | Description | Required | Example |
|--------|-------------|----------|---------|
| `operation` | Operation type | Yes | `pickup.group.create` |
| `serviceProviderId` | Service provider identifier | Yes | `"MyServiceProvider"` |
| `groupId` | Group identifier | Yes | `"SalesGroup"` |
| `name` | Pickup group name | Yes | `"Sales Pickup Group"` |
| `userId[0]` | First user ID | Yes | `"user1@domain.com"` |
| `userId[1]` | Second user ID | No | `"user2@domain.com"` |
| `userId[2]` | Third user ID | No | `"user3@domain.com"` |
| ... | Additional users | No | `"userN@domain.com"` |

### Array Notation

The `userId[0]`, `userId[1]`, etc. notation allows you to specify multiple users in a single pickup group. You can include as many `userId[N]` columns as needed, but it's recommended to only include the number of columns you actually need to avoid empty columns.

### Example CSV Data

```csv
operation,serviceProviderId,groupId,name,userId[0],userId[1],userId[2]
pickup.group.create,MyServiceProvider,SalesGroup,Sales Pickup Group,john.doe@company.com,jane.smith@company.com,bob.wilson@company.com
pickup.group.create,MyServiceProvider,SupportGroup,Support Pickup Group,support1@company.com,support2@company.com,
```

### Usage

```python
from broadworks_sdk import Client, Agent

# Initialize client
client = Client(
    host="your-broadworks-server.com",
    username="your-username",
    password="your-password"
)

# Get agent instance
agent = Agent.get_instance(client)

# Create pickup groups from CSV
results = agent.bulk.create_call_pickup_from_csv(
    csv_path="path/to/your/pickup_groups.csv",
    dry_run=False  # Set to True to validate without creating
)

# Process results
for result in results:
    if result["success"]:
        print(f"✅ Created pickup group: {result['data']['name']}")
    else:
        print(f"❌ Failed to create pickup group: {result.get('error', 'Unknown error')}")
```

## Create from Data (Method Call in IDE)

For programmatic creation without CSV files:

```python
from broadworks_sdk import Client, Agent

# Initialize client
client = Client(
    host="your-broadworks-server.com",
    username="your-username", 
    password="your-password"
)

# Get agent instance
agent = Agent.get_instance(client)

# Define pickup group data
pickup_groups_data = [
    {
        "operation": "pickup.group.create",
        "serviceProviderId": "MyServiceProvider",
        "groupId": "SalesGroup", 
        "name": "Sales Pickup Group",
        "userId": [
            "john.doe@company.com",
            "jane.smith@company.com", 
            "bob.wilson@company.com"
        ]
    },
    {
        "operation": "pickup.group.create",
        "serviceProviderId": "MyServiceProvider",
        "groupId": "SupportGroup",
        "name": "Support Pickup Group", 
        "userId": [
            "support1@company.com",
            "support2@company.com"
        ]
    }
]

# Create pickup groups from data
results = agent.bulk.create_call_pickup_from_data(
    call_pickup_data=pickup_groups_data,
    dry_run=False  # Set to True to validate without creating
)

# Process results
for result in results:
    if result["success"]:
        print(f"✅ Created pickup group: {result['data']['name']}")
    else:
        print(f"❌ Failed to create pickup group: {result.get('error', 'Unknown error')}")
```

## Dry Run Mode

Both methods support dry run mode for validation:

```python
# Validate data without creating pickup groups
results = agent.bulk.create_call_pickup_from_csv(
    csv_path="path/to/your/pickup_groups.csv",
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
        "data": {...},  # Original data for this pickup group
        "command": {...},  # Generated command object
        "response": "",  # API response (empty for dry run)
        "success": True,  # Whether the operation succeeded
        "error": None  # Error message if failed
    },
    # ... more results
]
```

## Error Handling

The operation handles various error scenarios:

- **Validation errors**: Invalid data types or missing required fields
- **API errors**: BroadWorks server errors (duplicate groups, invalid users, etc.)
- **Network errors**: Connection issues

Check the `success` field and `error` message in results for detailed error information.

## Notes

- **User ID arrays**: The `userId[0]`, `userId[1]` notation can handle as many users as needed, but it's best practice to only include the number of columns you actually need
- **Template location**: Find the bulk sheet template in [`pickup.group.create.csv`](https://github.com/Fourteen-IP/mercury-ocip/tree/main/assets/bulk%20sheets)
- **Case conversion**: Column names are automatically converted from camelCase to snake_case
- **Empty values**: Empty `userId[N]` columns are automatically filtered out