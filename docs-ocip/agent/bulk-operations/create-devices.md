# Create Devices

The devices bulk operation allows you to create multiple group-level access devices efficiently using either CSV files or direct method calls.

## Description

Access devices are physical or virtual endpoints (phones, ATAs, etc.) that connect to BroadWorks. This bulk operation creates multiple devices with their configuration in a single operation, supporting both CSV-based and programmatic approaches.

> **Note:** This operation creates devices at the group level. Service provider-level devices require different operations.

## Create from CSV

### Setup

1. **Get the template**: Find the bulk sheet template at [`device.create.csv`](https://github.com/Fourteen-IP/mercury-ocip/tree/main/assets/bulk%20sheets)
2. **Fill in your data**: Use the template to define your devices

### CSV Format

The CSV template includes these columns:

| Column | Description | Required | Example |
|--------|-------------|----------|---------|
| `operation` | Operation type | Yes | `"device.group.create"` |
| `serviceProviderId` | Service provider identifier | Yes | `"MyServiceProvider"` |
| `groupId` | Group identifier | Yes | `"SalesGroup"` |
| `deviceType` | Device type identifier | Yes | `"Polycom VVX 450"` |
| `deviceName` | Unique device name | Yes | `"sales-phone-01"` |
| `transportProtocol` | SIP transport protocol | No | `"UDP"` or `"TCP"` or `"TLS"` |
| `netAddress` | Network address (IP or FQDN) | No | `"192.168.1.100"` or `"phone.domain.com"` |
| `port` | SIP port number | No | `5060` |
| `outboundProxyServerNetAddress` | Outbound proxy server address | No | `"proxy.domain.com"` |
| `stunServerNetAddress` | STUN server address | No | `"stun.domain.com"` |
| `macAddress` | Device MAC address | No | `"00:11:22:33:44:55"` |
| `serialNumber` | Device serial number | No | `"SN123456789"` |
| `description` | Device description | No | `"Sales floor phone 1"` |
| `physicalLocation` | Physical location description | No | `"Building A, Floor 2, Desk 15"` |
| `useCustomUserNamePassword` | Use custom credentials | No | `true` or `false` |
| `accessDeviceCredentials.userName` | Device username (if custom) | No | `"deviceuser123"` |
| `accessDeviceCredentials.password` | Device password (if custom) | No | `"SecurePass123"` |

### Defaults

Unlike some other bulk operations, device creation has minimal defaults to ensure explicit configuration:

**No Automatic Defaults:**
- All device configuration must be explicitly provided
- This ensures devices are configured correctly for your network environment
- Only specify optional fields that are actually needed for your deployment

**Benefits of Explicit Configuration:**
- **Network control**: Ensures devices are configured for your specific network topology
- **Security**: Forces deliberate decisions about credentials and network settings
- **Flexibility**: Supports diverse deployment scenarios without assumptions

**Example - Minimal CSV:**
```csv
operation,serviceProviderId,groupId,deviceType,deviceName
device.group.create,MyServiceProvider,SalesGroup,Polycom VVX 450,sales-phone-01
```

This minimal example creates a device with only the required fields. Optional network and credential settings can be added as needed.

### Nested Object Notation

The `accessDeviceCredentials.*` notation allows you to configure custom device credentials with nested properties:

- `accessDeviceCredentials.userName`: Custom username for device authentication
- `accessDeviceCredentials.password`: Custom password for device authentication

> **Note:** Custom credentials are only used when `useCustomUserNamePassword` is set to `true`.

### Example CSV Data

```csv
operation,serviceProviderId,groupId,deviceType,deviceName,transportProtocol,netAddress,port,macAddress,serialNumber,description,physicalLocation,useCustomUserNamePassword,accessDeviceCredentials.userName,accessDeviceCredentials.password
device.group.create,MyServiceProvider,SalesGroup,Polycom VVX 450,sales-phone-01,UDP,192.168.1.100,5060,00:11:22:33:44:55,SN123456789,Sales floor phone 1,Building A Floor 2 Desk 15,true,salesphone01,SecurePass123
device.group.create,MyServiceProvider,SupportGroup,Cisco 8851,support-phone-01,TLS,phone01.support.company.com,5061,AA:BB:CC:DD:EE:FF,SN987654321,Support team phone,Building B Floor 1 Desk 5,true,supportphone01,AnotherSecurePass
device.group.create,MyServiceProvider,ExecutiveGroup,Polycom VVX 601,exec-phone-01,TCP,10.0.10.50,5060,11:22:33:44:55:66,SN555666777,Executive office phone,Executive Suite Room 301,false,,
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

# Create devices from CSV
results = agent.bulk.create_device_from_csv(
    csv_path="path/to/your/devices.csv",
    dry_run=False  # Set to True to validate without creating
)

# Process results
for result in results:
    if result["success"]:
        print(f"✅ Created device: {result['data']['deviceName']}")
    else:
        print(f"❌ Failed to create device: {result.get('error', 'Unknown error')}")
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

# Define device data
devices_data = [
    {
        "operation": "device.group.create",
        "service_provider_id": "MyServiceProvider", 
        "group_id": "SalesGroup",
        "device_type": "Polycom VVX 450",
        "device_name": "sales-phone-01",
        "transport_protocol": "UDP",
        "net_address": "192.168.1.100",
        "port": 5060,
        "mac_address": "00:11:22:33:44:55",
        "serial_number": "SN123456789",
        "description": "Sales floor phone 1",
        "physical_location": "Building A, Floor 2, Desk 15",
        "use_custom_user_name_password": True,
        "access_device_credentials": {
            "user_name": "salesphone01",
            "password": "SecurePass123"
        }
    },
    {
        "operation": "device.group.create", 
        "service_provider_id": "MyServiceProvider",
        "group_id": "SupportGroup",
        "device_type": "Cisco 8851",
        "device_name": "support-phone-01",
        "transport_protocol": "TLS",
        "net_address": "phone01.support.company.com",
        "port": 5061,
        "mac_address": "AA:BB:CC:DD:EE:FF",
        "serial_number": "SN987654321",
        "description": "Support team phone",
        "physical_location": "Building B, Floor 1, Desk 5",
        "use_custom_user_name_password": True,
        "access_device_credentials": {
            "user_name": "supportphone01",
            "password": "AnotherSecurePass"
        }
    },
    {
        "operation": "device.group.create",
        "service_provider_id": "MyServiceProvider",
        "group_id": "ExecutiveGroup",
        "device_type": "Polycom VVX 601",
        "device_name": "exec-phone-01",
        "transport_protocol": "TCP",
        "net_address": "10.0.10.50",
        "port": 5060,
        "mac_address": "11:22:33:44:55:66",
        "serial_number": "SN555666777",
        "description": "Executive office phone",
        "physical_location": "Executive Suite, Room 301",
        "use_custom_user_name_password": False
    }
]

# Create devices from data
results = agent.bulk.create_device_from_data(
    device_data=devices_data,
    dry_run=False  # Set to True to validate without creating
)

# Process results
for result in results:
    if result["success"]:
        print(f"✅ Created device: {result['data']['device_name']}")
    else:
        print(f"❌ Failed to create device: {result.get('error', 'Unknown error')}")
```

## Dry Run Mode

Both methods support dry run mode for validation:

```python
# Validate data without creating devices
results = agent.bulk.create_device_from_csv(
    csv_path="path/to/your/devices.csv",
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
        "data": {...},  # Original data for this device
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
- **API errors**: BroadWorks server errors (duplicate device names, invalid device types, etc.)
- **Network errors**: Connection issues
- **Credential errors**: Invalid custom credentials when `useCustomUserNamePassword` is `true`

Check the `success` field and `error` message in results for detailed error information.

## Notes

- **Template location**: Find the bulk sheet template in [`device.create.csv`](https://github.com/Fourteen-IP/mercury-ocip/tree/main/assets/bulk%20sheets)
- **Case conversion**: Column names are automatically converted from camelCase to snake_case
- **Device names**: Must be unique within the group
- **Device types**: Must be valid device types already configured in BroadWorks
- **Nested objects**: Use dot notation (e.g., `accessDeviceCredentials.userName`) for nested object properties
- **Boolean values**: Use `true`/`false` for boolean fields in CSV
- **Integer fields**: `port` is automatically converted to integer
- **MAC address format**: Use colon-separated format (e.g., `00:11:22:33:44:55`)
- **Credentials**: Custom credentials are only used when `useCustomUserNamePassword` is `true`
- **Post-creation assignment**: After creating devices, you'll need to assign them to users through the BroadWorks interface or additional API calls
- **Group-level only**: This operation creates group-level devices only; service provider-level devices require different operations

