# Adding a New Bulk Operation

Guide for adding a new bulk operation entity type.

## Steps

### 1. Create Entity Operation Class

Create a new file in `src/mercury_ocip/bulk/` (e.g., `new_entity.py`):

```python
from mercury_ocip.bulk.base_operation import BaseBulkOperations
from mercury_ocip.client import BaseClient


class NewEntityBulkOperations(BaseBulkOperations):
    """Bulk operations for new entity type"""

    def __init__(self, client: BaseClient) -> None:
        super().__init__(client)
        
        self.operation_mapping = {
            "entity.create": {
                "command": "OCIClassName",
                "nested_types": {...},
                "defaults": {...},
                "integer_fields": [...]
            }
        }
```

### 2. Define Operation Mapping

Configure the `operation_mapping` dictionary:

#### Command

The OCI command class name from the dispatch table:

```python
"command": "UserConsolidatedAddRequest22"
```

#### Nested Types

Map nested data structures to OCI command classes:

```python
"nested_types": {
    # Simple nested type
    "address": "StreetAddress",
    
    # Array of nested types
    "alternate_user_id": "AlternateUserIdEntry",
    
    # Complex nested structure
    "access_device_endpoint": {
        "ConsolidatedAccessDeviceMultipleIdentityEndpointAndContactAdd22": {
            "access_device": "AccessDevice",
            "access_device_credentials": "DeviceManagementUserNamePassword16"
        }
    }
}
```

#### Defaults

Provide default values for optional fields:

```python
"defaults": {
    "type": "Basic",
    "policy": "Circular",
    "service_instance_profile": {
        "name": "Default Name",
        "calling_line_id_last_name": "Default"
    }
}
```

Defaults are merged into the data before command creation.

#### Integer Fields

List fields that should be converted from string to integer:

```python
"integer_fields": [
    "queue_length",
    "wrap_up_seconds",
    "port_number"
]
```

### 3. Register in BulkOperations Gateway

Add methods to `src/mercury_ocip/bulk/bulk_operations.py`:

```python
from mercury_ocip.bulk.new_entity import NewEntityBulkOperations

class BulkOperations:
    def __init__(self, client):
        self.client = client
        # ... existing entities ...
        self.new_entity = NewEntityBulkOperations(client)
    
    def create_new_entity_from_csv(
        self, csv_path: str, dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        return self.new_entity.execute_from_csv(csv_path, dry_run)
    
    def create_new_entity_from_data(
        self, entity_data: List[Dict[str, Any]], dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        return self.new_entity.execute_from_data(entity_data, dry_run)
```

### 4. Create CSV Template

Add a CSV template to `assets/bulk sheets/`:

- First row: Column headers
- Second row: Data types and allowed values
- Format: Use dot notation for nested objects, brackets for arrays

Example:
```csv
operation,serviceProviderId,entityField,nested.field,array[0]
entity.create,string,string,string,string
```

### 5. Add Tests

Create tests in `tests/bulk_operations/`:

```python
def test_csv_flow(self, mock_client):
    # Test CSV processing
    pass

def test_data_flow(self, mock_client):
    # Test direct data processing
    pass

def test_nested_types(self, mock_client):
    # Test nested type conversion
    pass

def test_defaults(self, mock_client):
    # Test default value application
    pass
```

## Data Processing Details

### Nested Object Notation

The parser handles these patterns:

- `serviceInstanceProfile.name` → `{"service_instance_profile": {"name": value}}`
- `address.city` → `{"address": {"city": value}}`

### Array Notation

- `alias[0]` → `{"alias": [value]}`
- `alias[0]`, `alias[1]` → `{"alias": [value0, value1]}`
- `accessDeviceEndpoint.contact[0]` → `{"access_device_endpoint": {"contact": [value]}}`
- `alternateUserId[0].alternateUserId` → `{"alternate_user_id": [{"alternate_user_id": value}]}`

### Type Conversions

Applied automatically during parsing:

- `"true"` / `"false"` → `True` / `False`
- `"none"` → filtered out (empty values)
- Integer fields → `int()` conversion
- Phone numbers starting with `+` → E.164 normalisation
- camelCase keys → snake_case keys

## Best Practices

1. **Use descriptive operation names** - e.g., `call.center.create`, `user.modify`
2. **Document defaults** - Comment which call center type or entity variant uses which defaults
3. **Test edge cases** - Empty arrays, missing nested objects, invalid data types
4. **Follow existing patterns** - Look at similar entities (e.g., call center for service entities)
5. **Validate command names** - Ensure the command class exists in the dispatch table

## Common Issues

### Command Not Found

Error: `Command X not found in dispatch table`

Solution: Verify the command class name matches exactly what's in `commands/commands.py`

### Nested Type Errors

Error: Validation errors on nested objects

Solution: Check nested type mappings match the command class structure

### Missing Defaults

Error: Required fields missing

Solution: Add missing fields to `defaults` or mark them as required in CSV template

