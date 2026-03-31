# Enterprise Number Block

Blocks a number across every group and department in an enterprise in one call.

> **Note**: This automation can also be run via the CLI. See the [CLI documentation](../../CLI/index.md) for details.

## Description

Normally blocking a number enterprise-wide means logging into each group, adding the digit pattern, and setting the incoming calling plan permission to deny — one group at a time. This automation does all of that in a single call.

For each group it:
1. Adds the digit pattern to the group's calling plan
2. Sets the incoming calling plan permission to deny at group level and for every department in that group

If BroadWorks rejects the operation for a specific group (e.g. the pattern already exists), that group is skipped with a warning and the rest of the enterprise is still processed.

## Usage

```python
from mercury_ocip import Client, Agent

client = Client(
    host="your-broadworks-server.com",
    username="your-username",
    password="your-password"
)

agent = Agent.get_instance(client)

result = agent.automate.block_number_in_enterprise(
    enterprise_id="MyEnterprise",
    number="01234567890"
)

if result.ok:
    print(f"Blocked: {result.payload.digit_plan.digit_pattern_name}")
else:
    print("Block failed")
```

## Response format

Returns an `AutomationResult[EnterpriseNumBlockResult]`:

```python
{
    "ok": True,
    "payload": {
        "digit_plan": {
            "digit_pattern_name": "Block 01234567890",
            "allow": False
        }
    }
}
```

## Notes

- The `number` field is used as the digit pattern directly — wildcards are supported if your BroadWorks instance allows them
- Groups rejected by BroadWorks are skipped and logged as warnings, not errors
- Only group-level departments are targeted; enterprise departments shared across groups are not modified
