import sys
from mercury_ocip.cli.globals import MERCURY_CLI

completer = MERCURY_CLI.completer()
console = MERCURY_CLI.console()


@completer.action("sysver", display_meta="Gives the current system version")
def _sysver():
    version = MERCURY_CLI.client().raw_command("SystemSoftwareVersionGetRequest")
    print(f"Current system version: {version.version}")


@completer.action("exit", display_meta="Exits the CLI")
def _exit():
    print("Exiting mercury_cli. Goodbye!")
    MERCURY_CLI.client().disconnect()
    sys.exit()


@completer.action("clear", display_meta="Clears the terminal screen")
def _clear():
    console.clear()
