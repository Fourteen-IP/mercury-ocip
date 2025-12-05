# Bulk Operations Reference

Quick reference for bulk operations implementation details.

## BaseBulkOperations Methods

### Public Methods

#### `execute_from_csv(csv_path: str, dry_run: bool = False)`

Read CSV file and process each row.

- Reads CSV using `FileHandler.read_csv_to_dict()`
- Parses each row through `_parse_csv()`
- Executes via `execute_from_data()`

#### `execute_from_data(data: List[Dict[str, Any]], dry_run: bool = False)`

Process Python data structures.

- Iterates through data list
- Creates OCI command for each item
- Executes command (unless dry_run)
- Returns structured results

### Private Methods

#### `_parse_csv(data: List[Dict[str, Any]])`

Parse CSV rows into structured dictionaries.

- Converts camelCase to snake_case
- Handles nested objects, arrays, and type conversions
- Returns list of processed dictionaries

#### `_process_row(row: Dict[str, Any])`

Process a single CSV row.

- Applies type conversions (boolean, integer, phone)
- Handles nested object notation (`field.subfield`)
- Handles array notation (`field[0]`, `field[0].subfield`)
- Returns processed dictionary

#### `_create_command(data: Dict[str, Any], operation: str)`

Create OCI command object from data.

- Looks up operation in `operation_mapping`
- Applies defaults
- Converts nested types to command objects
- Instantiates command class
- Returns `OCICommand` instance

#### `_handle_nested_types(processed_data, nested_types)`

Convert nested dictionaries to OCI command objects.

- Recursively processes nested structures
- Instantiates command classes from dispatch table
- Handles arrays of nested types
- Returns data with nested objects converted

#### `_handle_defaults(data, defaults)`

Apply default values to missing fields.

- Merges defaults recursively
- Only applies if field is missing
- Supports nested default structures

## Operation Mapping Structure

```python
{
    "operation.name": {
        "command": str,                    # Required: OCI class name
        "nested_types": Dict[str, Any],    # Optional: Nested type mappings
        "defaults": Dict[str, Any],       # Optional: Default values
        "integer_fields": List[str]        # Optional: Fields to convert to int
    }
}
```

### Nested Types Format

**Simple nested type:**
```python
"address": "StreetAddress"
```

**Array of nested types:**
```python
"alternate_user_id": "AlternateUserIdEntry"
```

**Complex nested structure:**
```python
"access_device_endpoint": {
    "ConsolidatedAccessDeviceMultipleIdentityEndpointAndContactAdd22": {
        "access_device": "AccessDevice",
        "access_device_credentials": "DeviceManagementUserNamePassword16"
    }
}
```

## Data Processing Patterns

### Regex Patterns

The parser uses these regex patterns to identify data structures:

- **Top-level array**: `r"([\w.]+)\[(\d+)\]"`
- **Nested object**: `r"([\w.]+)\.(\w+)"`
- **Nested array**: `r"([\w.]+)\.(\w+)\[(\d+)\]"`
- **Array with object**: `r"([\w.]+)\[(\d+)\]\.(\w+)"`

### Type Conversions

Automatic conversions applied:

| CSV Value | Python Type | Notes |
|-----------|-------------|-------|
| `"true"` / `"false"` | `bool` | Case insensitive |
| `"none"` | Filtered | Empty values removed |
| `"+1234567890"` | `str` | E.164 normalised |
| Integer field value | `int` | Fields in `integer_fields` |
| camelCase key | snake_case key | All keys converted |

### Data Flow

```
CSV Row / Dict
  ↓
_parse_csv() → _process_row()
  ↓
Processed Dict (snake_case, type conversions)
  ↓
_create_command() → _handle_defaults() → _handle_nested_types()
  ↓
OCICommand Instance
  ↓
_execute_command() → client.command()
  ↓
Response / ErrorResponse
  ↓
Result Dict
```

## Result Structure

```python
{
    "index": int,              # Row index in input data
    "data": Dict[str, Any],    # Original processed data
    "command": OCICommand,    # Generated command object
    "response": OCIResponse,  # API response (None if dry_run)
    "success": bool,          # True if operation succeeded
    "error": str | None,      # Error message if failed
    "detail": Any | None      # Additional error details
}
```

## Error Handling

### Validation Errors

Caught during command creation:
- Missing required fields
- Invalid data types
- Pydantic validation failures

Error stored in `error` field, `success` = `False`

### API Errors

Returned as `ErrorResponse`:
- BroadWorks server errors
- Duplicate entities
- Invalid configurations

Error details in `response.summary` and `response.detail`

### Network Errors

Caught during command execution:
- Connection failures
- Timeout errors

Exception message stored in `error` field

## Dispatch Table

Commands are resolved through `client._dispatch_table`:

```python
command_class = self.client._dispatch_table.get("CommandClassName")
```

Ensure command class names in `operation_mapping` match entries in the dispatch table.

## Testing

Common test patterns:

```python
# Mock client with dispatch table
client._dispatch_table = {
    "CommandClassName": CommandClass
}

# Test CSV flow
results = entity_ops.execute_from_csv("test.csv", dry_run=False)

# Test data flow
results = entity_ops.execute_from_data([{...}], dry_run=False)

# Test validation
results = entity_ops.execute_from_data([{...}], dry_run=True)
```

