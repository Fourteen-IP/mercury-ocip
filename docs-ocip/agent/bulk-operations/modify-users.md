# Modify Users

Bulk user modification lets you adjust existing profiles in batches, whether you need to flip a flag, refresh credentials, or realign services. The operation mirrors `UserConsolidatedModifyRequest22`, so anything the request supports, the sheet covers.

## Description

Use this when you have established users and need to push coordinated changes. You can cherry-pick single attributes (leave the rest blank) or replace entire lists such as SIP aliases and service packs.

## Modify from CSV

### Setup

1. **Template**: Grab [`user.modify.csv`](https://github.com/Fourteen-IP/mercury-ocip/tree/main/assets/bulk%20sheets) from the GitHub repository.
2. **Fill only what changes**: Empty cells leave existing values untouched. Put `none` or `null` to clear a field that supports nillable updates.

### CSV Format

Key columns you are likely to touch:

| Column | Description | Required | Example |
|--------|-------------|----------|---------|
| `operation` | Must be `user.modify` | Yes | `user.modify` |
| `userId` | Target user | Yes | `"john.doe@corp.com"` |
| `deleteExistingDevices` | Drop endpoints before reassigning | No | `true` |
| `unassignPhoneNumbers` | Scope for unassigning numbers | No | `"Group"` |
| `addPhoneNumberToGroup` | Auto-authorise new numbers | No | `true` |
| `newUserId` | Rename the user | No | `"j.doe@corp.com"` |
| `firstName` / `lastName` | Display names | No | `"John"` |
| `callingLineIdFirstName` / `callingLineIdLastName` | CLID overrides | No | `"Support"` |
| `nameDialingName.nameDialingFirstName` / `nameDialingName.nameDialingLastName` | Name-dialling pronunciation | No | `"JOHN"` |
| `hiraganaFirstName` / `hiraganaLastName` | Hiragana names | No | `"ジョン"` |
| `phoneNumber` / `extension` | Primary number updates | No | `"+441632960100"` |
| `callingLineIdPhoneNumber` | External CLID | No | `"+441632960999"` |
| `oldPassword` / `newPassword` | End-user password rotation | No | `"hunter2"` |
| `language` / `timeZone` | Localisation settings | No | `"en_US"` / `"Europe/London"` |
| `sipAliasList.sipAlias[0..2]` | Replace SIP alias list | No | `"john.doe"` |
| `alternateUserIdList.alternateUserId[0..2].alternateUserId` | Replace alternate IDs | No | `"jdoe"` |
| `alternateUserIdList.alternateUserId[0..2].description` | Alternate ID descriptions | No | `"Legacy ID"` |
| `userServiceList.userServiceServiceName[0..2].userServiceName` | Replace authorised user services (with optional quantity) | No | `"Executive"` |
| `userServiceList.userServiceServiceName[0..2].authorizedQuantity` | Service quantity | No | `5` |
| `servicePackList.servicePack[0..2].servicePackName` | Replace service packs (with optional quantity) | No | `"UnifiedCommunicator"` |
| `servicePackList.servicePack[0..2].authorizedQuantity` | Service pack quantity | No | `1` |
| `thirdPartyVoiceMailServerSelection` | Third-party VM selection | No | `"BroadSoft"` |
| `thirdPartyVoiceMailServerUserServer` | Third-party VM server | No | `"vm.example.com"` |
| `thirdPartyVoiceMailServerMailboxIdType` | Mailbox ID type | No | `"PhoneNumber"` |
| `thirdPartyVoiceMailMailboxURL` | Mailbox URL | No | `"https://vm.example.com/mailbox"` |
| `sipAuthenticationUserName` | SIP auth username | No | `"john.doe"` |
| `newSipAuthenticationPassword` / `OldSipAuthenticationPassword` | SIP auth credentials | No | `"supers3cret"` |
| `newPasscode` / `oldPasscode` | Voice portal PIN rotation | No | `"1234"` |
| `impPassword` | Integrated IMP password | No | `"impSecret!"` |
| `address.addressLine1`, `address.addressLine2`, `address.city`, `address.stateOrProvince`, `address.zipOrPostalCode`, `address.country` | Replace postal address | No | `"1 Fleet Place"` |
| `networkClassOfService` | Apply a new NCoS | No | `"Premium"` |
| `emailAddress`, `mobilePhoneNumber`, `pagerPhoneNumber` | Contact updates | No | `"john.doe@corp.com"` |
| `title`, `addressLocation`, `yahooId` | Misc profile details | No | `"Team Lead"` |
| `newUserExternalId` | Update external reference | No | `"ext-123"` |

### Endpoint Configuration

The user modify operation supports updating device endpoints. Use the `endpointType` field to specify which type of endpoint you're modifying:

| `endpointType` Value | Description |
|---------------------|-------------|
| `accessDeviceEndpoint` | Modify access device endpoint (SIP phone, etc.) |
| `TrunkAddressing` | Modify trunk addressing endpoint |
| `none` | Leave endpoint unchanged |
| `null` | Clear/remove the endpoint |

#### Access Device Endpoint Fields

When `endpointType` is set to `accessDeviceEndpoint`, you can configure:

| Column | Description | Required | Example |
|--------|-------------|----------|---------|
| `accessDeviceEndpoint.accessDevice.deviceName` | Device name | No | `"sip-phone-01"` |
| `accessDeviceEndpoint.accessDevice.deviceLevel` | Device level | No | `"Group"` |
| `accessDeviceEndpoint.protocol` | Protocol type | No | `"SIP"` |
| `accessDeviceEndpoint.deviceType` | Device type | No | `"Access Device"` |
| `accessDeviceEndpoint.portNumber` | Port number | No | `5060` |
| `accessDeviceEndpoint.status` | Device status | No | `"Active"` |
| `accessDeviceEndpoint.transportProtocol` | Transport protocol | No | `"UDP"` |
| `accessDeviceEndpoint.macAddress` | MAC address | No | `"00:11:22:33:44:55"` |
| `accessDeviceEndpoint.useCustomUserNamePassword` | Use custom credentials | No | `true` |
| `accessDeviceEndpoint.accessDeviceCredentials.userName` | Device username | No | `"device-user"` |
| `accessDeviceEndpoint.accessDeviceCredentials.password` | Device password | No | `"device-pass"` |
| `accessDeviceEndpoint.linePort` | Line port | No | `"1"` |
| `accessDeviceEndpoint.useHotline` | Enable hotline | No | `true` |
| `accessDeviceEndpoint.privateIdentity` | Private identity | No | `"sip:user@domain.com"` |
| `accessDeviceEndpoint.contact[0..2]` | Contact addresses (up to 3) | No | `"sip:user@192.168.1.100"` |
| `accessDeviceEndpoint.hotlineContact` | Hotline contact | No | `"sip:hotline@domain.com"` |

#### Trunk Addressing Fields

When `endpointType` is set to `TrunkAddressing`, you can configure:

| Column | Description | Required | Example |
|--------|-------------|----------|---------|
| `trunkAddressing.trunkGroupDeviceEndpoint.name` | Trunk group name | No | `"trunk-group-01"` |
| `trunkAddressing.trunkGroupDeviceEndpoint.linePort` | Trunk line port | No | `"1"` |

#### Shared Call Appearance Access Device Endpoint Fields

You can also modify shared call appearance endpoints:

| Column | Description | Required | Example |
|--------|-------------|----------|---------|
| `sharedCallAppearanceAccessDeviceEndpoint[0].accessDevice.deviceLevel` | Device level | No | `"Group"` |
| `sharedCallAppearanceAccessDeviceEndpoint[0].accessDevice.deviceName` | Device name | No | `"sca-device-01"` |
| `sharedCallAppearanceAccessDeviceEndpoint[0].deviceType` | Device type | No | `"Access Device"` |
| `sharedCallAppearanceAccessDeviceEndpoint[0].linePort` | Line port | No | `"1"` |
| `sharedCallAppearanceAccessDeviceEndpoint[0].IsActive` | Is active | No | `true` |
| `sharedCallAppearanceAccessDeviceEndpoint[0].allowOrigination` | Allow origination | No | `true` |
| `sharedCallAppearanceAccessDeviceEndpoint[0].allowTermination` | Allow termination | No | `true` |
| `sharedCallAppearanceAccessDeviceEndpoint[0].useCustomUserNamePassword` | Use custom credentials | No | `true` |
| `sharedCallAppearanceAccessDeviceEndpoint[0].accessDeviceCredentials.userName` | Device username | No | `"sca-user"` |
| `sharedCallAppearanceAccessDeviceEndpoint[0].accessDeviceCredentials.password` | Device password | No | `"sca-pass"` |
| `sharedCallAppearanceAccessDeviceEndpoint[0].useHotline` | Enable hotline | No | `true` |

The template already exposes slots for three aliases/service entries and shared call appearance endpoints. Add more columns (`sipAliasList.sipAlias[3]`, `sharedCallAppearanceAccessDeviceEndpoint[1]`, etc.) when you need deeper lists.

**Clearing values:** set the cell to `none` (exact lowercase) or `null` (exact lowercase) to wipe optional fields such as aliases, emails, addresses, or endpoints. Use `null` for explicit nillable field clearing.

### Example CSV Rows

**Basic profile update:**
```csv
operation,userId,firstName,lastName,callingLineIdFirstName,callingLineIdLastName,language,timeZone,emailAddress,deleteExistingDevices,userServiceList.userServiceServiceName[0].userServiceName,userServiceList.userServiceServiceName[0].authorizedQuantity,servicePackList.servicePack[0].servicePackName,sipAliasList.sipAlias[0],sipAliasList.sipAlias[1],sipAuthenticationUserName,newSipAuthenticationPassword,OldSipAuthenticationPassword
user.modify,john.doe@corp.com,Johnathan,Doe,Johnny,Doe,en_US,Europe/London,john.doe@corp.com,true,Executive,5,UnifiedCommunicator,johnny.doe,jdoe.voip,john.doe,newStrongPassword!,currentPassword!
```

**Device endpoint modification:**
```csv
operation,userId,endpointType,accessDeviceEndpoint.accessDevice.deviceName,accessDeviceEndpoint.accessDevice.deviceLevel,accessDeviceEndpoint.protocol,accessDeviceEndpoint.deviceType,accessDeviceEndpoint.portNumber,accessDeviceEndpoint.status,accessDeviceEndpoint.transportProtocol,accessDeviceEndpoint.linePort,accessDeviceEndpoint.contact[0]
user.modify,john.doe@corp.com,accessDeviceEndpoint,new-sip-device,Group,SIP,Access Device,5060,Active,UDP,1,sip:john@192.168.1.100
```

**Clearing endpoint (using null):**
```csv
operation,userId,endpointType
user.modify,jane.smith@corp.com,null
```

### Device vs Service Updates

- **Endpoints**: Reassigning endpoints or SIP aliases? Use the `deleteExistingDevices` flag to drop stale devices before the new assignments kick in. Set `endpointType` to `accessDeviceEndpoint` or `TrunkAddressing` to modify endpoints, or `null` to clear them.
- **Alias & service lists**: Replacement lists overwrite the entire existing set. Omit the column to leave the old list untouched.
- **Null support**: Use `null` (exact lowercase) to explicitly clear nillable fields like endpoints. Use `none` for other optional field clearing.

## Modify from Data (Method Call in IDE)

You can skip CSVs and send dictionaries straight to the bulk layer. Supply only the fields you want changed.

**Basic profile update:**
```python
from broadworks_sdk import Client, Agent

client = Client(
    host="broadworks.example.com",
    username="api-user",
    password="p@ssw0rd",
)
agent = Agent.get_instance(client)

payload = [
    {
        "operation": "user.modify",
        "user_id": "john.doe@corp.com",
        "first_name": "Johnathan",
        "delete_existing_devices": True,
        "sip_alias_list": {
            "sip_alias": ["johnny.doe", "jdoe.voip"]
        },
        "user_service_list": {
            "user_service_service_name": [
                {"user_service_name": "Executive", "authorized_quantity": 5}
            ]
        },
        "service_pack_list": {
            "service_pack": [
                {"service_pack_name": "UnifiedCommunicator"}
            ]
        }
    }
]

results = agent.bulk.modify_user_from_data(user_data=payload, dry_run=False)

for result in results:
    if result["success"]:
        print(f"✅ Updated {result['data']['user_id']}")
    else:
        print(f"❌ Failed {result['data']['user_id']}: {result.get('response')}")
```

**Device endpoint modification:**
```python
payload = [
    {
        "operation": "user.modify",
        "user_id": "john.doe@corp.com",
        "endpoint_type": "accessDeviceEndpoint",
        "access_device_endpoint": {
            "access_device": {
                "device_name": "new-sip-device",
                "device_level": "Group"
            },
            "protocol": "SIP",
            "device_type": "Access Device",
            "port_number": 5060,
            "status": "Active",
            "transport_protocol": "UDP",
            "line_port": "1",
            "contact_list": {
                "contact": ["sip:john@192.168.1.100"]
            }
        }
    }
]

results = agent.bulk.modify_user_from_data(user_data=payload, dry_run=False)
```

**Clearing endpoint:**
```python
from mercury_ocip.commands.base_command import OCINil

payload = [
    {
        "operation": "user.modify",
        "user_id": "jane.smith@corp.com",
        "endpoint_type": OCINil()  # or use "null" string in CSV
    }
]

results = agent.bulk.modify_user_from_data(user_data=payload, dry_run=False)
```

The same structure works with `dry_run=True` to validate without issuing OCI calls.

## Dry Run Mode

```python
agent.bulk.modify_user_from_csv(
    csv_path="path/to/user-updates.csv",
    dry_run=True,
)
```

Validation checks:
- Headers line up with known aliases from `UserConsolidatedModifyRequest22`
- Field types convert cleanly (booleans, integers)
- Required pairings (e.g. `OldSipAuthenticationPassword` when sending `newSipAuthenticationPassword`)
- Endpoint type choices are valid (`accessDeviceEndpoint`, `TrunkAddressing`, `none`, or `null`)
- Device endpoint configurations are properly structured

No external traffic occurs in dry-run mode; you just get a report of would-be issues.

## Response Format

Every bulk call returns a list like:

```python
[
    {
        "index": 0,
        "data": {...},       # original row
        "command": {...},    # generated request object
        "response": "",      # OCI response or error detail
        "success": True,
        "detail": None,
    },
    ...
]
```

Use this to split successes from failures and retry the bad ones after fixing data.

## Notes

- **Partial updates**: Blank cell == untouched field. `none` or `null` == wipe it (use `null` for explicit nillable field clearing).
- **Password rotations**: Provide both old and new values where the platform expects them (`oldPassword`/`newPassword`, SIP auth, voice portal).
- **List replacements**: Arrays replace wholesale—include the full desired list each time.
- **Device cleanup**: Combine `deleteExistingDevices=true` with new endpoint data to avoid duplicates.
- **Endpoint types**: Use `endpointType` to specify which endpoint type you're modifying (`accessDeviceEndpoint`, `TrunkAddressing`, `none`, or `null` to clear).
- **Null support**: The `null` value (exact lowercase) is converted to `OCINil()` for explicit nillable field clearing, particularly useful for endpoints.
- **Integer fields**: Fields like `portNumber` and `authorizedQuantity` are automatically converted to integers.
- **Case conversion**: Columns convert camelCase to snake_case during ingestion, so stick with the camelCase template headers.
- **Testing first**: Always run with `dry_run=True` before shipping a mass change—especially when unassigning numbers, deleting devices, or modifying endpoints.


