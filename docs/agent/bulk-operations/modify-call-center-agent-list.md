# Modify Call Center Agent List

The call center agent list modification operation allows you to update the agents assigned to existing call centers efficiently using either CSV files or direct method calls.

## Description

Call center agent list modification enables you to add, remove, or replace agents in existing call centers. This bulk operation updates multiple call centers' agent assignments in a single operation, supporting both CSV-based and programmatic approaches.

## Modify from CSV

### Setup

1. **Get the template**: Find the bulk sheet template at [`call.center.modify.agent.list.csv`](https://github.com/Fourteen-IP/mercury-ocip/tree/main/assets/bulk%20sheets)
2. **Fill in your data**: Use the template to define your agent list modifications

### CSV Format

The CSV template includes these columns:

| Column | Description | Required | Example |
|--------|-------------|----------|---------|
| `operation` | Operation type | Yes | `call.center.update.agent.list` |
| `serviceUserId` | Call center service user ID | Yes | `"sales-center@domain.com"` |
| `agentUserIdList.userId[0]` | First agent user ID | No | `"agent1@domain.com"` |
| `agentUserIdList.userId[1]` | Second agent user ID | No | `"agent2@domain.com"` |
| `agentUserIdList.userId[2]` | Third agent user ID | No | `"agent3@domain.com"` |
| `agentUserIdList.userId[3]` | Fourth agent user ID | No | `"agent4@domain.com"` |
| `agentUserIdList.userId[4]` | Fifth agent user ID | No | `"agent5@domain.com"` |
| `agentUserIdList.userId[5]` | Sixth agent user ID | No | `"agent6@domain.com"` |
| `agentUserIdList.userId[6]` | Seventh agent user ID | No | `"agent7@domain.com"` |
| `agentUserIdList.userId[7]` | Eighth agent user ID | No | `"agent8@domain.com"` |

### Important Notes

- **Replacement Operation**: This operation **completely replaces** the existing agent list with the new list provided
- **Empty Lists**: If you provide an empty list (all `agentUserIdList.userId[N]` fields empty), all agents will be removed from the call center
- **Agent Requirements**: All specified agents must exist and be valid users in the system
- **Call Center Must Exist**: The call center specified by `serviceUserId` must already exist

### Array Notation

The `agentUserIdList.userId[0]`, `agentUserIdList.userId[1]`, etc. notation allows you to specify multiple agents for a call center. You can include as many `userId[N]` columns as needed, but it's recommended to only include the number of columns you actually need to avoid empty columns.

### Example CSV Data

```csv
operation,serviceUserId,agentUserIdList.userId[0],agentUserIdList.userId[1],agentUserIdList.userId[2],agentUserIdList.userId[3]
call.center.update.agent.list,sales-center@company.com,john.doe@company.com,jane.smith@company.com,bob.wilson@company.com,alice.brown@company.com
call.center.update.agent.list,support-center@company.com,support1@company.com,support2@company.com,,
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

# Modify call center agent lists from CSV
results = agent.bulk.modify_call_center_agent_list_from_csv(
    csv_path="path/to/your/agent_modifications.csv",
    dry_run=False  # Set to True to validate without modifying
)

# Process results
for result in results:
    if result["success"]:
        print(f"✅ Updated agent list for call center: {result['data']['serviceUserId']}")
    else:
        print(f"❌ Failed to update agent list: {result.get('error', 'Unknown error')}")
```

## Modify from Data (Method Call in IDE)

When modifying call center agent lists programmatically:

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

# Define agent list modification data
agent_modifications_data = [
    {
        "operation": "call.center.update.agent.list",
        "service_user_id": "sales-center@company.com",
        "agent_user_id_list": {
            "user_id": [
                "john.doe@company.com",
                "jane.smith@company.com",
                "bob.wilson@company.com",
                "alice.brown@company.com"
            ]
        }
    },
    {
        "operation": "call.center.update.agent.list", 
        "service_user_id": "support-center@company.com",
        "agent_user_id_list": {
            "user_id": [
                "support1@company.com",
                "support2@company.com"
            ]
        }
    }
]

# Modify call center agent lists from data
results = agent.bulk.modify_call_center_agent_list_from_data(
    agent_modification_data=agent_modifications_data,
    dry_run=False  # Set to True to validate without modifying
)

# Process results
for result in results:
    if result["success"]:
        print(f"✅ Updated agent list for call center: {result['data']['serviceUserId']}")
    else:
        print(f"❌ Failed to update agent list: {result.get('error', 'Unknown error')}")
```

## Dry Run Mode

Both methods support dry run mode for validation:

```python
# Validate data without modifying agent lists
results = agent.bulk.modify_call_center_agent_list_from_csv(
    csv_path="path/to/your/agent_modifications.csv",
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
        "data": {...},  # Original data for this modification
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
- **API errors**: BroadWorks server errors (call center not found, invalid agents, etc.)
- **Network errors**: Connection issues

Check the `success` field and `error` message in results for detailed error information.

## Common Use Cases

### Adding Agents to Call Center
```csv
operation,serviceUserId,agentUserIdList.userId[0],agentUserIdList.userId[1]
call.center.update.agent.list,sales-center@company.com,new.agent1@company.com,new.agent2@company.com
```

### Removing All Agents from Call Center
```csv
operation,serviceUserId
call.center.update.agent.list,sales-center@company.com
```

### Replacing Agent List
```csv
operation,serviceUserId,agentUserIdList.userId[0],agentUserIdList.userId[1],agentUserIdList.userId[2]
call.center.update.agent.list,sales-center@company.com,replacement1@company.com,replacement2@company.com,replacement3@company.com
```

## Notes

- **Template location**: Find the bulk sheet template in [`call.center.modify.agent.list.csv`](https://github.com/Fourteen-IP/mercury-ocip/tree/main/assets/bulk%20sheets)
- **Case conversion**: Column names are automatically converted from camelCase to snake_case
- **Empty values**: Empty `agentUserIdList.userId[N]` columns are automatically filtered out
- **Nested objects**: Use dot notation (e.g., `agentUserIdList.userId[0]`) for nested object properties
- **Replacement behavior**: This operation completely replaces the existing agent list
- **Agent validation**: All specified agents must exist in the system before the operation
- **Call center validation**: The target call center must exist before modifying its agent list
- **No defaults**: This operation has no default values - you must specify the exact agent list you want