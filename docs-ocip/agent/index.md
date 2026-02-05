# Agent

The `Agent` class gives you access to bulk operations and automation tasks. It uses a singleton pattern so there's one instance managing everything.

## Getting started

Access the `Agent` through `get_instance()`:

```python
from mercury_ocip import Client, Agent

client = Client(
    host="https://your-server.com",
    username="your_user",
    password="your_pass",
)

agent = Agent.get_instance(client)
```

> Always use `Agent.get_instance(client)` rather than `Agent(client)` directly. The singleton pattern keeps state consistent across your application.

## Bulk operations

Access bulk operations through `agent.bulk`. These let you create and modify BroadWorks entities from CSV files or Python data.

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

Available bulk operations:

* Users
* Devices
* Call Centers
* Hunt Groups
* Auto Attendants
* Call Pickup

See the [Bulk Operations Overview](../developer/bulk-operations/bulk-operations-overview.md) for details.

## Automation tasks

Access automation tasks through `agent.automate`. These handle common admin tasks that would otherwise require multiple API calls.

```python
# Find where an alias is assigned
result = agent.automate.find_alias(
    service_provider_id="SP",
    group_id="Group",
    alias="alias@sp.com"
)
```

See the [Automations](../agent/automations/) section for what's available.

## Plugin system

The `Agent` discovers and loads plugins automatically. Any installed package with a name starting with `mercury_ocip_` gets loaded, and its bulk operations and automations become available on `agent.bulk` and `agent.automate`.

List installed plugins:

```python
plugins = agent.list_plugins()
print(plugins)
```

## Complete example

```python
from mercury_ocip import Client, Agent

client = Client(
    host="https://broadworks.example.com",
    username="admin",
    password="password",
)

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