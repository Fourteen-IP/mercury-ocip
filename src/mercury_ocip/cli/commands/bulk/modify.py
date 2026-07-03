from mercury_ocip.cli.core import cli
from mercury_ocip.cli.commands.bulk.bulk import register_bulk_csv_command

cli.describe("bulk modify", "Bulk modify operations for various entities")

register_bulk_csv_command(
    "bulk modify agent_list",
    "modify_call_center_agent_list_from_csv",
    "call centers",
    meta=(
        "Call center agent list modification enables you to add, remove, or "
        "replace agents in existing call centers."
    ),
)

register_bulk_csv_command(
    "bulk modify user",
    "modify_user_from_csv",
    "users",
    meta="Bulk modify users from a CSV file",
)

register_bulk_csv_command(
    "bulk modify group_admin_policy",
    "modify_group_admin_policy_from_csv",
    "group admins",
    meta="Bulk modify group admins policies from a CSV file",
)

register_bulk_csv_command(
    "bulk modify service_provider_admin_policy",
    "modify_service_provider_admin_policy_from_csv",
    "service provider admins",
    meta="Bulk modify service provider admins policies from a CSV file",
)
