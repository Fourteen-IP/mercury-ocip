# Group Audit

The group audit automation performs a comprehensive audit of a BroadWorks group, collecting detailed information about group configuration, license usage, and assigned directory numbers.

> **Note**: This automation can also be executed via the CLI. See the [CLI documentation](../../CLI/index.md) for details on running automations from the command line.

## Description

When you need a complete overview of a group's configuration and resource usage, this automation collects group details, license breakdown information, and directory number assignments. It provides a snapshot of the group's current state, making it ideal for auditing, reporting, or planning purposes.

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

# Execute audit
result = agent.automate.audit_group(
    service_provider_id="MyServiceProvider",
    group_id="SalesGroup"
)

# Check results
if result.ok:
    audit_data = result.payload
    print(f"✅ Audit complete")
    if audit_data.group_details:
        print(f"Group: {audit_data.group_details.group_name or 'N/A'}")
    if audit_data.group_dns:
        print(f"Total DNs: {audit_data.group_dns.total}")
else:
    print(f"❌ {result.message}")
```

## Audit Behaviour

The audit collects information in three main areas:

1. **Group Details** - Fetches comprehensive group configuration information including group name, default domain, time zone, and other settings via `GroupGetRequest22V5`

2. **License Breakdown** - Retrieves service authorisation information and parses it into three categories:
   - `group_services_authorization_table` - Services authorised at the group level
   - `service_packs_authorization_table` - Service packs authorised for the group
   - `user_services_authorization_table` - Services authorised for users in the group

3. **Directory Numbers** - Fetches all assigned directory numbers (phone numbers) and:
   - Expands phone number ranges (e.g., "1000 - 1099" becomes individual numbers)
   - Returns both the total count and the complete set of assigned numbers
   - Handles both individual numbers and ranges

## Response Format

The automation returns an `AutomationResult[GroupAuditResult]`:

```python
{
    "ok": True,  # Whether audit completed successfully
    "message": "Audit completed successfully",  # Status message
    "payload": {
        "group_details": GroupGetResponse22V5 | None,  # Complete group configuration (may be None)
        "license_breakdown": LicenseBreakdown | None,  # License usage breakdown (may be None)
        "group_dns": GroupDns | None  # Directory numbers information (may be None)
    }
}
```

Where `LicenseBreakdown` contains:
```python
{
    "group_services_authorization_table": dict[str, str],  # Service name -> usage count
    "service_packs_authorization_table": dict[str, str],   # Pack name -> usage count
    "user_services_authorization_table": dict[str, str]    # Service name -> usage count
}
```

And `GroupDns` contains:
```python
{
    "total": int,           # Total number of assigned directory numbers
    "numbers": set[str]     # Set of all assigned directory numbers (as strings)
}
```

### Group Details

The `group_details` field is of type `GroupGetResponse22V5 | None`. When present, it contains the full group configuration response, which includes:
- Group name and ID
- Default domain
- Time zone
- Contact information
- And other group configuration settings

### License Breakdown

The `license_breakdown` field is of type `LicenseBreakdown | None`. When present, it contains dictionaries mapping service/service pack names to their usage counts (as strings). Only services with non-zero usage are included. Each dictionary may be empty if no services of that type are in use. For example:

```python
license_breakdown = LicenseBreakdown(
    group_services_authorization_table={
        "Basic": "10",
        "Standard": "50"
    },
    service_packs_authorization_table={
        "Premium Pack": "25"
    },
    user_services_authorization_table={
        "Call Waiting": "75",
        "Call Forwarding": "60"
    }
)
```

### Directory Numbers

The `group_dns` field is of type `GroupDns | None`. When present, it contains:
- `total`: An integer representing the total count of assigned directory numbers (after expanding ranges)
- `numbers`: A set of strings containing all individual directory numbers

The numbers are stored as strings (e.g., `"1000"`, `"555-1234"`), and phone number ranges are automatically expanded (e.g., `"1000 - 1099"` becomes 100 individual number strings).

## Example: Comprehensive Audit Report

```python
# Perform audit
result = agent.automate.audit_group(
    service_provider_id="SP1",
    group_id="Sales"
)

if result.ok:
    audit = result.payload
    
    # Group information
    if audit.group_details:
        print(f"\n=== Group: {audit.group_details.group_name or 'N/A'} ===")
        print(f"Default Domain: {audit.group_details.default_domain or 'N/A'}")
    
    # License usage
    print("\n--- License Usage ---")
    if audit.license_breakdown:
        licenses = audit.license_breakdown
        
        if licenses.group_services_authorization_table:
            print("\nGroup Services:")
            for service, usage in licenses.group_services_authorization_table.items():
                print(f"  {service}: {usage}")
        
        if licenses.service_packs_authorization_table:
            print("\nService Packs:")
            for pack, usage in licenses.service_packs_authorization_table.items():
                print(f"  {pack}: {usage}")
        
        if licenses.user_services_authorization_table:
            print("\nUser Services:")
            for service, usage in licenses.user_services_authorization_table.items():
                print(f"  {service}: {usage}")
    else:
        print("License breakdown not available")
    
    # Directory numbers
    if audit.group_dns:
        print(f"\n--- Directory Numbers ---")
        print(f"Total Assigned: {audit.group_dns.total}")
        if audit.group_dns.numbers:
            print(f"Sample Numbers: {list(audit.group_dns.numbers)[:10]}")
    else:
        print("\nDirectory numbers not available")
else:
    print(f"Audit failed: {result.message}")
```

## Example: Checking DN Availability

```python
# Check if specific numbers are available
result = agent.automate.audit_group(
    service_provider_id="SP1",
    group_id="Sales"
)

if result.ok and result.payload.group_dns:
    assigned_numbers = result.payload.group_dns.numbers
    
    # Check availability
    requested_numbers = ["2000", "2001", "2002"]
    available = [num for num in requested_numbers if num not in assigned_numbers]
    
    if available:
        print(f"Available numbers: {available}")
    else:
        print("All requested numbers are already assigned")
```

## Notes

- The audit fetches data from multiple OCIP commands, so it may take longer for groups with many directory numbers
- Phone number ranges are automatically expanded (e.g., "1000 - 1099" becomes 100 individual numbers)
- Only services with non-zero usage are included in the license breakdown
- All directory numbers are returned as strings in the set
- Requires appropriate permissions to read group details, service authorisations, and directory number assignments
- The `group_details`, `license_breakdown`, and `group_dns` fields may be `None` if their respective API calls fail

