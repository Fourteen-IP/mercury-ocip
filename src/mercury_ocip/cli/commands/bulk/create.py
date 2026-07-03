from mercury_ocip.cli.core import cli
from mercury_ocip.cli.commands.bulk.bulk import register_bulk_csv_command

cli.describe("bulk create", "Bulk create operations for various entities")

_CREATE_OPERATIONS = [
    # (command name, bulk method, entity display name)
    ("hunt_group", "create_hunt_group_from_csv", "hunt groups"),
    ("call_pickup", "create_call_pickup_from_csv", "call pickup groups"),
    ("call_center", "create_call_center_from_csv", "call centres"),
    ("auto_attendant", "create_auto_attendant_from_csv", "auto attendants"),
    ("user", "create_user_from_csv", "users"),
    ("group_admin", "create_group_admin_from_csv", "group admins"),
    (
        "service_provider_admin",
        "create_service_provider_admin_from_csv",
        "service provider admins",
    ),
]

for _name, _method, _entity in _CREATE_OPERATIONS:
    register_bulk_csv_command(
        f"bulk create {_name}",
        _method,
        _entity,
        meta=f"Bulk create {_entity} from a CSV file",
    )
