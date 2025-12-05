# Modify Users

Bulk user modification lets you adjust existing profiles in batches, whether you need to flip a flag, refresh credentials, or realign services. The operation mirrors `UserConsolidatedModifyRequest22`, so anything the request supports, the sheet covers.

## Description

Use this when you have established users and need to push coordinated changes. You can cherry-pick single attributes (leave the rest blank) or replace entire lists such as SIP aliases and service packs.

## Modify from CSV

### Setup

1. **Template**: Grab [`user.modify.csv`](https://github.com/Fourteen-IP/mercury-ocip/tree/main/assets/bulk%20sheets) from the GitHub repository.
2. **Fill only what changes**: Empty cells leave existing values untouched. Put `none` to clear a field that supports nillable updates.

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
| `phoneNumber` / `extension` | Primary number updates | No | `"+441632960100"` |
| `callingLineIdPhoneNumber` | External CLID | No | `"+441632960999"` |
| `oldPassword` / `newPassword` | End-user password rotation | No | `"hunter2"` |
| `sipAliasList.sipAlias[0..2]` | Replace SIP alias list | No | `"john.doe"` |
| `alternateUserIdList.alternateUserId[0..2].alternateUserId` | Replace alternate IDs | No | `"jdoe"` |
| `userServiceList.userServiceServiceName[0..2].userServiceName` | Replace authorised user services (with optional quantity) | No | `"Executive"` |
| `servicePackList.servicePack[0..2].servicePackName` | Replace service packs (with optional quantity) | No | `"UnifiedCommunicator"` |
| `thirdPartyVoiceMailServerSelection` | Third-party VM selection | No | `"BroadSoft"` |
| `sipAuthenticationUserName` | SIP auth username | No | `"john.doe"` |
| `newSipAuthenticationPassword` / `OldSipAuthenticationPassword` | SIP auth credentials | No | `"supers3cret"` |
| `newPasscode` / `oldPasscode` | Voice portal PIN rotation | No | `"1234"` |
| `impPassword` | Integrated IMP password | No | `"impSecret!"` |
| `address.addressLine1`, `address.city`, `address.country`, etc. | Replace postal address | No | `"1 Fleet Place"` |
| `networkClassOfService` | Apply a new NCoS | No | `"Premium"` |
| `emailAddress`, `mobilePhoneNumber`, `pagerPhoneNumber` | Contact updates | No | `"john.doe@corp.com"` |
| `title`, `addressLocation`, `yahooId` | Misc profile details | No | `"Team Lead"` |
| `newUserExternalId` | Update external reference | No | `"ext-123"` |

The template already exposes slots for three aliases/service entries. Add more columns (`sipAliasList.sipAlias[3]`, etc.) when you need deeper lists.

**Clearing values:** set the cell to `none` (exact lowercase) to wipe optional fields such as aliases, emails, or addresses.

### Example CSV Row

```csv
operation,userId,firstName,lastName,callingLineIdFirstName,callingLineIdLastName,language,timeZone,emailAddress,deleteExistingDevices,userServiceList.userServiceServiceName[0].userServiceName,userServiceList.userServiceServiceName[0].authorizedQuantity,servicePackList.servicePack[0].servicePackName,sipAliasList.sipAlias[0],sipAliasList.sipAlias[1],sipAuthenticationUserName,newSipAuthenticationPassword,OldSipAuthenticationPassword
user.modify,john.doe@corp.com,Johnathan,Doe,Johnny,Doe,en_US,Europe/London,john.doe@corp.com,true,Executive,5,UnifiedCommunicator,johnny.doe,jdoe.voip,john.doe,newStrongPassword!,currentPassword!
```

### Device vs Service Updates

- **Endpoints**: Reassigning SCA endpoints or SIP aliases? Use the `deleteExistingDevices` flag to drop stale devices before the new assignments kick in.
- **Alias & service lists**: Replacement lists overwrite the entire existing set. Omit the column to leave the old list untouched.

## Modify from Data (Method Call in IDE)

You can skip CSVs and send dictionaries straight to the bulk layer. Supply only the fields you want changed.

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

- **Partial updates**: Blank cell == untouched field. `none` == wipe it.
- **Password rotations**: Provide both old and new values where the platform expects them (`oldPassword`/`newPassword`, SIP auth, voice portal).
- **List replacements**: Arrays replace wholesale—include the full desired list each time.
- **Device cleanup**: Combine `deleteExistingDevices=true` with new endpoint data to avoid duplicates.
- **Case conversion**: Columns convert camelCase to snake_case during ingestion, so stick with the camelCase template headers.
- **Testing first**: Always run with `dry_run=True` before shipping a mass change—especially when unassigning numbers or deleting devices.


