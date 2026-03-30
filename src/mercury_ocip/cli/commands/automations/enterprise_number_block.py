from action_completer import Empty

from mercury_ocip.cli.globals import MERCURY_CLI
from mercury_ocip.cli.utils.service_group_id_callable import (
    _get_service_provider_id_completions,
)

console = MERCURY_CLI.console()
completer = MERCURY_CLI.completer()


@completer.automations.action(
    "block_number", display_meta="Block a number across all groups in an enterprise"
)
@completer.param(
    _get_service_provider_id_completions,
    display_meta="Enterprise ID",
    cast=str,
)
@completer.param(Empty, display="number", display_meta="Number to block", cast=str)
def _block_number(enterprise_id: str, number: str):
    """
    Block a number across all groups and departments in an enterprise.

    Args:
        enterprise_id: The ID of the enterprise to target.
        number: The digit pattern (e.g. phone number) to block.
    """
    with console.status(
        "[cyan]Blocking number across enterprise...",
        spinner="dots",
        spinner_style="cyan",
    ) as status:
        try:
            result = MERCURY_CLI.agent().automate.block_number_in_enterprise(
                enterprise_id=enterprise_id,
                number=number,
            )

            status.stop()

            if result.ok:
                console.print(
                    f"✔ '{result.payload.digit_plan.digit_pattern_name}' applied across all groups in '{enterprise_id}'.",
                    style="green",
                )
            else:
                console.print(
                    f"✘ Failed to block '{number}' in enterprise '{enterprise_id}'.",
                    style="red",
                )

        except Exception as e:
            status.stop()
            console.print(f"✘ {e}", style="red")
