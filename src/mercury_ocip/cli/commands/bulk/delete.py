from mercury_ocip.cli.core import cli
from mercury_ocip.cli.commands.bulk.bulk import register_bulk_csv_command

cli.describe("bulk delete", "Bulk delete operations for various entities")

register_bulk_csv_command(
    "bulk delete group_admin",
    "delete_group_admin_from_csv",
    "group admins",
    meta="Bulk delete group admins from a CSV file",
)

register_bulk_csv_command(
    "bulk delete service_provider_admin",
    "delete_service_provider_admin_from_csv",
    "service provider admins",
    meta="Bulk delete service provider admins from a CSV file",
)
