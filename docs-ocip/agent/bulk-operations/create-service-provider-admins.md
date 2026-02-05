# Create Service Provider Admins

The service provider admin bulk operation allows you to create multiple service provider administrators efficiently using either CSV files or direct method calls.

## Description

Service provider admin creation enables you to set up individual service provider administrator accounts with various configurations including personal information, administrator type, and authentication details. This bulk operation creates multiple service provider administrators with their associated configuration in a single operation, supporting both CSV-based and programmatic approaches.

## Create from CSV

### Setup

1. **Get the template**: Find the bulk sheet template at [`service.provider.admin.create.csv`](https://github.com/Fourteen-IP/mercury-ocip/tree/main/assets/bulk%20sheets)
2. **Fill in your data**: Use the template to define your service provider administrators

### CSV Format

The CSV template includes these columns:

| Column | Description | Required | Example |
|--------|-------------|----------|---------|
| `operation` | Operation type | Yes | `service.provider.admin.create` |
| `serviceProviderId` | Service provider identifier | Yes | `"MyServiceProvider"` |
| `administratorType` | Administrator type | Yes | `"Normal"` |
| `userId` | Service provider administrator user identifier | Yes | `"admin@company.com"` |
| `firstName` | Administrator's first name | No | `"John"` |
| `lastName` | Administrator's last name | No | `"Doe"` |
| `password` | Administrator password | No | `"password123"` |
| `language` | Language | No | `"English"` |

### Administrator Type Values

The `administratorType` field accepts the following values:
- `"Normal"` - Standard service provider administrator
- `"Customer"` - Customer-level administrator
- `"Password Reset Only"` - Administrator with password reset capabilities only

### Defaults

To make service provider admin creation more user-friendly, many fields have sensible defaults that will be automatically applied if you don't specify them. This means you only need to provide the essential information, and the system will handle the rest.

**Service Provider Admin Profile Defaults:**
- No defaults are currently configured for service provider admin creation
- All required fields must be explicitly provided

**Benefits of Explicit Configuration:**
- **Clear requirements**: You know exactly what information is needed
- **Flexible setup**: Configure only what you need for your specific use case
- **Consistent behaviour**: Explicit configuration ensures predictable admin setup across your organisation
- **Easy migration**: Existing service provider administrators can be recreated with their exact configuration

**Example - Minimal CSV:**
```csv
operation,serviceProviderId,administratorType,userId,firstName,lastName,password,language
service.provider.admin.create,MyServiceProvider,Normal,admin@company.com,John,Doe,password123,English
```

This minimal example will create a service provider administrator with all required fields specified.

### Example CSV Data

```csv
operation,serviceProviderId,administratorType,userId,firstName,lastName,password,language
service.provider.admin.create,MyServiceProvider,Normal,admin1@company.com,John,Doe,password123,English
service.provider.admin.create,MyServiceProvider,Customer,admin2@company.com,Jane,Smith,password456,English
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

# Create service provider admins from CSV
results = agent.bulk.create_service_provider_admin_from_csv(
    csv_path="path/to/your/service_provider_admins.csv",
    dry_run=False  # Set to True to validate without creating
)

# Process results
for result in results:
    if result["success"]:
        print(f"✅ Created service provider admin: {result['data']['user_id']}")
    else:
        print(f"❌ Failed to create service provider admin: {result.get('response', 'Unknown error')}")
```

## Create from Data (Method Call in IDE)

> **Note:** This is a highlighted note
> When creating service provider administrators programmatically, you can omit any optional fields, but all required fields must be explicitly provided. The system will validate all required fields before processing.

When creating service provider administrators programmatically, you can omit any optional fields, but all required fields must be explicitly provided. The system will validate all required fields before processing.

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

# Define service provider admin data
service_provider_admin_data = [
    {
        "operation": "service.provider.admin.create",
        "service_provider_id": "MyServiceProvider",
        "administrator_type": "Normal",
        "user_id": "admin1@company.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "password123",
        "language": "English"
    },
    {
        "operation": "service.provider.admin.create",
        "service_provider_id": "MyServiceProvider",
        "administrator_type": "Customer",
        "user_id": "admin2@company.com",
        "first_name": "Jane",
        "last_name": "Smith",
        "password": "password456",
        "language": "English"
    }
]

# Create service provider admins from data
results = agent.bulk.create_service_provider_from_data(
    service_provider_admin_data=service_provider_admin_data,
    dry_run=False  # Set to True to validate without creating
)

# Process results
for result in results:
    if result["success"]:
        print(f"✅ Created service provider admin: {result['data']['user_id']}")
    else:
        print(f"❌ Failed to create service provider admin: {result.get('response', 'Unknown error')}")
```

## Dry Run Mode

Both methods support dry run mode for validation:

```python
# Validate data without creating service provider admins
results = agent.bulk.create_service_provider_admin_from_csv(
    csv_path="path/to/your/service_provider_admins.csv",
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
        "data": {...},  # Original data for this service provider admin
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
- **API errors**: BroadWorks server errors (duplicate admins, invalid service providers, etc.)
- **Network errors**: Connection issues

Check the `success` field and `response` field in results for detailed error information. When `success` is `False`, the `response` field will contain the error details.

## Notes

- **Template location**: Find the bulk sheet template in [`service.provider.admin.create.csv`](https://github.com/Fourteen-IP/mercury-ocip/tree/main/assets/bulk%20sheets)
- **Case conversion**: Column names are automatically converted from camelCase to snake_case
- **Required fields**: All required fields must be explicitly provided as no defaults are configured


