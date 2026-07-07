from mercury_ocip.cli.core import (
    cli,
    kv_table,
    operation,
    report_header,
    section_panel,
    simple_table,
    status_icon,
)
from mercury_ocip.cli.globals import MERCURY_CLI
from mercury_ocip.automate.call_center_digest import CallCenterDigestResult
from mercury_ocip.automate.base_automation import AutomationResult

from rich.text import Text

console = MERCURY_CLI.console()


def _format_call_center_digest_output(
    result: AutomationResult[CallCenterDigestResult],
) -> None:
    """Display a beautifully formatted call center digest using Rich."""

    try:
        digest = result.payload

        console.print(report_header("Call Center Digest Report"))

        _print_config(digest)
        _print_queue_status(digest)
        _print_agents(digest)

    except AttributeError as e:
        console.print(f"Error: Missing data field - {e}", style="error")
    except Exception as e:
        console.print(f"Error displaying call center digest: {e}", style="error")


def _print_config(digest: CallCenterDigestResult) -> None:
    """Print call center configuration."""
    if not digest.config:
        return

    config = digest.config

    rows = [
        ("Name", config.name or "N/A"),
        ("Type", config.type or "N/A"),
        ("Service User ID", config.service_user_id or "N/A"),
        ("Policy", config.policy or "N/A"),
        ("Phone Number", config.phone_number or "N/A"),
        ("Extension", config.extension or "N/A"),
        ("Routing Type", config.routing_type or "N/A"),
        ("Queue Length", str(config.queue_length)),
        ("Allow Agent Logoff", status_icon(bool(config.allow_agent_logoff))),
        (
            "Allow Call Waiting",
            status_icon(bool(config.allow_call_waiting_for_agents)),
        ),
        ("Video Enabled", status_icon(bool(config.enable_video))),
        (
            "Wrap Up Seconds",
            str(config.wrap_up_seconds) if config.wrap_up_seconds else "N/A",
        ),
    ]

    console.print(
        section_panel(kv_table(rows, columns=2, label_width=25), title="Configuration")
    )


def _print_queue_status(digest: CallCenterDigestResult) -> None:
    """Print queue status information."""
    if not digest.queue_status:
        return

    queue = digest.queue_status
    calls_queued = int(queue.number_of_calls_queued) if queue.number_of_calls_queued else 0
    agents_staffed_count = len(queue.agents_staffed)

    status_text = Text(justify="center")
    status_text.append("Calls Queued: ", style="label")

    queue_color = "success" if calls_queued == 0 else "warning" if calls_queued < 5 else "error"
    status_text.append(f"{calls_queued}", style=queue_color)

    status_text.append("  |  ", style="separator")
    status_text.append("Agents Staffed: ", style="label")
    status_text.append(f"{agents_staffed_count}", style="value")

    console.print(section_panel(status_text, title="Queue Status"))


def _print_agents(digest: CallCenterDigestResult) -> None:
    """Print agents table with their status."""
    if not digest.agents:
        console.print(
            section_panel(
                Text("No agents assigned to this call center", style="label"),
                title="Agents",
            )
        )
        return

    acd_status_map = {status.user_id: status for status in digest.agent_acd_statuses}

    rows = []
    for agent in digest.agents:
        acd_status = acd_status_map.get(agent.user_id)
        acd_state = acd_status.acd_state if acd_status else "Unknown"
        acd_state_color = _get_acd_state_color(acd_state)

        rows.append(
            (
                f"{agent.first_name} {agent.last_name}",
                agent.user_id,
                agent.extension or "—",
                f"[{acd_state_color}]{acd_state}[/]",
                status_icon(agent.is_available),
                str(agent.skill_level) if agent.skill_level else "—",
            )
        )

    agents_table = simple_table(
        [
            ("Name", {"style": "value", "min_width": 20}),
            ("User ID", {"style": "label", "min_width": 25}),
            ("Extension", {"style": "label", "min_width": 10}),
            ("ACD State", {"min_width": 12}),
            ("Available", {"min_width": 10}),
            ("Skill", {"style": "label", "min_width": 8}),
        ],
        rows,
    )

    console.print(section_panel(agents_table, title="Agents"))


def _get_acd_state_color(state: str | None) -> str:
    """Get the color for an ACD state."""
    if state is None:
        return "label"
    state_colors = {
        "Available": "success",
        "Sign-In": "success",
        "Unavailable": "error",
        "Sign-Out": "error",
        "Wrap-Up": "warning",
    }
    return state_colors.get(state, "label")


@cli.command(
    "automations call_center_digest",
    meta="Perform a comprehensive digest of a call center",
)
@cli.param("service_user_id", meta="Service User ID")
def _call_center_digest(service_user_id: str):
    """
    Perform a comprehensive digest of a call center.

    Args:
        service_user_id: The service user ID of the call center.
    """
    with operation("Performing call center digest...") as op:
        result = MERCURY_CLI.agent().automate.call_center_digest(
            service_user_id=service_user_id,
        )

        if result.ok:
            op.stop()
            _format_call_center_digest_output(result)
        else:
            op.fail(f"Call center digest failed for '{service_user_id}'.")
