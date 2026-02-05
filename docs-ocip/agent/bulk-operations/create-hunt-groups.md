# Create Hunt Groups

The hunt groups bulk operation allows you to create multiple hunt groups efficiently using either CSV files or direct method calls.

## Description

Hunt groups enable call distribution across multiple agents with various policies like Regular, Circular, Simultaneous, Uniform, and Weighted Call Distribution. This bulk operation creates multiple hunt groups with their associated agents and configuration in a single operation, supporting both CSV-based and programmatic approaches.

## Create from CSV

### Setup

1. **Get the template**: Find the bulk sheet template at [`hunt.group.create.csv`](https://github.com/Fourteen-IP/mercury-ocip/tree/main/assets/bulk%20sheets)
2. **Fill in your data**: Use the template to define your hunt groups

### CSV Format

The CSV template includes these columns:

| Column | Description | Required | Example |
|--------|-------------|----------|---------|
| `operation` | Operation type | Yes | `hunt.group.create` |
| `serviceProviderId` | Service provider identifier | Yes | `"MyServiceProvider"` |
| `groupId` | Group identifier | Yes | `"SalesGroup"` |
| `serviceUserId` | Hunt group service user ID | Yes | `"sales-hunt@domain.com"` |
| `serviceInstanceProfile.name` | Hunt group display name | Yes | `"Sales Hunt Group"` |
| `serviceInstanceProfile.callingLineIdLastName` | Last name for caller ID | Yes | `"Sales"` |
| `serviceInstanceProfile.callingLineIdFirstName` | First name for caller ID | Yes | `"Team"` |
| `serviceInstanceProfile.hiraganaLastName` | Hiragana last name | No | `"セールス"` |
| `serviceInstanceProfile.hiraganaFirstName` | Hiragana first name | No | `"チーム"` |
| `serviceInstanceProfile.phoneNumber` | Phone number | No | `"+81355555555"` |
| `serviceInstanceProfile.extension` | Extension | No | `"1234"` |
| `serviceInstanceProfile.password` | Password | No | `"password123"` |
| `serviceInstanceProfile.language` | Language | No | `"Japanese"` |
| `serviceInstanceProfile.timeZone` | Time zone | No | `"Asia/Tokyo"` |
| `serviceInstanceProfile.alias[0-2]` | Aliases (up to 3) | No | `"sales-team"` |
| `serviceInstanceProfile.publicUserIdentity` | Public user identity | No | `"sip:sales@domain.com"` |
| `serviceInstanceProfile.callingLineIdPhoneNumber` | Caller ID number | No | `"+81355555555"` |
| `policy` | Hunt group policy | Yes | `"Regular"` |
| `huntAfterNoAnswer` | Hunt to next agent on no answer | No | `true` |
| `noAnswerNumberOfRings` | Number of rings before hunting | No | `5` |
| `forwardAfterTimeout` | Forward calls after timeout | No | `false` |
| `forwardTimeoutSeconds` | Timeout in seconds | No | `10` |
| `allowCallWaitingForAgents` | Allow call waiting for agents | No | `true` |
| `useSystemHuntGroupCLIDSetting` | Use system CLID setting | No | `false` |
| `includeHuntGroupNameInCLID` | Include group name in CLID | No | `true` |
| `enableNotReachableForwarding` | Enable not reachable forwarding | No | `false` |
| `makeBusyWhenNotReachable` | Make busy when not reachable | No | `true` |
| `allowMembersToControlGroupBusy` | Allow members to control group busy | No | `true` |
| `enableGroupBusy` | Enable group busy | No | `false` |
| `applyGroupBusyWhenTerminatingToAgent` | Apply group busy when terminating to agent | No | `true` |
| `forwardToPhoneNumber` | Forward to phone number | No | `"+81355555556"` |
| `notReachableForwardToPhoneNumber` | Not reachable forward number | No | `"+81355555557"` |
| `networkClassOfService` | Network class of service | No | `"Premium"` |
| `agentUserId[0-7]` | Agent user IDs (up to 8) | Yes (at least one) | `"agent1@domain.com"` |

### Defaults

To make hunt group creation more user-friendly, many fields have sensible defaults that will be automatically applied if you don't specify them. This means you only need to provide the essential information, and the system will handle the rest.

**Service Instance Profile Defaults:**
- `serviceInstanceProfile.name`: `"Test Group Name"`
- `serviceInstanceProfile.callingLineIdLastName`: `"Test Calling Lined Id Last Name"`
- `serviceInstanceProfile.callingLineIdFirstName`: `"Test Calling Lined Id First Name"`
- `serviceInstanceProfile.alias`: `[]` (empty array)

**Hunt Group Configuration Defaults:**
- `policy`: `"Regular"` (sequential hunting)
- `huntAfterNoAnswer`: `true` (hunt to next agent on no answer)
- `noAnswerNumberOfRings`: `5` (ring 5 times before hunting)
- `forwardAfterTimeout`: `false` (don't forward after timeout)
- `forwardTimeoutSeconds`: `10` (10 second timeout)
- `allowCallWaitingForAgents`: `true` (allow call waiting)
- `useSystemHuntGroupCLIDSetting`: `true` (use system CLID settings)
- `includeHuntGroupNameInCLID`: `true` (include group name in caller ID)
- `enableNotReachableForwarding`: `false` (disable not reachable forwarding)
- `makeBusyWhenNotReachable`: `false` (don't make busy when not reachable)
- `allowMembersToControlGroupBusy`: `false` (don't allow members to control group busy)
- `enableGroupBusy`: `false` (disable group busy)
- `applyGroupBusyWhenTerminatingToAgent`: `false` (don't apply group busy when terminating)
- `agentUserId`: `[]` (empty array - you must provide at least one agent)

**Benefits of Defaults:**
- **Simplified CSV**: You only need to specify the fields you want to customise
- **Faster setup**: Focus on the important configuration without worrying about every detail
- **Consistent behaviour**: Defaults ensure predictable hunt group behaviour across your organisation
- **Easy migration**: Existing hunt groups can be recreated with minimal configuration

**Example - Minimal CSV:**
```csv
operation,serviceProviderId,groupId,serviceUserId,serviceInstanceProfile.name,agentUserId[0],agentUserId[1]
hunt.group.create,MyServiceProvider,SalesGroup,sales-hunt@company.com,Sales Hunt Group,john.doe@company.com,jane.smith@company.com
```

This minimal example will create a hunt group with all the default settings applied automatically.

### Policy Options

The `policy` field supports these hunt group policies:

- **Regular**: Sequential hunting through agents
- **Circular**: Round-robin hunting
- **Simultaneous**: Ring all agents simultaneously
- **Uniform**: Distribute calls evenly
- **Weighted Call Distribution**: Distribute based on agent weights

### Nested Object Notation

The `serviceInstanceProfile.*` notation allows you to configure the hunt group's service instance profile with nested properties like name, caller ID settings, and aliases.

### Array Notation

The `agentUserId[0]`, `agentUserId[1]`, etc. notation allows you to specify multiple agents in a single hunt group. You can include as many `agentUserId[N]` columns as needed, but it's recommended to only include the number of columns you actually need to avoid empty columns.

### Example CSV Data

```csv
operation,serviceProviderId,groupId,serviceUserId,serviceInstanceProfile.name,serviceInstanceProfile.callingLineIdLastName,serviceInstanceProfile.callingLineIdFirstName,policy,huntAfterNoAnswer,noAnswerNumberOfRings,agentUserId[0],agentUserId[1],agentUserId[2]
hunt.group.create,MyServiceProvider,SalesGroup,sales-hunt@company.com,Sales Hunt Group,Sales,Team,Regular,true,5,john.doe@company.com,jane.smith@company.com,bob.wilson@company.com
hunt.group.create,MyServiceProvider,SupportGroup,support-hunt@company.com,Support Hunt Group,Support,Team,Circular,true,3,support1@company.com,support2@company.com,
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

# Create hunt groups from CSV
results = agent.bulk.create_hunt_group_from_csv(
    csv_path="path/to/your/hunt_groups.csv",
    dry_run=False  # Set to True to validate without creating
)

# Process results
for result in results:
    if result["success"]:
        print(f"✅ Created hunt group: {result['data']['serviceInstanceProfile']['name']}")
    else:
        print(f"❌ Failed to create hunt group: {result.get('error', 'Unknown error')}")
```

## Create from Data (Method Call in IDE)

> **Note:** This is a highlighted note
> When creating hunt groups programmatically, you can omit any optional fields - the defaults detailed in the CSV Format section above will 
> be automatically applied, allowing for more concise data structures.


When creating hunt groups programmatically, you can omit any optional fields - the defaults detailed in the CSV Format section above will be automatically applied, allowing for more concise data structures.

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

# Define hunt group data
hunt_groups_data = [
    {
        "operation": "hunt.group.create",
        "service_provider_id": "MyServiceProvider", 
        "group_id": "SalesGroup",
        "service_user_id": "sales-hunt@company.com",
        "service_instance_profile": {
            "name": "Sales Hunt Group",
            "calling_line_id_last_name": "Sales",
            "calling_line_id_first_name": "Team",
            "alias": ["sales-team", "sales-hunt"]
        },
        "policy": "Regular",
        "hunt_after_no_answer": True,
        "no_answer_number_of_rings": 5,
        "forward_after_timeout": False,
        "forward_timeout_seconds": 10,
        "allow_call_waiting_for_agents": True,
        "agent_user_id": [
            "john.doe@company.com",
            "jane.smith@company.com",
            "bob.wilson@company.com"
        ]
    },
    {
        "operation": "hunt.group.create", 
        "service_provider_id": "MyServiceProvider",
        "group_id": "SupportGroup",
        "service_user_id": "support-hunt@company.com",
        "service_instance_profile": {
            "name": "Support Hunt Group",
            "calling_line_id_last_name": "Support",
            "calling_line_id_first_name": "Team",
            "alias": ["support-team"]
        },
        "policy": "Circular",
        "hunt_after_no_answer": True,
        "no_answer_number_of_rings": 3,
        "agent_user_id": [
            "support1@company.com",
            "support2@company.com"
        ]
    }
]

# Create hunt groups from data
results = agent.bulk.create_hunt_group_from_data(
    hunt_group_data=hunt_groups_data,
    dry_run=False  # Set to True to validate without creating
)

# Process results
for result in results:
    if result["success"]:
        print(f"✅ Created hunt group: {result['data']['serviceInstanceProfile']['name']}")
    else:
        print(f"❌ Failed to create hunt group: {result.get('error', 'Unknown error')}")
```

## Dry Run Mode

Both methods support dry run mode for validation:

```python
# Validate data without creating hunt groups
results = agent.bulk.create_hunt_group_from_csv(
    csv_path="path/to/your/hunt_groups.csv",
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
        "data": {...},  # Original data for this hunt group
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
- **API errors**: BroadWorks server errors (duplicate groups, invalid agents, etc.)
- **Network errors**: Connection issues

Check the `success` field and `error` message in results for detailed error information.

## Notes

- **Agent ID arrays**: The `agentUserId[0]`, `agentUserId[1]` notation can handle as many agents as needed, but it's best practice to only include the number of columns you actually need
- **Template location**: Find the bulk sheet template in [`hunt.group.create.csv`](https://github.com/Fourteen-IP/mercury-ocip/tree/main/assets/bulk%20sheets)
- **Case conversion**: Column names are automatically converted from camelCase to snake_case
- **Empty values**: Empty `agentUserId[N]` columns are automatically filtered out
- **Nested objects**: Use dot notation (e.g., `serviceInstanceProfile.name`) for nested object properties
- **Boolean values**: Use `true`/`false` for boolean fields in CSV
- **Integer fields**: `noAnswerNumberOfRings` and `forwardTimeoutSeconds` are automatically converted to integers