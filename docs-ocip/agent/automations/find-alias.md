# Find Alias

The alias finder automation searches for alias assignments across multiple entity types within a group.

> **Note**: This automation can also be executed via the CLI. See the [CLI documentation](../../CLI/index.md) for details on running automations from the command line.

## Description

When you need to locate which entity (Call Center, Hunt Group, Auto Attendant, or User) is using a specific alias, this automation searches through all entity types and returns the matching entity. It handles aliases with or without domain parts and checks both direct alias fields and nested service instance profile configurations.

## Usage

```python
from mercury_ocip import Client, Agent

# Initialise client
client = Client(
    host="your-broadworks-server.com",
    username="your-username",
    password="your-password"
)

# Get Agent object
agent = Agent.get_instance(client)

# Execute search
result = agent.automate.find_alias(
    service_provider_id="MyServiceProvider",
    group_id="SalesGroup",
    alias="0"  # Domain part is optional
)

# Check results
if result.ok:
    entity = result.payload.entity
    print(f"✅ Alias found: {entity}")
else:
    print(f"❌ {result.message}")
```

## Search Behaviour

The finder searches entity types in this order:
1. **Call Centers** - Checks all call centers in the group
2. **Hunt Groups** - Checks all hunt groups in the group
3. **Auto Attendants** - Checks all auto attendants in the group
4. **Users** - Checks all users in the group

The search stops and returns as soon as a match is found.

## Alias Matching

- Aliases are matched by their local part only (everything before `@`)
- Input alias `0` or `*56` will match `0@domain.com` and `*56@domain.com`
- Case-sensitive matching
- Supports entities with single or multiple aliases

## Response Format

The automation returns an `AutomationResult[AliasResult]`:

```python
{
    "ok": True,  # Whether alias was found
    "message": "Alias found.",  # Status message
    "payload": {
        "found": True,  # Whether alias was found
        "entity": {...},  # The matching OCIResponse entity
        "message": "Alias found."  # Status message
    }
}
```

When the alias is not found:
```python
{
    "ok": False,
    "message": "Alias not found.",
    "payload": {
        "found": False,
        "entity": None,
        "message": "Alias not found."
    }
}
```

## Example: Find and Update

```python
# Find alias
result = agent.automate.find_alias(
    service_provider_id="SP1",
    group_id="Sales",
    alias="sales.main"
)

if result.ok:
    entity = result.payload.entity
    
    # Determine entity type and take action
    if hasattr(entity, 'service_instance_profile'):
        entity_type = entity.service_instance_profile.get('type', 'Unknown')
    else:
        entity_type = type(entity).__name__
    
    print(f"Found alias on {entity_type}")
    # Proceed with updates or other operations
else:
    print("Alias available for assignment")
```

## Notes

- The search fetches all entities of each type, which may be slow for large groups
- Only searches within the specified group, not across the entire service provider
- Returns the first match found; does not check for duplicates across entity types
- Requires appropriate permissions to read entity details

