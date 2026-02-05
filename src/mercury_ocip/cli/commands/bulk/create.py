from prompt_toolkit.completion import PathCompleter
from mercury_ocip.cli.commands.bulk.bulk import _cli_wrap_verification
from mercury_ocip.cli.globals import MERCURY_CLI

completer = MERCURY_CLI.completer()

completer.bulk.create.display_meta = "Bulk create operations for various entities"


# -- Hunt Group Create Commands -- #
@completer.bulk.create.action(
    "hunt_group", display_meta="Bulk create hunt groups from a CSV file"
)
@completer.param(
    source=PathCompleter(), display="file_path", display_meta="Path to CSV"
)
def _bulk_hunt_group(file_path: str):
    _cli_wrap_verification(
        "create_hunt_group_from_csv", "hunt groups", file_path=file_path
    )


# -- Call Pickup Create Commands -- #
@completer.bulk.create.action(
    "call_pickup", display_meta="Bulk create call pickup groups from a CSV file"
)
@completer.param(
    source=PathCompleter(), display="file_path", display_meta="Path to CSV"
)
def _bulk_call_pickup(file_path: str):
    _cli_wrap_verification(
        "create_call_pickup_from_csv", "call pickup groups", file_path=file_path
    )


# -- Call Center Create Commands -- #
@completer.bulk.create.action(
    "call_center", display_meta="Bulk create call centers from a CSV file"
)
@completer.param(
    source=PathCompleter(), display="file_path", display_meta="Path to CSV"
)
def _bulk_call_center(file_path: str):
    _cli_wrap_verification(
        "create_call_center_from_csv", "call centres", file_path=file_path
    )


# -- Auto Attendant Create Commands -- #
@completer.bulk.create.action(
    "auto_attendant", display_meta="Bulk create auto attendants from a CSV file"
)
@completer.param(
    source=PathCompleter(), display="file_path", display_meta="Path to CSV"
)
def _bulk_auto_attendant(file_path: str):
    _cli_wrap_verification(
        "create_auto_attendant_from_csv", "auto attendants", file_path=file_path
    )


# -- User Create Commands -- #
@completer.bulk.create.action("user", display_meta="Bulk create users from a CSV file")
@completer.param(
    source=PathCompleter(), display="file_path", display_meta="Path to CSV"
)
def _bulk_user(file_path: str):
    _cli_wrap_verification("create_user_from_csv", "users", file_path=file_path)


# -- Group Admin Create Commands -- #
@completer.bulk.create.action(
    "group_admin", display_meta="Bulk create group admins from a CSV file"
)
@completer.param(
    source=PathCompleter(), display="file_path", display_meta="Path to CSV"
)
def _bulk_group_admin(file_path: str):
    _cli_wrap_verification(
        "create_group_admin_from_csv", "group admins", file_path=file_path
    )


@completer.bulk.create.action(
    "service_provider_admin",
    display_meta="Bulk create service provider admins from a CSV file",
)
@completer.param(
    source=PathCompleter(), display="file_path", display_meta="Path to CSV"
)
def _bulk_service_provider_admin(file_path: str):
    _cli_wrap_verification(
        "create_service_provider_admin_from_csv",
        "service provider admins",
        file_path=file_path,
    )
