from prompt_toolkit.completion import PathCompleter
from mercury_ocip.cli.commands.bulk.bulk import _cli_wrap_verification
from mercury_ocip.cli.globals import MERCURY_CLI

completer = MERCURY_CLI.completer()
completer.bulk.modify.display_meta = "Bulk modify operations for various entities"


# -- Call Center Modify Commands -- #
@completer.bulk.modify.action(
    "agent_list",
    display_meta="Call center agent list modification enables you to add, remove, or replace agents in existing call centers.",
)
@completer.param(
    source=PathCompleter(), display="file_path", display_meta="Path to CSV"
)
def _bulk_call_center_agent_list(file_path: str):
    _cli_wrap_verification(
        "modify_call_center_agent_list_from_csv", "call centers", file_path=file_path
    )


# -- User Modify Commands -- #
@completer.bulk.modify.action("user", display_meta="Bulk modify users from a CSV file")
@completer.param(
    source=PathCompleter(), display="file_path", display_meta="Path to CSV"
)
def _bulk_user(file_path: str):
    _cli_wrap_verification("modify_user_from_csv", "users", file_path=file_path)


# -- Group Admin Modify Commands -- #
@completer.bulk.modify.action(
    "group_admin_policy",
    display_meta="Bulk modify group admins policies from a CSV file",
)
@completer.param(
    source=PathCompleter(), display="file_path", display_meta="Path to CSV"
)
def _bulk_group_admin(file_path: str):
    _cli_wrap_verification(
        "modify_group_admin_policy_from_csv", "group admins", file_path=file_path
    )


@completer.bulk.modify.action(
    "service_provider_admin_policy",
    display_meta="Bulk modify service provider admins policies from a CSV file",
)
@completer.param(
    source=PathCompleter(), display="file_path", display_meta="Path to CSV"
)
def _bulk_service_provider_admin(file_path: str):
    _cli_wrap_verification(
        "modify_service_provider_admin_policy_from_csv",
        "service provider admins",
        file_path=file_path,
    )
