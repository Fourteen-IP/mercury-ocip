# Bulk Operations

The bulk command processes CSV files to perform mass operations

!!! note "Mercury OCIP Docs"
    The CSV format and guide to making your own automation sheets can be found here:

    *[:octicons-link-16: Agent Documentation](https://mercury-docs.14ip.net/mercury-ocip/agent/bulk-operations/)*

## Usage

```asciinema-player
{
    "file": "/assets/asciinema/bulk_example.cast",
    "title": "Bulk Operations Showcase",
    "mkap_theme": "none",
    "theme": "dracula",
    "fit": "width",
    "cols": 120,
    "rows": 24,
    "autoplay": true
}
```


```
bulk <operation> <entity> <file_path>
```

--- 
## Operations

### create

Creates new entities from a CSV file.

- **Supported entities:**
    * `hunt_group` - Create hunt groups
    * `call_pickup` - Create call pickup groups
    * `call_center` - Create call centers
    * `auto_attendant` - Create auto attendants
    * `user` - Create users
    * `group_admin` - Create group admins

**Example:**
```bash title="Create Users in Bulk"
bulk create user /path/to/users.csv
```
---
### modify

Modifies existing entities from a CSV file.

- **Supported entities:**
    * `agent_list` - Add, remove, or replace agents in call centers
    * `user` - Modify user configurations
    * `group_admin_policy` - Modify group admin policies

**Example:**
```bash title="Modify Users in Bulk"
bulk modify user /path/to/users.csv
```
---
## CSV Format

Each entity type has its own required CSV format. Check the entity-specific documentation or example templates.

- The file must:
    * Be a valid CSV file (`.csv` extension)
    * Exist on the filesystem
    * Have the correct headers for the entity type

---
## Output

Success: Shows count of processed entities.

Failure: Shows count of failures with row-by-row error details.

!!! note "Error Output"
    For detailed information on how the output of bulk operations is structured, refer to the *[:octicons-link-16: Response Format](https://mercury-docs.14ip.net/mercury-ocip/agent/bulk-operations/create-auto-attendant/#response-format)* section in the Mercury OCIP documentation.

---
## Notes

- Processing stops on file validation errors (not CSV, file not found)
- Individual row failures don't stop the entire batch
- No rollback on partial failures