# Modify Group Admin Policy

The group admin policy bulk operation allows you to modify group administrator policy settings efficiently using either CSV files or direct method calls.

## Description

Group admin policy modification enables you to update access control settings for group administrators. This bulk operation modifies multiple group administrator policies with their associated access settings in a single operation, supporting both CSV-based and programmatic approaches.

## Modify from CSV

### Setup

1. **Get the template**: Find the bulk sheet template at [`group.admin.modify.policy.csv`](https://github.com/Fourteen-IP/mercury-ocip/tree/main/assets/bulk%20sheets)
2. **Fill in your data**: Use the template to define your group admin policy modifications

### CSV Format

The CSV template includes these columns:

| Column | Description | Required | Example |
|--------|-------------|----------|---------|
| `operation` | Operation type | Yes | `group.admin.modify.policy` |
| `userId` | Group administrator user identifier | Yes | `"admin@company.com"` |
| `profileAccess` | Profile access level | No | `"Full"` |
| `userAccess` | User access level | No | `"Full"` |
| `adminAccess` | Admin access level | No | `"Full"` |
| `departmentAccess` | Department access level | No | `"Full"` |
| `accessDeviceAccess` | Access device access level | No | `"Read-Only"` |
| `enhancedServiceInstanceAccess` | Enhanced service instance access level | No | `"Modify-Only"` |
| `featureAccessCodeAccess` | Feature access code access level | No | `"Read-Only"` |
| `phoneNumberExtensionAccess` | Phone number extension access level | No | `"Read-Only"` |
| `callingLineIdNumberAccess` | Calling line ID number access level | No | `"Full"` |
| `serviceAccess` | Service access level | No | `"Read-Only"` |
| `trunkGroupAccess` | Trunk group access level | No | `"Full"` |
| `sessionAdmissionControlAccess` | Session admission control access level | No | `"Read-Only"` |
| `officeZoneAccess` | Office zone access level | No | `"Read-Only"` |
| `dialableCallerIDAccess` | Dialable caller ID access level | No | `"Read-Only"` |
| `numberActivationAccess` | Number activation access level | No | `"None"` |

### Access Level Values

All access level fields accept the following values:
- `"None"` - No access
- `"Read-Only"` - Read-only access
- `"Full"` - Full access
- `"Modify-Only"` - Modify-only access (for some fields)

### Defaults

To make group admin policy modification more user-friendly, sensible defaults are automatically applied if you don't specify them. This means you only need to provide the `userId`, and the system will apply all default access settings.

**Group Admin Policy Defaults:**

When you don't specify access levels, the following defaults are automatically applied:

| Field | Default Value |
|-------|---------------|
| `profileAccess` | `"Read-Only"` |
| `userAccess` | `"Full"` |
| `adminAccess` | `"Read-Only"` |
| `departmentAccess` | `"Full"` |
| `accessDeviceAccess` | `"Read-Only"` |
| `enhancedServiceInstanceAccess` | `"Modify-Only"` |
| `featureAccessCodeAccess` | `"Read-Only"` |
| `phoneNumberExtensionAccess` | `"Read-Only"` |
| `callingLineIdNumberAccess` | `"Full"` |
| `serviceAccess` | `"Read-Only"` |
| `trunkGroupAccess` | `"Full"` |
| `sessionAdmissionControlAccess` | `"Read-Only"` |
| `officeZoneAccess` | `"Read-Only"` |
| `numberActivationAccess` | `"None"` |
| `dialableCallerIDAccess` | `"Read-Only"` |

**Benefits of Defaults:**
- **Quick setup**: Apply standard policy settings with minimal configuration
- **Consistent policies**: Defaults ensure consistent access control across your organisation
- **Easy customisation**: Override any default by specifying a different value
- **Minimal configuration**: Only specify `userId` to apply all default policies

**Example - Minimal CSV (Defaults Applied):**

```csv
operation,userId
group.admin.modify.policy,admin@company.com
```

This minimal example will modify the group admin policy with all default access settings applied. The administrator will have:
- `Read-Only` access to profiles, admin settings, devices, feature codes, phone numbers, services, session admission control, office zones, and dialable caller ID
- `Full` access to users, departments, calling line ID numbers, and trunk groups
- `Modify-Only` access to enhanced service instances
- `None` access to number activation

**Example - Custom CSV (Overriding Defaults):**

```csv
operation,userId,profileAccess,userAccess,adminAccess
group.admin.modify.policy,admin@company.com,Full,Full,Full
```

This example overrides the default values for `profileAccess`, `userAccess`, and `adminAccess` to `Full`, while all other fields will use their defaults.

### Example CSV Data

```csv
operation,userId,profileAccess,userAccess,adminAccess,departmentAccess,accessDeviceAccess,enhancedServiceInstanceAccess,featureAccessCodeAccess,phoneNumberExtensionAccess,callingLineIdNumberAccess,serviceAccess,trunkGroupAccess,sessionAdmissionControlAccess,officeZoneAccess,dialableCallerIDAccess,numberActivationAccess
group.admin.modify.policy,admin1@company.com,Full,Full,Full,Full,Read-Only,Full,Read-Only,Read-Only,Full,Read-Only,Full,Read-Only,Read-Only,Read-Only,None
group.admin.modify.policy,admin2@company.com,Read-Only,Full,Read-Only,Full,Read-Only,Modify-Only,Read-Only,Read-Only,Full,Read-Only,Full,Read-Only,Read-Only,Read-Only,None
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

# Modify group admin policies from CSV
results = agent.bulk.modify_group_admin_policy_from_csv(
    csv_path="path/to/your/group_admin_policies.csv",
    dry_run=False  # Set to True to validate without modifying
)

# Process results
for result in results:
    if result["success"]:
        print(f"✅ Modified policy for: {result['data']['user_id']}")
    else:
        print(f"❌ Failed to modify policy: {result.get('response', 'Unknown error')}")
```

## Modify from Data (Method Call in IDE)

> **Note:** This is a highlighted note
> When modifying group admin policies programmatically, you can omit any optional fields, and defaults will be automatically applied. Only the `user_id` field is required.

When modifying group admin policies programmatically, you can omit any optional fields, and defaults will be automatically applied. Only the `user_id` field is required.

For programmatic modification without CSV files:

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

# Define group admin policy data
group_admin_policy_data = [
    {
        "operation": "group.admin.modify.policy",
        "user_id": "admin1@company.com",
        "profile_access": "Full",
        "user_access": "Full",
        "admin_access": "Full",
        "department_access": "Full"
    },
    {
        # All other fields will use defaults
        "operation": "group.admin.modify.policy",
        "user_id": "admin2@company.com"
    }
]

# Modify group admin policies from data
results = agent.bulk.modify_group_admin_policy_from_data(
    group_admin_policy_data=group_admin_policy_data,
    dry_run=False  # Set to True to validate without modifying
)

# Process results
for result in results:
    if result["success"]:
        print(f"✅ Modified policy for: {result['data']['user_id']}")
    else:
        print(f"❌ Failed to modify policy: {result.get('response', 'Unknown error')}")
```

### Example - Apply Defaults Only

The simplest way to apply all default policies is to provide only the `user_id`:

```python
# Apply all default policies
group_admin_policy_data = [
    {
        "operation": "group.admin.modify.policy",
        "user_id": "admin@company.com"
    }
]

results = agent.bulk.modify_group_admin_policy_from_data(
    group_admin_policy_data=group_admin_policy_data,
    dry_run=False
)
```

This will apply all default access settings as listed in the Defaults section above.

## Dry Run Mode

Both methods support dry run mode for validation:

```python
# Validate data without modifying policies
results = agent.bulk.modify_group_admin_policy_from_csv(
    csv_path="path/to/your/group_admin_policies.csv",
    dry_run=True
)
```

Dry run mode will:
- Parse and validate your data
- Check for required fields and data types
- Apply defaults to preview the final configuration
- Return validation results without making actual API calls

## Response Format

Both methods return a list of result dictionaries:

```python
[
    {
        "index": 0,
        "data": {...},  # Original data for this policy modification
        "command": {...},  # Generated command object with defaults applied
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
- **API errors**: BroadWorks server errors (invalid admin, access denied, etc.)
- **Network errors**: Connection issues

Check the `success` field and `response` field in results for detailed error information. When `success` is `False`, the `response` field will contain the error details.

## Notes

- **Template location**: Find the bulk sheet template in [`group.admin.modify.policy.csv`](https://github.com/Fourteen-IP/mercury-ocip/tree/main/assets/bulk%20sheets)
- **Case conversion**: Column names are automatically converted from camelCase to snake_case
- **Default application**: All access level fields will use defaults if not specified
- **Required fields**: Only `userId` is required; all other fields are optional and will use defaults

