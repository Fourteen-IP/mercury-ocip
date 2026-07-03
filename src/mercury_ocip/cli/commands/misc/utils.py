import sys

from rich import box
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from mercury_ocip.cli.core import cli, debug, debug_enabled
from mercury_ocip.cli.globals import MERCURY_CLI
from mercury_ocip.cli.utils.service_group_id_callable import (
    group_ids,
    group_service_packs,
    service_provider_ids,
)
from mercury_ocip.commands.base_command import ErrorResponse
from mercury_ocip.commands.commands import GroupGetUserServiceAssignedUserListResponse

console = MERCURY_CLI.console()


@cli.command("sysver", meta="Gives the current system version")
def _sysver():
    version = MERCURY_CLI.client().raw_command("SystemSoftwareVersionGetRequest")
    console.print(f"Current system version: [cyan]{version.version}")


@cli.command("exit", meta="Exits the CLI")
def _exit():
    console.print("[dim]Exiting mercury_cli. Goodbye!")
    if MERCURY_CLI.client():
        MERCURY_CLI.client().disconnect()
    sys.exit()


@cli.command("clear", meta="Clears the terminal screen")
def _clear():
    console.clear()


@cli.command("debug", meta="Toggle debug mode (full tracebacks on errors)")
def _debug():
    debug(not debug_enabled())
    state = "on" if debug_enabled() else "off"
    console.print(f"Debug mode {state}.", style="value")
