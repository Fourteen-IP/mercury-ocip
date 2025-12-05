# Agent

The `Agent` class is the gateway object that provides unified access to bulk operations and automation tasks. It implements a singleton pattern to ensure a single instance manages all operations across your application.

## Getting Started

The `Agent` must be accessed via the `get_instance()` class method. This ensures you're working with the singleton instance:

```python
from mercury_ocip import Client, Agent

client = Client(
    host="https://your-server.com",
    username="your_user",
    password="your_pass",
)

agent = Agent.get_instance(client)
```

> **Important**: Always use `Agent.get_instance(client)` rather than instantiating directly with `Agent(client)`. The singleton pattern prevents multiple instances and ensures consistent state across your application.

## Available Functionality

### Bulk Operations

Access bulk operations through `agent.bulk`. This provides methods to create and modify BroadWorks entities from CSV files or Python data structures.

```python
# Create users from CSV
agent.bulk.create_user_from_csv("users.csv", dry_run=False)

# Create users from Python data
user_data = [
    {
        "operation": "user.create",
        "service_provider_id": "SP",
        "alias": ["user1@sp.com"]
    }
]
agent.bulk.create_users_from_data(user_data)

# Create devices from CSV
agent.bulk.create_device_from_csv("devices.csv")

# Create call centers from data
agent.bulk.create_call_center_from_data(call_center_data)
```

The `bulk` object provides operations for creating, modifying, and deleting core BroadWorks entities:
- Users
- Devices 
- Call Centers 
- Hunt Groups 
- Auto Attendants 
- Call Pickup

See the [Bulk Operations Overview](../developer/bulk_opertaions/bulk-operations-overview.md) for detailed information about bulk operations.

### Automation Tasks

Access automation tasks through `agent.automate`. These provide convenient methods for common administrative tasks.

```python
# Find where an alias is assigned
result = agent.automate.find_alias(
    service_provider_id="SP",
    group_id="Group",
    alias="alias@sp.com"
)
```

The `automate` object provides various automation tasks. See the [Automations](../agent/automations/) section for detailed documentation on each automation.

## Plugin System

The `Agent` automatically discovers and activates plugins installed in your environment. Any package with a name starting with `mercury_ocip_` will be loaded and its bulk operations and automation classes will be made available on the `agent.bulk` and `agent.automate` objects respectively.

You can list installed plugins:

```python
plugins = agent.list_plugins()
print(plugins)
```

## Complete Example

```python
from mercury_ocip import Client, Agent

# Initialise client
client = Client(
    host="https://broadworks.example.com",
    username="admin",
    password="password",
)

# Get agent instance
agent = Agent.get_instance(client)

# Use bulk operations
results = agent.bulk.create_users_from_data([
    {"operation": "user.create", "service_provider_id": "SP", "alias": ["user1@sp.com"]}
])

# Use automation tasks
alias_location = agent.automate.find_alias("SP", "Group", "user1@sp.com")

print(f"Created users: {len([r for r in results if r['success']])}")
print(f"Alias location: {alias_location}")
```

