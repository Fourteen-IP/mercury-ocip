# Create Auto Attendants

The auto attendants bulk operation allows you to create multiple auto attendants efficiently using either CSV files or direct method calls.

## Description

Auto attendants provide automated call routing and menu systems for incoming calls. This bulk operation creates multiple auto attendants with their configuration in a single operation, supporting both CSV-based and programmatic approaches.

> **Note:** This operation creates basic auto attendants only. Adding keys and menu options is not supported in this bulk operation and must be configured separately after creation.

## Create from CSV

### Setup

1. **Get the template**: Find the bulk sheet template at [`auto.attendant.create.csv`](https://github.com/Fourteen-IP/mercury-ocip/tree/main/assets/bulk%20sheets)
2. **Fill in your data**: Use the template to define your auto attendants

### CSV Format

The CSV template includes these columns:

| Column | Description | Required | Example |
|--------|-------------|----------|---------|
| `operation` | Operation type | Yes | `auto.attendant.create` |
| `serviceProviderId` | Service provider identifier | Yes | `"MyServiceProvider"` |
| `groupId` | Group identifier | Yes | `"SalesGroup"` |
| `serviceUserId` | Auto attendant service user ID | Yes | `"sales-aa@domain.com"` |
| `serviceInstanceProfile.name` | Auto attendant display name | Yes | `"Sales Auto Attendant"` |
| `serviceInstanceProfile.callingLineIdLastName` | Last name for caller ID | Yes | `"Sales"` |
| `serviceInstanceProfile.callingLineIdFirstName` | First name for caller ID | Yes | `"AA"` |
| `serviceInstanceProfile.hiraganaLastName` | Hiragana last name | No | `"セールス"` |
| `serviceInstanceProfile.hiraganaFirstName` | Hiragana first name | No | `"オートアテンダント"` |
| `serviceInstanceProfile.phoneNumber` | Phone number | No | `"+81355555555"` |
| `serviceInstanceProfile.extension` | Extension | No | `"1234"` |
| `serviceInstanceProfile.password` | Password | No | `"password123"` |
| `serviceInstanceProfile.language` | Language | No | `"English"` |
| `serviceInstanceProfile.timeZone` | Time zone | No | `"Asia/Tokyo"` |
| `serviceInstanceProfile.alias[0-2]` | Aliases (up to 3) | No | `"sales-aa"` |
| `serviceInstanceProfile.publicUserIdentity` | Public user identity | No | `"sip:sales@domain.com"` |
| `serviceInstanceProfile.callingLineIdPhoneNumber` | Caller ID number | No | `"+81355555555"` |
| `type` | Auto attendant type | No | `"Basic"` |
| `firstDigitTimeoutSeconds` | First digit timeout in seconds | No | `10` |
| `enableVideo` | Enable video calls | No | `false` |
| `extensionDialingScope` | Extension dialing scope | No | `"Group"` |
| `nameDialingEntries` | Name dialing entries | No | `"LastName + FirstName"` |
| `isActive` | Whether auto attendant is active | No | `true` |

### Defaults

To make auto attendant creation more user-friendly, many fields have sensible defaults that will be automatically applied if you don't specify them. This means you only need to provide the essential information, and the system will handle the rest.

**Service Instance Profile Defaults:**
- `serviceInstanceProfile.name`: `"Default Auto Attendant Name"`
- `serviceInstanceProfile.callingLineIdLastName`: `"Default CLID Last Name"`
- `serviceInstanceProfile.callingLineIdFirstName`: `"Default CLID First Name"`

**Auto Attendant Configuration Defaults:**
- `type`: `"Basic"` (Basic auto attendant type)
- `firstDigitTimeoutSeconds`: `10` (10 second timeout for first digit)
- `enableVideo`: `false` (disable video calls)
- `extensionDialingScope`: `"Group"` (group-level extension dialing)
- `nameDialingScope`: `"Group"` (group-level name dialing)
- `nameDialingEntries`: `"LastName + FirstName"` (name dialing format)
- `isActive`: `true` (auto attendant is active)

**Benefits of Defaults:**
- **Simplified CSV**: You only need to specify the fields you want to customise
- **Faster setup**: Focus on the important configuration without worrying about every detail
- **Consistent behaviour**: Defaults ensure predictable auto attendant behaviour across your organisation
- **Easy migration**: Existing auto attendants can be recreated with minimal configuration

**Example - Minimal CSV:**
```csv
operation,serviceProviderId,groupId,serviceUserId,serviceInstanceProfile.name
auto.attendant.create,MyServiceProvider,SalesGroup,sales-aa@company.com,Sales Auto Attendant
```

This minimal example will create an auto attendant with all the default settings applied automatically.

### Type Options

The `type` field supports these auto attendant types:

- **Basic**: Basic auto attendant functionality
- **Standard**: Standard auto attendant with enhanced features

### Extension Dialing Scope Options

The `extensionDialingScope` field supports these options:

- **Group**: Extension dialing within the group
- **Enterprise**: Extension dialing within the enterprise
- **Service Provider**: Extension dialing within the service provider

### Name Dialing Entries Options

The `nameDialingEntries` field supports these options:

- **LastName + FirstName**: Last name followed by first name
- **FirstName + LastName**: First name followed by last name
- **FirstName**: First name only
- **LastName**: Last name only

### Nested Object Notation

The `serviceInstanceProfile.*` notation allows you to configure the auto attendant's service instance profile with nested properties like name, caller ID settings, and aliases.

### Array Notation

The `serviceInstanceProfile.alias[0]`, `serviceInstanceProfile.alias[1]`, etc. notation allows you to specify multiple aliases for an auto attendant. You can include as many `alias[N]` columns as needed, but it's recommended to only include the number of columns you actually need to avoid empty columns.

### Example CSV Data

```csv
operation,serviceProviderId,groupId,serviceUserId,serviceInstanceProfile.name,serviceInstanceProfile.callingLineIdLastName,serviceInstanceProfile.callingLineIdFirstName,type,firstDigitTimeoutSeconds,enableVideo,extensionDialingScope,nameDialingEntries,isActive
auto.attendant.create,MyServiceProvider,SalesGroup,sales-aa@company.com,Sales Auto Attendant,Sales,AA,Basic,15,false,Group,LastName + FirstName,true
auto.attendant.create,MyServiceProvider,SupportGroup,support-aa@company.com,Support Auto Attendant,Support,AA,Standard,20,true,Enterprise,FirstName + LastName,true
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

# Create auto attendants from CSV
results = agent.bulk.create_auto_attendant_from_csv(
    csv_path="path/to/your/auto_attendants.csv",
    dry_run=False  # Set to True to validate without creating
)

# Process results
for result in results:
    if result["success"]:
        print(f"✅ Created auto attendant: {result['data']['serviceInstanceProfile']['name']}")
    else:
        print(f"❌ Failed to create auto attendant: {result.get('error', 'Unknown error')}")
```

## Create from Data (Method Call in IDE)

> **Note:** This is a highlighted note
> When creating auto attendants programmatically, you can omit any optional fields - the defaults detailed in the CSV Format section above will 
> be automatically applied, allowing for more concise data structures.

When creating auto attendants programmatically, you can omit any optional fields - the defaults detailed in the CSV Format section above will be automatically applied, allowing for more concise data structures.

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

# Define auto attendant data
auto_attendants_data = [
    {
        "operation": "auto.attendant.create",
        "service_provider_id": "MyServiceProvider", 
        "group_id": "SalesGroup",
        "service_user_id": "sales-aa@company.com",
        "service_instance_profile": {
            "name": "Sales Auto Attendant",
            "calling_line_id_last_name": "Sales",
            "calling_line_id_first_name": "AA",
            "alias": ["sales-aa", "sales-menu"]
        },
        "type": "Basic",
        "first_digit_timeout_seconds": 15,
        "enable_video": False,
        "extension_dialing_scope": "Group",
        "name_dialing_entries": "LastName + FirstName",
        "is_active": True
    },
    {
        "operation": "auto.attendant.create", 
        "service_provider_id": "MyServiceProvider",
        "group_id": "SupportGroup",
        "service_user_id": "support-aa@company.com",
        "service_instance_profile": {
            "name": "Support Auto Attendant",
            "calling_line_id_last_name": "Support",
            "calling_line_id_first_name": "AA",
            "alias": ["support-aa"]
        },
        "type": "Standard",
        "first_digit_timeout_seconds": 20,
        "enable_video": True,
        "extension_dialing_scope": "Enterprise",
        "name_dialing_entries": "FirstName + LastName",
        "is_active": True
    }
]

# Create auto attendants from data
results = agent.bulk.create_auto_attendant_from_data(
    auto_attendant_data=auto_attendants_data,
    dry_run=False  # Set to True to validate without creating
)

# Process results
for result in results:
    if result["success"]:
        print(f"✅ Created auto attendant: {result['data']['serviceInstanceProfile']['name']}")
    else:
        print(f"❌ Failed to create auto attendant: {result.get('error', 'Unknown error')}")
```

## Dry Run Mode

Both methods support dry run mode for validation:

```python
# Validate data without creating auto attendants
results = agent.bulk.create_auto_attendant_from_csv(
    csv_path="path/to/your/auto_attendants.csv",
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
        "data": {...},  # Original data for this auto attendant
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
- **API errors**: BroadWorks server errors (duplicate auto attendants, invalid configuration, etc.)
- **Network errors**: Connection issues

Check the `success` field and `error` message in results for detailed error information.

## Notes

- **Template location**: Find the bulk sheet template in [`auto.attendant.create.csv`](https://github.com/Fourteen-IP/mercury-ocip/tree/main/assets/bulk%20sheets)
- **Case conversion**: Column names are automatically converted from camelCase to snake_case
- **Empty values**: Empty `alias[N]` columns are automatically filtered out
- **Nested objects**: Use dot notation (e.g., `serviceInstanceProfile.name`) for nested object properties
- **Boolean values**: Use `true`/`false` for boolean fields in CSV
- **Integer fields**: `firstDigitTimeoutSeconds` is automatically converted to integer
- **Keys not supported**: Adding keys and menu options is not supported in this bulk operation and must be configured separately after creation
- **Post-creation configuration**: After creating auto attendants, you'll need to configure keys, menu options, and call routing separately through the BroadWorks interface or additional API calls