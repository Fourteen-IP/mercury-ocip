# Modify Service Provider Admin Policy

The service provider admin policy bulk operation allows you to modify service provider administrator policy settings efficiently using either CSV files or direct method calls.

## Description

Service provider admin policy modification enables you to update access control settings for service provider administrators. This bulk operation modifies multiple service provider administrator policies with their associated access settings in a single operation, supporting both CSV-based and programmatic approaches.

## Modify from CSV

### Setup

1. **Get the template**: Find the bulk sheet template at [`service.provider.admin.modify.policy.csv`](https://github.com/Fourteen-IP/mercury-ocip/tree/main/assets/bulk%20sheets)
2. **Fill in your data**: Use the template to define your service provider admin policy modifications

### CSV Format

The CSV template includes these columns:

| Column | Description | Required | Example |
|--------|-------------|----------|---------|
| `operation` | Operation type | Yes | `service.provider.admin.modify.policy` |
| `userId` | Service provider administrator user identifier | Yes | `"admin@company.com"` |
| `profileAccess` | Profile access level | No | `"Full"` |
| `groupAccess` | Group access level | No | `"Full"` |
| `userAccess` | User access level | No | `"Full Profile"` |
| `adminAccess` | Admin access level | No | `"Full"` |
| `departmentAccess` | Department access level | No | `"Full"` |
| `accessDeviceAccess` | Access device access level | No | `"Full"` |
| `phoneNumberExtensionAccess` | Phone number extension access level | No | `"Assign To Services and Users"` |
| `callingLineIdNumberAccess` | Calling line ID number access level | No | `"Full"` |
| `serviceAccess` | Service access level | No | `"No Authorization"` |
| `servicePackAccess` | Service pack access level | No | `"Full"` |
| `sessionAdmissionControlAccess` | Session admission control access level | No | `"Read-Only"` |
| `webBrandingAccess` | Web branding access level | No | `"Full"` |
| `officeZoneAccess` | Office zone access level | No | `"Full"` |
| `communicationBarringAccess` | Communication barring access level | No | `"Read-Only"` |
| `networkPolicyAccess` | Network policy access level | No | `"None"` |
| `numberActivationAccess` | Number activation access level | No | `"Full"` |
| `dialableCallerIDAccess` | Dialable caller ID access level | No | `"Full"` |
| `verifyTranslationAndRoutingAccess` | Verify translation and routing access level | No | `"None"` |

### Access Level Values

Access level fields accept different values depending on the field:

- **Common values**: `"None"`, `"Full"`, `"Read-Only"`
- **Profile access**: `"None"`, `"Full"`, `"Read-Only"`
- **Group access**: `"None"`, `"Full"`, `"Restricted from Adding or Removing Groups"`
- **User access**: `"None"`, `"Full"`, `"Full Profile"`, `"Read-Only Profile"`, `"No Profile"`
- **Access device access**: `"None"`, `"Full"`, `"Associate User With Device"`, `"Read-Only"`
- **Phone number extension access**: `"None"`, `"Full"`, `"Assign To Services and Users"`
- **Service access**: `"None"`, `"Full"`, `"No Authorization"`, `"Read-Only"`

### Defaults

To make service provider admin policy modification more user-friendly, sensible defaults are automatically applied if you don't specify them. This means you only need to provide the `userId`, and the system will apply all default access settings.

**Service Provider Admin Policy Defaults:**

When you don't specify access levels, the following defaults are automatically applied:

| Field | Default Value |
|-------|---------------|
| `profileAccess` | `"Read-Only"` |
| `groupAccess` | `"None"` |
| `userAccess` | `"Read-Only Profile"` |
| `adminAccess` | `"Read-Only"` |
| `departmentAccess` | `"Full"` |
| `accessDeviceAccess` | `"Full"` |
| `phoneNumberExtensionAccess` | `"Assign To Services and Users"` |
| `callingLineIdNumberAccess` | `"Full"` |
| `serviceAccess` | `"No Authorization"` |
| `servicePackAccess` | `"None"` |
| `sessionAdmissionControlAccess` | `"Read-Only"` |
| `webBrandingAccess` | `"Full"` |
| `officeZoneAccess` | `"Full"` |
| `communicationBarringAccess` | `"Read-Only"` |
| `networkPolicyAccess` | `"None"` |
| `numberActivationAccess` | `"Full"` |
| `dialableCallerIDAccess` | `"Full"` |
| `verifyTranslationAndRoutingAccess` | `"None"` |

**Benefits of Defaults:**
- **Quick setup**: Apply standard policy settings with minimal configuration
- **Consistent policies**: Defaults ensure consistent access control across your organisation
- **Easy customisation**: Override any default by specifying a different value
- **Minimal configuration**: Only specify `userId` to apply all default policies

**Example - Minimal CSV (Defaults Applied):**

```csv
operation,userId
service.provider.admin.modify.policy,admin@company.com
```

This minimal example will modify the service provider admin policy with all default access settings applied. The administrator will have:
- `Read-Only` access to profiles, admin settings, session admission control, and communication barring
- `Full` access to departments, access devices, calling line ID numbers, web branding, office zones, number activation, and dialable caller ID
- `Read-Only Profile` access to users
- `Assign To Services and Users` access to phone number extensions
- `No Authorization` access to services
- `None` access to groups, service packs, network policies, and verify translation and routing

**Example - Custom CSV (Overriding Defaults):**

```csv
operation,userId,profileAccess,userAccess,adminAccess
service.provider.admin.modify.policy,admin@company.com,Full,Full Profile,Full
```

This example overrides the default values for `profileAccess`, `userAccess`, and `adminAccess` to `Full` or `Full Profile`, while all other fields will use their defaults.

### Example CSV Data

```csv
operation,userId,profileAccess,groupAccess,userAccess,adminAccess,departmentAccess,accessDeviceAccess,phoneNumberExtensionAccess,callingLineIdNumberAccess,serviceAccess,servicePackAccess,sessionAdmissionControlAccess,webBrandingAccess,officeZoneAccess,communicationBarringAccess,networkPolicyAccess,numberActivationAccess,dialableCallerIDAccess,verifyTranslationAndRoutingAccess
service.provider.admin.modify.policy,admin1@company.com,Full,Full,Full Profile,Full,Full,Full,Assign To Services and Users,Full,Full,Full,Read-Only,Full,Full,Read-Only,None,Full,Full,None
service.provider.admin.modify.policy,admin2@company.com,Read-Only,None,Read-Only Profile,Read-Only,Full,Full,Assign To Services and Users,Full,No Authorization,None,Read-Only,Full,Full,Read-Only,None,Full,Full,None
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

# Modify service provider admin policies from CSV
results = agent.bulk.modify_service_provider_admin_policy_from_csv(
    csv_path="path/to/your/service_provider_admin_policies.csv",
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
> When modifying service provider admin policies programmatically, you can omit any optional fields, and defaults will be automatically applied. Only the `user_id` field is required.

When modifying service provider admin policies programmatically, you can omit any optional fields, and defaults will be automatically applied. Only the `user_id` field is required.

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

# Define service provider admin policy data
service_provider_admin_policy_data = [
    {
        "operation": "service.provider.admin.modify.policy",
        "user_id": "admin1@company.com",
        "profile_access": "Full",
        "user_access": "Full Profile",
        "admin_access": "Full",
        "department_access": "Full"
    },
    {
        # All other fields will use defaults
        "operation": "service.provider.admin.modify.policy",
        "user_id": "admin2@company.com"
    }
]

# Modify service provider admin policies from data
results = agent.bulk.modify_service_provider_admin_policy_from_data(
    service_provider_admin_policy_data=service_provider_admin_policy_data,
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
service_provider_admin_policy_data = [
    {
        "operation": "service.provider.admin.modify.policy",
        "user_id": "admin@company.com"
    }
]

results = agent.bulk.modify_service_provider_admin_policy_from_data(
    service_provider_admin_policy_data=service_provider_admin_policy_data,
    dry_run=False
)
```

This will apply all default access settings as listed in the Defaults section above.

## Dry Run Mode

Both methods support dry run mode for validation:

```python
# Validate data without modifying policies
results = agent.bulk.modify_service_provider_admin_policy_from_csv(
    csv_path="path/to/your/service_provider_admin_policies.csv",
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

- **Template location**: Find the bulk sheet template in [`service.provider.admin.modify.policy.csv`](https://github.com/Fourteen-IP/mercury-ocip/tree/main/assets/bulk%20sheets)
- **Case conversion**: Column names are automatically converted from camelCase to snake_case
- **Default application**: All access level fields will use defaults if not specified
- **Required fields**: Only `userId` is required; all other fields are optional and will use defaults


