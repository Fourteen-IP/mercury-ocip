from mercury_ocip.cli.globals import MERCURY_CLI

completer = MERCURY_CLI.completer()

completer.automations.display_meta = (
    "Automations for various entities such as Users and Groups"
)
