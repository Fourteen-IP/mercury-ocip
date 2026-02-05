from prompt_toolkit.completion import PathCompleter
from mercury_ocip.cli.commands.bulk.bulk import _cli_wrap_verification
from mercury_ocip.cli.globals import MERCURY_CLI

completer = MERCURY_CLI.completer()

completer.bulk.delete.display_meta = "Bulk delete operations for various entities"


# -- Group Admin Delete Commands -- #
@completer.bulk.delete.action(
    "group_admin", display_meta="Bulk delete group admins from a CSV file"
)
@completer.param(
    source=PathCompleter(), display="file_path", display_meta="Path to CSV"
)
def _bulk_group_admin(file_path: str):
    _cli_wrap_verification(
        "delete_group_admin_from_csv", "group admins", file_path=file_path
    )


# -- Service Provider Admin Delete Commands -- #
@completer.bulk.delete.action(
    "service_provider_admin",
    display_meta="Bulk delete service provider admins from a CSV file",
)
@completer.param(
    source=PathCompleter(), display="file_path", display_meta="Path to CSV"
)
def _bulk_service_provider_admin(file_path: str):
    _cli_wrap_verification(
        "delete_service_provider_admin_from_csv",
        "service provider admins",
        file_path=file_path,
    )
