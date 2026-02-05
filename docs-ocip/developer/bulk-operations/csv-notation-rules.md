# CSV Column Notation Rules for Bulk Operations

This document describes the notation rules for CSV column headers used in Mercury OCIP bulk operations. These rules allow you to represent complex nested data structures and arrays in a flat CSV format.

## Overview

The CSV parser dynamically builds Python dictionaries that match the structure of OCI-P commands. Column headers use a special notation to indicate nested objects, arrays, and combinations thereof.

## Basic Rules

### 1. Simple Fields

A column header with no special characters represents a top-level field:

```csv
userId,firstName,lastName
john@example.com,John,Doe
```

Result:
```python
{
    "user_id": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
}
```

### 2. Nested Objects (Dot Notation)

Use `.` to indicate nested objects. Each dot represents one level of nesting:

```csv
address.city,address.country
London,UK
```

Result:
```python
{
    "address": {
        "city": "London",
        "country": "UK"
    }
}
```

### 3. Arrays (Bracket Notation)

Use `[index]` to indicate array elements. Indices are zero-based:

```csv
alias[0],alias[1],alias[2]
john.doe,jdoe,johnny
```

Result:
```python
{
    "alias": ["john.doe", "jdoe", "johnny"]
}
```

### 4. Arrays with Objects

Combine bracket and dot notation to represent arrays containing objects:

```csv
alternateUserId[0].alternateUserId,alternateUserId[1].alternateUserId
john.alt@example.com,jdoe.alt@example.com
```

Result:
```python
{
    "alternate_user_id": [
        {"alternate_user_id": "john.alt@example.com"},
        {"alternate_user_id": "jdoe.alt@example.com"}
    ]
}
```

## Advanced Patterns

### Multiple Levels of Nesting

You can nest objects multiple levels deep using multiple dots:

```csv
accessDeviceEndpoint.accessDevice.deviceName,accessDeviceEndpoint.accessDevice.deviceLevel
DEVICE001,Group
```

Result:
```python
{
    "access_device_endpoint": {
        "access_device": {
            "device_name": "DEVICE001",
            "device_level": "Group"
        }
    }
}
```

### Nested Objects with Arrays

Arrays can appear at any level of nesting:

```csv
serviceInstanceProfile.alias[0],serviceInstanceProfile.alias[1]
main.contact,backup.contact
```

Result:
```python
{
    "service_instance_profile": {
        "alias": ["main.contact", "backup.contact"]
    }
}
```

### Arrays of Objects with Multiple Fields

Each array element can have multiple fields:

```csv
servicePack[0].servicePackName,servicePack[1].servicePackName,servicePack[2].servicePackName
Standard,Premium,Enterprise
```

Result:
```python
{
    "service_pack": [
        {"service_pack_name": "Standard"},
        {"service_pack_name": "Premium"},
        {"service_pack_name": "Enterprise"}
    ]
}
```

### Deep Nesting with Arrays at Multiple Levels

You can combine all patterns for deeply nested structures:

```csv
trunkAddressing.trunkGroupDeviceEndpoint.name,trunkAddressing.trunkGroupDeviceEndpoint.linePort
TrunkGroup1,1
```

With arrays:
```csv
accessDeviceEndpoint.contact[0],accessDeviceEndpoint.contact[1],accessDeviceEndpoint.contact[2]
sip:user1@domain.com,sip:user2@domain.com,sip:user3@domain.com
```

Result:
```python
{
    "trunk_addressing": {
        "trunk_group_device_endpoint": {
            "name": "TrunkGroup1",
            "line_port": "1"
        }
    },
    "access_device_endpoint": {
        "contact": [
            "sip:user1@domain.com",
            "sip:user2@domain.com",
            "sip:user3@domain.com"
        ]
    }
}
```

## Parsing Logic

The parser follows these steps:

1. **Tokenization**: Split the column key into segments by dots, preserving array indices
2. **Path Navigation**: For each segment, navigate or create the nested structure
3. **Value Assignment**: Set the value at the final destination
4. **Array Cleanup**: Remove None padding used during construction

### Key Concepts

- **Dots (`.`)** indicate object nesting - the part before the dot is the parent object, the part after is a field or nested object
- **Brackets (`[n]`)** indicate array indices - can appear at any nesting level
- **Order matters** - array indices should be sequential starting from 0
- **Type inference** - the parser determines whether to create a dict or list based on the notation used

## Real-World Examples

### User Creation

From `user.create.csv`:

```csv
operation,userId,address.city,address.country,alternateUserId[0].alternateUserId,servicePack[0].servicePackName
user.create,john@example.com,London,UK,john.alt@example.com,Standard
```

### Call Center Creation

From `call.center.create.csv`:

```csv
operation,serviceUserId,serviceInstanceProfile.name,serviceInstanceProfile.phoneNumber,serviceInstanceProfile.alias[0]
call.center.create,support@example.com,Support Queue,+442071234567,support.main
```

### Device Access Configuration

```csv
operation,accessDeviceEndpoint.accessDevice.deviceName,accessDeviceEndpoint.accessDeviceCredentials.userName,accessDeviceEndpoint.accessDeviceCredentials.password
device.create,PHONE001,device_user,secure_pass
```

## Tips and Best Practices

1. **Use consistent casing**: Column headers are automatically converted to snake_case
2. **Sequential indices**: Always start arrays at index 0 and increment sequentially
3. **Sparse arrays**: If you skip indices, None values will be filtered out automatically
4. **Complex structures**: For very complex nested structures, refer to the command definition in `commands.py`
5. **Type mapping**: The `operation_mapping` in bulk operation classes defines `nested_types` that correspond to OCI-P types

## Special Field Types

### Integer Fields

Fields listed in `integer_fields` for an operation are automatically converted:

```python
"integer_fields": ["port_number", "queue_length"]
```

### Boolean Fields

String values like "true", "false", "yes", "no" are automatically converted to booleans.

### Phone Numbers

Strings starting with `+` are normalised to E.164 format.

## Troubleshooting

### Common Issues

**Problem**: Array not created correctly
- **Solution**: Ensure indices are sequential starting from 0

**Problem**: Nested object not recognised
- **Solution**: Check for typos in field names and ensure proper dot notation

**Problem**: Type mismatch error
- **Solution**: Verify the field name matches the command definition in the `operation_mapping`

### Validation

The bulk operations use Pydantic models for validation. If your CSV structure doesn't match the expected command structure, you'll receive a validation error with details about what's wrong.

## Reference

For implementation details, see:
- `src/mercury_ocip/bulk/base_operation.py` - Core parsing logic
- `src/mercury_ocip/bulk/user.py` - User operation mappings
- `src/mercury_ocip/bulk/call_center.py` - Call center operation mappings
- `src/mercury_ocip/commands/commands.py` - OCI-P command definitions

