from mercury_ocip.cli.core import cli, operation
from mercury_ocip.cli.globals import MERCURY_CLI
from mercury_ocip.cli.utils.service_group_id_callable import service_provider_ids


@cli.command(
    "automations block_number",
    meta="Block a number across all groups in an enterprise",
)
@cli.param("enterprise_id", source=service_provider_ids, meta="Enterprise ID")
@cli.param("number", meta="Number to block")
def _block_number(enterprise_id: str, number: str):
    """
    Block a number across all groups and departments in an enterprise.

    Args:
        enterprise_id: The ID of the enterprise to target.
        number: The digit pattern (e.g. phone number) to block.
    """
    with operation("Blocking number across enterprise...") as op:
        result = MERCURY_CLI.agent().automate.block_number_in_enterprise(
            enterprise_id=enterprise_id,
            number=number,
        )

        if result.ok:
            op.success(
                f"'{result.payload.digit_plan.digit_pattern_name}' applied "
                f"across all groups in '{enterprise_id}'."
            )
        else:
            op.fail(f"Failed to block '{number}' in enterprise '{enterprise_id}'.")
