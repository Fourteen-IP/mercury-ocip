# User Digest

The user digest automation generates a comprehensive summary of user information, including profile details, call forwarding settings, device registrations, and group memberships.

> **Note**: This automation can also be executed via the CLI. See the [CLI documentation](../../CLI/index.md) for details on running automations from the command line.

## Description

When you need a complete overview of a user's configuration and status, this automation collects user profile information, call forwarding settings, Do Not Disturb status, registered devices, and memberships in call centers, hunt groups, and call pickup groups. It provides a comprehensive snapshot of the user's current state, making it ideal for troubleshooting, auditing, or support purposes.

## Usage

```python
from mercury_ocip import Client, Agent

# Initialise client
client = Client(
    host="your-broadworks-server.com",
    username="your-username",
    password="your-password",
    conn_type="SOAP"  # or "TCP"
)

# Get Agent object
agent = Agent.get_instance(client)

# Execute user digest
result = agent.automate.user_digest(
    user_id="user@domain.com"
)

# Check results
if result.ok:
    digest = result.payload
    print(f"✅ User digest generated successfully")
    print(f"DND Status: {digest.user_details.dnd_status}")
    print(f"Registered Devices: {len(digest.user_details.registered_devices)}")
else:
    print(f"❌ {result.message}")
```

## Information Collected

The digest automation collects the following information:

* User Details
* Profile Information - Complete user profile from UserGetRequest23V2
* Call Forwarding - All forwarding variants (Always, Busy, No Answer, Not Reachable, Selective)
* Do Not Disturb - Current DND activation status
* Registered Devices - All currently registered endpoints with device name, type, and line/port
* Group Memberships
* Call Centers - All call centers the user is a member of, including agent ACD state and availability
* Hunt Groups - All hunt groups the user belongs to, with extension and busy status
* Call Pickup Groups - Call pickup group membership details