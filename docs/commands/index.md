# Base Command Reference

The `base_command.py` module is where all the foundational types for Mercury's OCI-P interface live. Every BroadWorks command and data type you'll work with inherits from the base classes here, and they take care of the serialization, deserialization, and various protocol quirks you'd otherwise have to handle yourself.

---

## Core Type Hierarchy

```
OCIType (base for all types)
└── OCICommand
    ├── OCIRequest (commands sent to BroadWorks)
    └── OCIResponse (responses from BroadWorks)
        ├── OCIDataResponse (responses containing data)
        ├── SuccessResponse (simple success acknowledgment)
        └── ErrorResponse (error responses)
```

---

## OCIType

This is the base class that everything else builds on. It handles serialization and deserialization between Python objects, dictionaries, and XML, plus manages field naming conventions between Python's snake_case and OCI's camelCase.

When you instantiate any command or type, you can pass in keyword arguments and the class validates them against its type hints. This means you'll get immediate feedback if you try to set a field that doesn't exist:

```python
from mercury_ocip.commands.commands import UserGetRequest22

# Create a command with kwargs
command = UserGetRequest22(user_id="john@example.com")
```

One thing you'll notice pretty quickly is that you write everything in snake_case, but BroadWorks expects camelCase in the XML. The field alias system handles this translation automatically through metadata stored in the dataclass fields. When you call `get_field_aliases()`, it pulls this mapping from the field metadata so the parser knows how to convert between the two naming styles:

```python
# Python code uses snake_case
command = UserGetRequest22(user_id="john@example.com")

# Serializes to XML with camelCase
# <userId>john@example.com</userId>
```

### Serialization Methods

All OCIType subclasses support bidirectional conversion:

| Method | Input | Output | Use Case |
|--------|-------|--------|----------|
| `to_dict()` | self | `dict[str, Any]` | Convert command to Python dict (snake_case keys) |
| `to_xml()` | self | `str` | Convert command to XML string |
| `from_dict(cls, data)` | `dict` | `OCIType` | Create instance from dict |
| `from_xml(cls, xml)` | `str` | `OCIType` | Create instance from XML |

!!! tip "Async Variants"
    All methods have async equivalents (`to_dict_async()`, `to_xml_async()`, etc.) for use with `AsyncClient`.

### Example: Serialization Workflow

```python
from mercury_ocip.commands.commands import UserGetRequest22

# Create command
command = UserGetRequest22(user_id="john@example.com")

# Convert to dict (snake_case)
data = command.to_dict()
# {'user_id': 'john@example.com'}

# Convert to XML (camelCase)
xml = command.to_xml()
# '<command xmlns="" ... C:type="UserGetRequest22"><userId>john@example.com</userId></command>'

# Reconstruct from XML
parsed_command = UserGetRequest22.from_xml(xml)
assert parsed_command.user_id == "john@example.com"
```

---

## OCITable and OCITableRow

When BroadWorks needs to return lists of data (like users in a group or hunt groups in a service provider), it uses a table structure rather than just returning arrays. This is represented in Mercury as `OCITable`, which consists of column headings and rows of data.

The structure is straightforward - `OCITableRow` holds a list of column values, and `OCITable` combines these rows with their column headings:

```python
@dataclass
class OCITableRow:
    col: list[str]  # List of column values for this row

@dataclass
class OCITable:
    col_heading: list[str]  # Column names (camelCase from BroadWorks)
    row: list[OCITableRow]  # List of rows
```

You'll rarely need to construct these manually since BroadWorks creates them for you in responses. But if you did need to, it would look like this:

```python
from mercury_ocip.commands.base_command import OCITable, OCITableRow

table = OCITable(
    col_heading=["User Id", "First Name", "Last Name"],
    row=[
        OCITableRow(["john@example.com", "John", "Doe"]),
        OCITableRow(["jane@example.com", "Jane", "Smith"]),
    ]
)
```

The real utility comes from the `to_dict()` method, which transforms this table structure into a list of dictionaries. The column headings become dictionary keys (converted to snake_case), and each row becomes a separate dict:

```python
# Using the table from above
data = table.to_dict()

# Result:
# [
#     {'user_id': 'john@example.com', 'first_name': 'John', 'last_name': 'Doe'},
#     {'user_id': 'jane@example.com', 'first_name': 'Jane', 'last_name': 'Smith'}
# ]

# Access data naturally
for row in data:
    print(f"{row['first_name']} {row['last_name']}: {row['user_id']}")
```

In practice, you'll typically encounter tables when working with list responses. Commands that return tables will have a field ending in `_table`, and you can convert it immediately:

```python
from mercury_ocip.commands.commands import GroupGetListInSystemRequest

response = client.raw_command("GroupGetListInSystemRequest", service_provider_id="ent1")

# Response has group_table field (OCITable instance)
groups = response.group_table.to_dict()

# Now you have a list of dicts
for group in groups:
    print(f"Group: {group['group_id']} in {group['service_provider_id']}")
```

The Parser handles `OCITable` detection automatically. When it sees XML with `colHeading` and `row` elements, it constructs an `OCITable` instance. When you call `to_dict()` on a command that contains a table, the Parser recursively walks through the object and converts any tables it finds into lists of dictionaries.

---

## Nillable Types and OCINil

Here's something that trips people up initially: OCI-P distinguishes between not sending a field at all (BroadWorks ignores it and keeps the existing value) and explicitly setting a field to nil (BroadWorks clears it). This is represented in XML as `xsi:nil="true"`, and Mercury handles it through the `Nillable[T]` type and `OCINil` class.

The distinction matters when you're modifying existing entities. If you omit a field, BroadWorks leaves that field untouched. If you send nil, BroadWorks actively clears the value. For type hints, `Nillable[T]` is just an alias for `T`, so it doesn't change the actual type - it's more of a signal that the field supports explicit nil values:

```python
from mercury_ocip.commands.base_command import Nillable, OCINil

# Type definition in commands
type Nillable[T] = T

# Usage in command definition
@dataclass
class AlternateNumberEntry21:
    phone_number: Optional[Nillable[str]]
    extension: Optional[Nillable[str]]
```

The `OCINil` class itself is just an empty dataclass that acts as a sentinel value. When the parser sees it, it knows to serialize that field with `xsi:nil="true"`:

```python
@dataclass
class OCINil:
    pass
```

In practice, when you want to clear a field, you pass `OCINil()` as the value:

```python
from mercury_ocip.commands.commands import AlternateNumberEntry21
from mercury_ocip.commands.base_command import OCINil

# Set phone_number to nil (explicitly clear it)
entry = AlternateNumberEntry21(phone_number=OCINil())

# Serializes to:
# <phoneNumber xsi:nil="true"/>
```

Here's how different Python values translate to XML and what BroadWorks does with them:

| Python Value | XML Output | BroadWorks Interpretation |
|--------------|------------|---------------------------|
| `None` or field omitted | Field not in XML | Ignored, keeps existing value |
| `OCINil()` | `<field xsi:nil="true"/>` | Field explicitly cleared |
| `"value"` | `<field>value</field>` | Field set to "value" |
| `""` (empty string) | `<field xsi:nil="true"/>` | Treated as nil |

!!! warning "Empty String Behavior"
    Empty strings are automatically converted to `OCINil()` during serialization. This is intentional to handle BroadWorks' nil semantics, but it means you can't actually send an empty string - it'll always become nil.

The difference becomes clear when you're modifying users or other entities. Say you want to update just the first name - you omit `last_name` entirely. But if you want to explicitly remove the last name, you pass `OCINil()`:

```python
from mercury_ocip.commands.commands import UserModifyRequest22
from mercury_ocip.commands.base_command import OCINil

# Scenario 1: Update first name only (don't touch last name)
client.raw_command(
    "UserModifyRequest22",
    user_id="john@example.com",
    first_name="Johnny"  # last_name not sent, existing value preserved
)

# Scenario 2: Explicitly clear last name
client.raw_command(
    "UserModifyRequest22",
    user_id="john@example.com",
    last_name=OCINil()  # Sends <lastName xsi:nil="true"/>, clears the value
)

# Scenario 3: Update both
client.raw_command(
    "UserModifyRequest22",
    user_id="john@example.com",
    first_name="Johnny",
    last_name="Doe"
)
```

The Parser handles this bidirectionally - when serializing to XML, it converts `OCINil()` to `xsi:nil="true"`. When parsing XML responses, it converts `xsi:nil="true"` back into `OCINil()` instances.

---

## Namespace Handling

Every `OCIType` instance has a namespace attribute set to `"C"`. This is part of the OCI-P protocol's XML schema requirements:

```python
class OCIType:
    namespace = "C"
```

During XML serialization, this namespace gets used to declare the schema instance namespace and to set the command type. You'll see it in the generated XML as `xmlns:C` and in the `C:type` attribute:

```xml
<command xmlns="" xmlns:C="http://www.w3.org/2001/XMLSchema-instance" C:type="UserGetRequest22">
```

That `C:type` attribute is how BroadWorks knows which command you're sending. The type system handles all of this automatically, so you don't need to worry about it unless you're debugging XML issues.

---

## Request and Response Classes

Commands you send to BroadWorks inherit from `OCIRequest`, while responses come back as subclasses of `OCIResponse`. The distinction is mostly organizational, but it helps with type checking and understanding data flow.

Requests are straightforward - you instantiate them with the fields you need:

```python
from mercury_ocip.commands.commands import UserGetRequest22

request = UserGetRequest22(user_id="john@example.com")
```

Responses come in a few flavors. Most of the time you'll get back `OCIDataResponse` instances that contain the actual data you requested. Simple operations might just return `SuccessResponse` to acknowledge completion. And when something goes wrong, you get an `ErrorResponse` with details about what failed:

```python
class ErrorResponse(OCIResponse):
    errorCode: Optional[int] = None
    summary: str
    summaryEnglish: str
    detail: Optional[str] = None
```

Error handling usually means checking the response type before trying to access its data. If you get an `ErrorResponse`, you can pull out the error code and message:

```python
response = client.raw_command("UserGetRequest22", user_id="invalid@example.com")

if isinstance(response, ErrorResponse):
    print(f"Error {response.errorCode}: {response.summary}")
    print(f"Detail: {response.detail}")
```

---

## Common Quirks and Patterns

### Field Initialization

When you create a command without providing all fields, any missing fields get initialized to `None`. This is useful for partial command construction, though keep in mind most commands have required fields that you'll need to fill in before sending:

```python
command = UserGetRequest22()
assert command.user_id is None  # True
```

### Runtime Validation

Field validation happens when you instantiate a command, not when you send it. If you try to set a field that doesn't exist on that command type, you'll get a `ValueError` immediately:

```python
try:
    command = UserGetRequest22(invalid_field="value")
except ValueError as e:
    print(f"Error: {e}")  # "Unknown field: invalid_field"
```

### Non-Dataclass Handling

Most types are dataclasses, but some of the generated types might not be. The `get_field_aliases()` method accounts for this with a safe fallback that returns an empty dict if it encounters a non-dataclass:

```python
def get_field_aliases(self):
    cls = self.__class__
    if not is_dataclass(cls):
        return {}  # Safe fallback
    return {f.name: f.metadata.get("alias", f.name) for f in fields(cls)}
```

### Field Naming

The field alias system preserves the exact casing from the BroadWorks schemas. You write snake_case in Python, it becomes camelCase in XML:

```python
# Python: snake_case
user_id: str = field(metadata={"alias": "userId"})

# XML: camelCase
# <userId>...</userId>
```

The Parser handles this conversion bidirectionally, so you never need to manually use camelCase in your Python code.

### Sync and Async

Every serialization method has both sync and async versions. If you're using the regular `Client`, use the sync methods. If you're using `AsyncClient`, use the async variants:

```python
# Sync
dict_data = command.to_dict()
xml_string = command.to_xml()

# Async
dict_data = await command.to_dict_async()
xml_string = await command.to_xml_async()
```

---

## Complete Example

Putting it all together:

```python
from mercury_ocip.client import Client
from mercury_ocip.commands.commands import (
    GroupGetListInSystemRequest,
    UserModifyRequest22,
    SuccessResponse
)
from mercury_ocip.commands.base_command import OCITable

# Initialize client
client = Client(
    host="broadworks.example.com",
    port=2209,
    username="admin",
    password="password",
    conn_type="SOAP"
)

try:
    # Execute a command that returns a table
    response = client.raw_command(
        "GroupGetListInSystemRequest",
        service_provider_id="ent1"
    )

    # Response has group_table (OCITable)
    if hasattr(response, 'group_table') and response.group_table:
        # Convert to list of dicts
        groups = response.group_table.to_dict()

        for group in groups:
            print(f"   Group ID: {group['group_id']}")
            print(f"   Group Name: {group.get('group_name', 'N/A')}")

    # Example with Nillable: Clear a user's extension
    response = client.raw_command(
        "UserModifyRequest22",
        user_id="john@example.com",
        extension=""  # Explicitly clear extension, could also use "OCINil()"
    )

    if isinstance(response, SuccessResponse):
        print("Extension cleared successfully")

finally:
    client.disconnect()
```

---

## Things Worth Knowing (tldr)

When you get an `OCITable` response, convert it to a dict right away with `to_dict()`. You'll find it much easier to work with as a list of dictionaries than dealing with the table structure directly.

If you need to explicitly clear a field value (not just leave it unchanged), use `OCINil()` instead of `None`. Passing `None` or omitting the field tells BroadWorks to ignore it, while `OCINil()` tells it to actively clear the value.

Stick to snake_case in your Python code and let the Parser handle the camelCase conversion. You shouldn't need to manually write camelCase field names - if you find yourself doing that, something's probably wrong.

Check response types with `isinstance()` before accessing data. BroadWorks can return errors as `ErrorResponse` objects, and trying to access data fields on an error response will fail.

If you're working with `AsyncClient`, remember to use the async method variants (the ones ending in `_async`). Mixing sync and async methods will cause issues.

Keep in mind that empty strings get converted to `OCINil()` automatically during serialization. This is intentional for BroadWorks compatibility, but it means you can't actually send an empty string value - it'll always become nil.

You'll almost never need to manually construct `OCITable` instances. BroadWorks creates them in responses, and you just convert them with `to_dict()` when you need to work with the data.

---

## Related Documentation

- [Client Documentation](client/client.md) - Learn how commands are executed
- [Async Client Documentation](client/async-client.md) - Asynchronous command execution