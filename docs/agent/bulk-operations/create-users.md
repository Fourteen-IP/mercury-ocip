# Create Users

The users bulk operation allows you to create multiple users efficiently using either CSV files or direct method calls.

## Description

User creation enables you to set up individual user accounts with various configurations including personal information, contact details, device assignments, and trunk addressing. This bulk operation creates multiple users with their associated devices and configuration in a single operation, supporting both CSV-based and programmatic approaches.

## Create from CSV

### Setup

1. **Get the template**: Find the bulk sheet template at [`user.create.csv`](https://github.com/Fourteen-IP/mercury-ocip/tree/main/assets/bulk%20sheets)
2. **Fill in your data**: Use the template to define your users

### CSV Format

The CSV template includes these columns:

| Column | Description | Required | Example |
|--------|-------------|----------|---------|
| `operation` | Operation type | Yes | `user.create` |
| `serviceProviderId` | Service provider identifier | Yes | `"MyServiceProvider"` |
| `groupId` | Group identifier | Yes | `"SalesGroup"` |
| `userId` | User identifier | Yes | `"john.doe@company.com"` |
| `firstName` | User's first name | Yes | `"John"` |
| `lastName` | User's last name | Yes | `"Doe"` |
| `callingLineIdFirstName` | First name for caller ID | Yes | `"John"` |
| `callingLineIdLastName` | Last name for caller ID | Yes | `"Doe"` |
| `hiraganaFirstName` | Hiragana first name | No | `"ジョン"` |
| `hiraganaLastName` | Hiragana last name | No | `"ドウ"` |
| `phoneNumber` | Phone number | No | `"+81355555555"` |
| `extension` | Extension | Yes | `"1234"` |
| `callingLineIdPhoneNumber` | Caller ID number | No | `"+81355555555"` |
| `password` | User password | Yes | `"password123"` |
| `language` | Language | No | `"Japanese"` |
| `timeZone` | Time zone | No | `"Asia/Tokyo"` |
| `title` | Job title | No | `"Sales Manager"` |
| `pagerPhoneNumber` | Pager number | No | `"+81355555556"` |
| `mobilePhoneNumber` | Mobile number | No | `"+81355555557"` |
| `emailAddress` | Email address | No | `"john.doe@company.com"` |
| `yahooId` | Yahoo ID | No | `"johndoe"` |
| `addressLocation` | Address location | No | `"Office"` |
| `address.addressLine1` | Address line 1 | No | `"123 Main Street"` |
| `address.addressLine2` | Address line 2 | No | `"Suite 100"` |
| `address.city` | City | No | `"Tokyo"` |
| `address.stateOrProvince` | State or province | No | `"Tokyo"` |
| `address.zipOrPostalCode` | ZIP or postal code | No | `"100-0001"` |
| `address.country` | Country | No | `"Japan"` |
| `networkClassOfService` | Network class of service | No | `"Premium"` |
| `accessDeviceEndpoint.accessDevice.deviceName` | Device name (existing) | No | `"existing-device-01"` |
| `accessDeviceEndpoint.accessDevice.deviceLevel` | Device level (existing) | No | `"Group"` |
| `accessDeviceEndpoint.protocol` | Protocol (new device) | No | `"SIP"` |
| `accessDeviceEndpoint.deviceType` | Device type (new device) | No | `"Access Device"` |
| `accessDeviceEndpoint.portNumber` | Port number (new device) | No | `5060` |
| `accessDeviceEndpoint.status` | Device status (new device) | No | `"Available"` |
| `accessDeviceEndpoint.transportProtocol` | Transport protocol (new device) | No | `"UDP"` |
| `accessDeviceEndpoint.macAddress` | MAC address (new device) | No | `"00:11:22:33:44:55"` |
| `accessDeviceEndpoint.useCustomUserNamePassword` | Use custom credentials | No | `true` |
| `accessDeviceEndpoint.accessDeviceCredentials.userName` | Device username | No | `"device_user"` |
| `accessDeviceEndpoint.accessDeviceCredentials.password` | Device password | No | `"device_pass"` |
| `accessDeviceEndpoint.linePort` | Line port | No | `"1"` |
| `accessDeviceEndpoint.useHotline` | Use hotline | No | `false` |
| `accessDeviceEndpoint.privateIdentity` | Private identity | No | `"sip:user@domain.com"` |
| `accessDeviceEndpoint.contact[0-2]` | Contact addresses (up to 3) | No | `"sip:user@192.168.1.100"` |
| `accessDeviceEndpoint.hotlineContact` | Hotline contact | No | `"sip:hotline@domain.com"` |
| `trunkAddressing.trunkGroupDeviceEndpoint.name` | Trunk group name | No | `"trunk-group-01"` |
| `trunkAddressing.trunkGroupDeviceEndpoint.linePort` | Trunk line port | No | `"1"` |
| `alias[0-2]` | Aliases (up to 3) | No | `"john.doe"` |
| `alternateUserId[0-2].alternateUserId` | Alternate user IDs (up to 3) | No | `"jdoe"` |

### Device Assignment Options

The user creation supports two different device assignment methods:

#### Option 1: Assign Existing Device

To assign a pre-existing device to the user, you only need to specify:
- `accessDeviceEndpoint.accessDevice.deviceName`: The name of the existing device
- `accessDeviceEndpoint.accessDevice.deviceLevel`: The level of the device (e.g., "Group", "Service Provider")

**Example for existing device:**
```csv
operation,serviceProviderId,groupId,userId,firstName,lastName,callingLineIdFirstName,callingLineIdLastName,extension,password,accessDeviceEndpoint.accessDevice.deviceName,accessDeviceEndpoint.accessDevice.deviceLevel
user.create,MyServiceProvider,SalesGroup,john.doe@company.com,John,Doe,John,Doe,1234,password123,existing-device-01,Group
```

#### Option 2: Create New Device

To create a new device and assign it to the user, you need to fill out the complete `accessDeviceEndpoint` details:

**Required fields for new device:**
- `accessDeviceEndpoint.protocol`
- `accessDeviceEndpoint.deviceType`
- `accessDeviceEndpoint.portNumber`
- `accessDeviceEndpoint.status`
- `accessDeviceEndpoint.transportProtocol`

**Example for new device:**
```csv
operation,serviceProviderId,groupId,userId,firstName,lastName,callingLineIdFirstName,callingLineIdLastName,extension,password,accessDeviceEndpoint.protocol,accessDeviceEndpoint.deviceType,accessDeviceEndpoint.portNumber,accessDeviceEndpoint.status,accessDeviceEndpoint.transportProtocol,accessDeviceEndpoint.macAddress
user.create,MyServiceProvider,SalesGroup,john.doe@company.com,John,Doe,John,Doe,1234,password123,SIP,Access Device,5060,Available,UDP,00:11:22:33:44:55
```

### Trunk Addressing

Alternatively, you can assign users to trunks using the `trunkAddressing` configuration. **Important**: You cannot use both device assignment and trunk addressing for the same user. Best practice is to remove the other values depending on what you're building.

**Example for trunk assignment:**
```csv
operation,serviceProviderId,groupId,userId,firstName,lastName,callingLineIdFirstName,callingLineIdLastName,extension,password,trunkAddressing.trunkGroupDeviceEndpoint.name,trunkAddressing.trunkGroupDeviceEndpoint.linePort
user.create,MyServiceProvider,SalesGroup,john.doe@company.com,John,Doe,John,Doe,1234,password123,trunk-group-01,1
```

### Defaults

To make user creation more user-friendly, many fields have sensible defaults that will be automatically applied if you don't specify them. This means you only need to provide the essential information, and the system will handle the rest.

**User Profile Defaults:**
- No defaults are currently configured for user creation
- All required fields must be explicitly provided

**Benefits of Explicit Configuration:**
- **Clear requirements**: You know exactly what information is needed
- **Flexible setup**: Configure only what you need for your specific use case
- **Consistent behaviour**: Explicit configuration ensures predictable user setup across your organisation
- **Easy migration**: Existing users can be recreated with their exact configuration

**Example - Minimal CSV (Existing Device):**
```csv
operation,serviceProviderId,groupId,userId,firstName,lastName,callingLineIdFirstName,callingLineIdLastName,extension,password,accessDeviceEndpoint.accessDevice.deviceName,accessDeviceEndpoint.accessDevice.deviceLevel
user.create,MyServiceProvider,SalesGroup,john.doe@company.com,John,Doe,John,Doe,1234,password123,existing-device-01,Group
```

This minimal example will create a user with an existing device assignment.

### Nested Object Notation

The `address.*` notation allows you to configure the user's address with nested properties like street, city, and postal code.

The `accessDeviceEndpoint.*` notation allows you to configure device settings for either existing device assignment or new device creation.

The `trunkAddressing.*` notation allows you to configure trunk group assignment for the user.

### Array Notation

The `alias[0]`, `alias[1]`, `alias[2]` notation allows you to specify multiple aliases for a single user. You can include as many `alias[N]` columns as needed, but it's recommended to only include the number of columns you actually need to avoid empty columns.

The `alternateUserId[0].alternateUserId`, `alternateUserId[1].alternateUserId`, `alternateUserId[2].alternateUserId` notation allows you to specify multiple alternate user IDs for a single user.

The `accessDeviceEndpoint.contact[0]`, `accessDeviceEndpoint.contact[1]`, `accessDeviceEndpoint.contact[2]` notation allows you to specify multiple contact addresses for device configuration.

### Example CSV Data

```csv
operation,serviceProviderId,groupId,userId,firstName,lastName,callingLineIdFirstName,callingLineIdLastName,extension,password,emailAddress,accessDeviceEndpoint.accessDevice.deviceName,accessDeviceEndpoint.accessDevice.deviceLevel,alias[0],alias[1]
user.create,MyServiceProvider,SalesGroup,john.doe@company.com,John,Doe,John,Doe,1234,password123,john.doe@company.com,existing-device-01,Group,john.doe,jdoe
user.create,MyServiceProvider,SalesGroup,jane.smith@company.com,Jane,Smith,Jane,Smith,1235,password456,jane.smith@company.com,existing-device-02,Group,jane.smith,jsmith
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

# Create users from CSV
results = agent.bulk.create_user_from_csv(
    csv_path="path/to/your/users.csv",
    dry_run=False  # Set to True to validate without creating
)

# Process results
for result in results:
    if result["success"]:
        print(f"✅ Created user: {result['data']['firstName']} {result['data']['lastName']}")
    else:
        print(f"❌ Failed to create user: {result.get('response', 'Unknown error')}")
```

## Create from Data (Method Call in IDE)

> **Note:** This is a highlighted note
> When creating users programmatically, you can omit any optional fields, but all required fields must be explicitly provided. The system will validate all required fields before processing.

When creating users programmatically, you can omit any optional fields, but all required fields must be explicitly provided. The system will validate all required fields before processing.

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

# Define user data
users_data = [
    {
        "operation": "user.create",
        "service_provider_id": "MyServiceProvider", 
        "group_id": "SalesGroup",
        "user_id": "john.doe@company.com",
        "first_name": "John",
        "last_name": "Doe",
        "calling_line_id_first_name": "John",
        "calling_line_id_last_name": "Doe",
        "extension": "1234",
        "password": "password123",
        "email_address": "john.doe@company.com",
        "access_device_endpoint": {
            "access_device": {
                "device_name": "existing-device-01",
                "device_level": "Group"
            }
        },
        "alias": ["john.doe", "jdoe"]
    },
    {
        "operation": "user.create", 
        "service_provider_id": "MyServiceProvider",
        "group_id": "SalesGroup",
        "user_id": "jane.smith@company.com",
        "first_name": "Jane",
        "last_name": "Smith",
        "calling_line_id_first_name": "Jane",
        "calling_line_id_last_name": "Smith",
        "extension": "1235",
        "password": "password456",
        "email_address": "jane.smith@company.com",
        "access_device_endpoint": {
            "protocol": "SIP",
            "device_type": "Access Device",
            "port_number": 5060,
            "status": "Available",
            "transport_protocol": "UDP",
            "mac_address": "00:11:22:33:44:56"
        },
        "alias": ["jane.smith", "jsmith"]
    }
]

# Create users from data
results = agent.bulk.create_user_from_data(
    user_data=users_data,
    dry_run=False  # Set to True to validate without creating
)

# Process results
for result in results:
    if result["success"]:
        print(f"✅ Created user: {result['data']['first_name']} {result['data']['last_name']}")
    else:
        print(f"❌ Failed to create user: {result.get('response', 'Unknown error')}")
```

## Dry Run Mode

Both methods support dry run mode for validation:

```python
# Validate data without creating users
results = agent.bulk.create_user_from_csv(
    csv_path="path/to/your/users.csv",
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
        "data": {...},  # Original data for this user
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
- **API errors**: BroadWorks server errors (duplicate users, invalid devices, etc.)
- **Network errors**: Connection issues

Check the `success` field and `response` field in results for detailed error information. When `success` is `False`, the `response` field will contain the error details.

## Notes

- **Device vs Trunk**: You cannot use both device assignment and trunk addressing for the same user. Choose one approach based on your requirements
- **Existing vs New Device**: For existing devices, only specify device name and level. For new devices, provide complete device configuration details
- **Template location**: Find the bulk sheet template in [`user.create.csv`](https://github.com/Fourteen-IP/mercury-ocip/tree/main/assets/bulk%20sheets)
- **Case conversion**: Column names are automatically converted from camelCase to snake_case
- **Empty values**: Empty array columns (alias[N], alternateUserId[N], etc.) are automatically filtered out
- **Nested objects**: Use dot notation (e.g., `address.city`, `accessDeviceEndpoint.protocol`) for nested object properties
- **Boolean values**: Use `true`/`false` for boolean fields in CSV
- **Integer fields**: `portNumber` and other numeric fields are automatically converted to integers
- **Required fields**: All required fields must be explicitly provided as no defaults are configured
