# Create Call Centers

The call centers bulk operation allows you to create multiple call centers efficiently using either CSV files or direct method calls.

## Description

Call center creation enables you to set up call center services with various configurations including service instance profiles, routing policies, queue management, and agent settings. This bulk operation creates multiple call centers with their associated configuration in a single operation, supporting both CSV-based and programmatic approaches.

**Important**: Call centers come in three types (Basic, Standard, and Premium), each with different available options. Using options that are not available for your selected call center type will result in errors. Always ensure you only use options compatible with your chosen `type`.

## Call Center Types

### Basic Call Center
The Basic call center type provides essential call center functionality with queue management and basic agent handling.

### Standard Call Center
The Standard call center type includes all Basic features plus reporting capabilities and advanced agent state management.

### Premium Call Center
The Premium call center type includes all Standard features plus advanced routing capabilities with priority-based or skill-based routing.

## Create from CSV

### Setup

1. **Get the template**: Find the bulk sheet template at [`call.center.create.csv`](https://github.com/Fourteen-IP/mercury-ocip/tree/main/assets/bulk%20sheets)
2. **Fill in your data**: Use the template to define your call centers

### CSV Format

The CSV template includes these columns:

| Column | Description | Required | Call Center Type | Example |
|--------|-------------|----------|------------------|---------|
| `operation` | Operation type | Yes | All | `call.center.create` |
| `serviceProviderId` | Service provider identifier | Yes | All | `"MyServiceProvider"` |
| `groupId` | Group identifier | Yes | All | `"SalesGroup"` |
| `serviceUserId` | Service user ID | Yes | All | `"sales-center@company.com"` |
| `serviceInstanceProfile.name` | Call center name | Yes | All | `"Sales Call Center"` |
| `serviceInstanceProfile.callingLineIdLastName` | CLID last name | Yes | All | `"Sales"` |
| `serviceInstanceProfile.callingLineIdFirstName` | CLID first name | Yes | All | `"Center"` |
| `serviceInstanceProfile.password` | Service password | Yes | All | `"password123"` |
| `serviceInstanceProfile.hiraganaLastName` | Hiragana last name | No | All | `"セールス"` |
| `serviceInstanceProfile.hiraganaFirstName` | Hiragana first name | No | All | `"センター"` |
| `serviceInstanceProfile.phoneNumber` | Phone number | No | All | `"+81355555555"` |
| `serviceInstanceProfile.extension` | Extension | No | All | `"5000"` |
| `serviceInstanceProfile.language` | Language | No | All | `"Japanese"` |
| `serviceInstanceProfile.timeZone` | Time zone | No | All | `"Asia/Tokyo"` |
| `serviceInstanceProfile.alias[0]` | Alias (1st) | No | All | `"sales-cc"` |
| `serviceInstanceProfile.alias[1]` | Alias (2nd) | No | All | `"sales-callcenter"` |
| `serviceInstanceProfile.alias[2]` | Alias (3rd) | No | All | `"sales-cc1"` |
| `serviceInstanceProfile.publicUserIdentity` | Public user identity | No | All | `"sip:sales@domain.com"` |
| `serviceInstanceProfile.callingLineIdPhoneNumber` | CLID phone number | No | All | `"+81355555555"` |
| `type` | Call center type | Yes | All | `Basic`, `Standard`, or `Premium` |
| `policy` | Routing policy | Yes | All | `Circular`, `Regular`, `Similtaneous`, `Uniform`, or `Weighted Call Distribution` |
| `enableVideo` | Enable video | No | All | `true` or `false` |
| `queueLength` | Queue length | No | All | `3` |
| `allowCallerToDialEscapeDigit` | Allow escape digit dialling | No | All | `true` or `false` |
| `escapeDigit` | Escape digit | No | All | `"3"` |
| `resetCallStatisticsUponEntryInQueue` | Reset stats on queue entry | No | All | `true` or `false` |
| `allowAgentLogoff` | Allow agent logoff | No | All | `true` or `false` |
| `allowCallWaitingForAgents` | Allow call waiting | No | All | `true` or `false` |
| `externalPreferredAudioCodec` | External audio codec | No | All | `"None"` |
| `internalPreferredAudioCodec` | Internal audio codec | No | All | `"None"` |
| `playRingingWhenOfferingCall` | Play ringing on call offer | No | All | `true` or `false` |
| `routingType` | Routing type | No | **Premium only** | `Priority Based` or `Skill Based` |
| `enableReporting` | Enable reporting | No | **Standard+ only** | `true` or `false` |
| `allowCallsToAgentsInWrapUp` | Allow calls during wrap-up | No | **Standard+ only** | `true` or `false` |
| `overrideAgentWrapUpTime` | Override wrap-up time | No | **Standard+ only** | `true` or `false` |
| `wrapUpSeconds` | Wrap-up time (seconds) | No | **Standard+ only** | `30` |
| `forceDeliveryOfCalls` | Force delivery of calls | No | **Premium only** | `true` or `false` |
| `forceDeliveryWaitTimeSeconds` | Force delivery wait time | No | **Premium only** | `9` |
| `enableAutomaticStateChangeForAgents` | Auto state change for agents | No | **Standard+ only** | `true` or `false` |
| `agentStateAfterCall` | Agent state after call | No | **Standard+ only** | `Available`, `Unavailable`, or `Wrap-Up` |
| `agentUnavailableCode` | Agent unavailable code | No | **Standard+ only** | `"3"` |
| `networkClassOfService` | Network class of service | No | All | `"Premium"` |

### Call Center Type-Specific Options

**Critical**: Only use options that are available for your selected call center `type`. Using incompatible options will result in API errors.

#### Basic Call Center Options
Basic call centers support all the core options but **cannot** use:
- `routingType` (Premium only)
- `enableReporting` (Standard+ only)
- `allowCallsToAgentsInWrapUp` (Standard+ only)
- `overrideAgentWrapUpTime` (Standard+ only)
- `wrapUpSeconds` (Standard+ only)
- `forceDeliveryOfCalls` (Premium only)
- `forceDeliveryWaitTimeSeconds` (Premium only)
- `enableAutomaticStateChangeForAgents` (Standard+ only)
- `agentStateAfterCall` (Standard+ only)
- `agentUnavailableCode` (Standard+ only)

#### Standard Call Center Options
Standard call centers include all Basic options plus:
- `enableReporting`
- `allowCallsToAgentsInWrapUp`
- `overrideAgentWrapUpTime`
- `wrapUpSeconds`
- `enableAutomaticStateChangeForAgents`
- `agentStateAfterCall`
- `agentUnavailableCode`

Standard call centers **cannot** use:
- `routingType` (Premium only)
- `forceDeliveryOfCalls` (Premium only)
- `forceDeliveryWaitTimeSeconds` (Premium only)

#### Premium Call Center Options
Premium call centers include all Standard options plus:
- `routingType`
- `forceDeliveryOfCalls`
- `forceDeliveryWaitTimeSeconds`

### Defaults

To make call center creation more user-friendly, many fields have sensible defaults that will be automatically applied if you don't specify them. This means you only need to provide the essential information, and the system will handle the rest.

**Call Center Profile Defaults:**
- `serviceInstanceProfile.name`: `"Default Call Center Name"`
- `serviceInstanceProfile.callingLineIdLastName`: `"Default CLID Last Name"`
- `serviceInstanceProfile.callingLineIdFirstName`: `"Default CLID First Name"`

**Basic Call Center Defaults:**
- `type`: `Basic`
- `policy`: `Circular`
- `enableVideo`: `false`
- `queueLength`: `3`
- `allowCallerToDialEscapeDigit`: `false`
- `escapeDigit`: `"3"`
- `resetCallStatisticsUponEntryInQueue`: `true`
- `allowAgentLogoff`: `true`
- `allowCallWaitingForAgents`: `true`
- `externalPreferredAudioCodec`: `"None"`
- `internalPreferredAudioCodec`: `"None"`
- `playRingingWhenOfferingCall`: `true`

**Standard Call Center Defaults:**
Standard call centers use all Basic defaults. The following are available but have no default values (you must explicitly set them if needed):
- `enableReporting`
- `wrapUpSeconds`
- `overrideAgentWrapUpTime`
- `allowCallsToAgentsInWrapUp`
- `enableAutomaticStateChangeForAgents`
- `agentStateAfterCall`
- `agentUnavailableCode`

**Premium Call Center Defaults:**
Premium call centers use all Standard defaults. The following are available but have no default values (you must explicitly set them if needed):
- `routingType`
- `forceDeliveryOfCalls`
- `forceDeliveryWaitTimeSeconds`

### Nested Object Notation

The `serviceInstanceProfile.*` notation allows you to configure the service instance profile with nested properties like name, calling line ID, password, and contact information.

### Array Notation

The `serviceInstanceProfile.alias[0]`, `serviceInstanceProfile.alias[1]`, `serviceInstanceProfile.alias[2]` notation allows you to specify up to 3 aliases for a single call center. You can include as many `alias[N]` columns as needed, but it's recommended to only include the number of columns you actually need to avoid empty columns.

### Example CSV Data

**Example - Basic Call Center:**
```csv
operation,serviceProviderId,groupId,serviceUserId,serviceInstanceProfile.name,serviceInstanceProfile.callingLineIdLastName,serviceInstanceProfile.callingLineIdFirstName,serviceInstanceProfile.password,type,policy
call.center.create,MyServiceProvider,SalesGroup,sales-center@company.com,Sales Call Center,Sales,Center,password123,Basic,Circular
```

**Example - Standard Call Center:**
```csv
operation,serviceProviderId,groupId,serviceUserId,serviceInstanceProfile.name,serviceInstanceProfile.callingLineIdLastName,serviceInstanceProfile.callingLineIdFirstName,serviceInstanceProfile.password,type,policy,enableReporting,wrapUpSeconds,allowCallsToAgentsInWrapUp
call.center.create,MyServiceProvider,SupportGroup,support-center@company.com,Support Call Center,Support,Center,password456,Standard,Circular,true,30,true
```

**Example - Premium Call Center:**
```csv
operation,serviceProviderId,groupId,serviceUserId,serviceInstanceProfile.name,serviceInstanceProfile.callingLineIdLastName,serviceInstanceProfile.callingLineIdFirstName,serviceInstanceProfile.password,type,policy,routingType,forceDeliveryOfCalls,forceDeliveryWaitTimeSeconds
call.center.create,MyServiceProvider,PremiumGroup,premium-center@company.com,Premium Call Center,Premium,Center,password789,Premium,Circular,Priority Based,false,9
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

# Create call centers from CSV
results = agent.bulk.create_call_center_from_csv(
    csv_path="path/to/your/call-centers.csv",
    dry_run=False  # Set to True to validate without creating
)

# Process results
for result in results:
    if result["success"]:
        print(f"✅ Created call center: {result['data']['service_instance_profile']['name']}")
    else:
        print(f"❌ Failed to create call center: {result.get('response', 'Unknown error')}")
```

## Create from Data (Method Call in IDE)

> **Note:** This is a highlighted note
> When creating call centers programmatically, you can omit any optional fields, but all required fields must be explicitly provided. The system will validate all required fields before processing. **Most importantly, ensure you only include options compatible with your selected call center `type` to avoid API errors.**

When creating call centers programmatically, you can omit any optional fields, but all required fields must be explicitly provided. The system will validate all required fields before processing.

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

# Define call center data
call_centers_data = [
    {
        "operation": "call.center.create",
        "service_provider_id": "MyServiceProvider",
        "group_id": "SalesGroup",
        "service_user_id": "sales-center@company.com",
        "service_instance_profile": {
            "name": "Sales Call Center",
            "calling_line_id_last_name": "Sales",
            "calling_line_id_first_name": "Center",
            "password": "password123"
        },
        "type": "Basic",
        "policy": "Circular"
    },
    {
        "operation": "call.center.create",
        "service_provider_id": "MyServiceProvider",
        "group_id": "SupportGroup",
        "service_user_id": "support-center@company.com",
        "service_instance_profile": {
            "name": "Support Call Center",
            "calling_line_id_last_name": "Support",
            "calling_line_id_first_name": "Center",
            "password": "password456"
        },
        "type": "Standard",
        "policy": "Circular",
        "enable_reporting": True,
        "wrap_up_seconds": 30,
        "allow_calls_to_agents_in_wrap_up": True
    },
    {
        "operation": "call.center.create",
        "service_provider_id": "MyServiceProvider",
        "group_id": "PremiumGroup",
        "service_user_id": "premium-center@company.com",
        "service_instance_profile": {
            "name": "Premium Call Center",
            "calling_line_id_last_name": "Premium",
            "calling_line_id_first_name": "Center",
            "password": "password789"
        },
        "type": "Premium",
        "policy": "Circular",
        "routing_type": "Priority Based",
        "enable_reporting": True,
        "wrap_up_seconds": 30,
        "force_delivery_of_calls": False,
        "force_delivery_wait_time_seconds": 9
    }
]

# Create call centers from data
results = agent.bulk.create_call_center_from_data(
    call_center_data=call_centers_data,
    dry_run=False  # Set to True to validate without creating
)

# Process results
for result in results:
    if result["success"]:
        print(f"✅ Created call center: {result['data']['service_instance_profile']['name']}")
    else:
        print(f"❌ Failed to create call center: {result.get('response', 'Unknown error')}")
```

## Dry Run Mode

Both methods support dry run mode for validation:

```python
# Validate data without creating call centers
results = agent.bulk.create_call_center_from_csv(
    csv_path="path/to/your/call-centers.csv",
    dry_run=True
)
```

Dry run mode will:
- Parse and validate your data
- Check for required fields and data types
- Return validation results without making actual API calls

**Note**: Dry run mode may not catch all call center type compatibility issues. Always ensure you're using options compatible with your selected `type`.

## Response Format

Both methods return a list of result dictionaries:

```python
[
    {
        "index": 0,
        "data": {...},  # Original data for this call center
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
- **API errors**: BroadWorks server errors (duplicate call centers, invalid service providers, **incompatible options for call center type**, etc.)
- **Network errors**: Connection issues

Check the `success` field and `response` field in results for detailed error information. When `success` is `False`, the `response` field will contain the error details.

## Notes

- **Call Center Type Compatibility**: **Critical** - Only use options that are available for your selected call center `type`. Using options from Standard/Premium on a Basic call center, or Premium-only options on a Standard call center, will result in API errors
- **Type Selection**: The `type` field determines which options are available. Choose `Basic`, `Standard`, or `Premium` based on your requirements
- **Routing Policy**: The `policy` field accepts: `Circular`, `Regular`, `Similtaneous`, `Uniform`, or `Weighted Call Distribution`
- **Routing Type**: The `routingType` field is **Premium only** and accepts: `Priority Based` or `Skill Based`
- **Template location**: Find the bulk sheet template in [`call.center.create.csv`](https://github.com/Fourteen-IP/mercury-ocip/tree/main/assets/bulk%20sheets)
- **Case conversion**: Column names are automatically converted from camelCase to snake_case
- **Empty values**: Empty array columns (`alias[N]`, etc.) are automatically filtered out
- **Nested objects**: Use dot notation (e.g., `serviceInstanceProfile.name`, `serviceInstanceProfile.callingLineIdFirstName`) for nested object properties
- **Boolean values**: Use `true`/`false` for boolean fields in CSV
- **Integer fields**: `queueLength`, `wrapUpSeconds`, and `forceDeliveryWaitTimeSeconds` are automatically converted to integers
- **Defaults**: Many fields have sensible defaults applied automatically (see Defaults section above)

