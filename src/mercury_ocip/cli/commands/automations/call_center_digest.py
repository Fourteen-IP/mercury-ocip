from mercury_ocip.cli.core import cli, operation
from mercury_ocip.cli.globals import MERCURY_CLI
from mercury_ocip.automate.call_center_digest import CallCenterDigestResult
from mercury_ocip.automate.base_automation import AutomationResult

from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.text import Text

console = MERCURY_CLI.console()


def _format_call_center_digest_output(
    result: AutomationResult[CallCenterDigestResult],
) -> None:
    """Display a beautifully formatted call center digest using Rich."""

    try:
        digest = result.payload

        # Header
        console.print(
            Panel(
                Text("Call Center Digest Report", style="header", justify="center"),
                style="divider",
            )
        )

        # Config section
        _print_config(digest)

        # Queue status section
        _print_queue_status(digest)

        # Agents section
        _print_agents(digest)

    except AttributeError as e:
        console.print(f"Error: Missing data field - {e}", style="red")
    except Exception as e:
        console.print(f"Error displaying call center digest: {e}", style="red")


def _print_config(digest: CallCenterDigestResult) -> None:
    """Print call center configuration."""
    if not digest.config:
        return

    config = digest.config

    info_table = Table(box=None, show_header=False, padding=(0, 2), expand=True)
    info_table.add_column(style="label", width=25)
    info_table.add_column(style="value")
    info_table.add_column(style="label", width=25)
    info_table.add_column(style="value")

    # Row 1: Name, Type
    info_table.add_row(
        "Name",
        config.name or "N/A",
        "Type",
        config.type or "N/A",
    )

    # Row 2: Service User ID, Policy
    info_table.add_row(
        "Service User ID",
        config.service_user_id or "N/A",
        "Policy",
        config.policy or "N/A",
    )

    # Row 3: Phone Number, Extension
    info_table.add_row(
        "Phone Number",
        config.phone_number or "N/A",
        "Extension",
        config.extension or "N/A",
    )

    # Row 4: Routing Type, Queue Length
    info_table.add_row(
        "Routing Type",
        config.routing_type or "N/A",
        "Queue Length",
        str(config.queue_length),
    )

    # Row 5: Allow Agent Logoff, Allow Call Waiting
    logoff_status = "✓" if config.allow_agent_logoff else "✗"
    waiting_status = "✓" if config.allow_call_waiting_for_agents else "✗"
    info_table.add_row(
        "Allow Agent Logoff",
        logoff_status,
        "Allow Call Waiting",
        waiting_status,
    )

    # Row 6: Video Enabled, Wrap Up Seconds
    video_status = "✓" if config.enable_video else "✗"
    info_table.add_row(
        "Video Enabled",
        video_status,
        "Wrap Up Seconds",
        str(config.wrap_up_seconds) if config.wrap_up_seconds else "N/A",
    )

    console.print(
        Panel(
            info_table,
            title="[bold #d8bbff]Configuration[/]",
            border_style="divider",
        )
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

    queue_color = "success" if calls_queued == 0 else "#ffaa00" if calls_queued < 5 else "#ff5555"
    status_text.append(f"{calls_queued}", style=queue_color)

    status_text.append("  |  ", style="separator")
    status_text.append("Agents Staffed: ", style="label")
    status_text.append(f"{agents_staffed_count}", style="value")

    console.print(
        Panel(
            status_text,
            title="[bold #d8bbff]Queue Status[/]",
            border_style="divider",
        )
    )


def _print_agents(digest: CallCenterDigestResult) -> None:
    """Print agents table with their status."""
    if not digest.agents:
        console.print(
            Panel(
                Text("No agents assigned to this call center", style="label"),
                title="[bold #d8bbff]Agents[/]",
                border_style="divider",
            )
        )
        return

    agents_table = Table(box=box.SIMPLE, show_header=True, expand=True)
    agents_table.add_column("Name", style="value", min_width=20)
    agents_table.add_column("User ID", style="label", min_width=25)
    agents_table.add_column("Extension", style="label", min_width=10)
    agents_table.add_column("ACD State", min_width=12)
    agents_table.add_column("Available", min_width=10)
    agents_table.add_column("Skill", style="label", min_width=8)

    # Create a lookup for ACD statuses by user_id
    acd_status_map = {
        status.user_id: status for status in digest.agent_acd_statuses
    }

    for agent in digest.agents:
        acd_status = acd_status_map.get(agent.user_id)

        # ACD State styling
        acd_state = acd_status.acd_state if acd_status else "Unknown"
        acd_state_color = _get_acd_state_color(acd_state)
        acd_state_display = f"[{acd_state_color}]{acd_state}[/]"

        # Availability styling
        available_display = (
            "[success]✓[/]" if agent.is_available else "[#ff5555]✗[/]"
        )

        # Skill level
        skill_display = str(agent.skill_level) if agent.skill_level else "—"

        agents_table.add_row(
            f"{agent.first_name} {agent.last_name}",
            agent.user_id,
            agent.extension or "—",
            acd_state_display,
            available_display,
            skill_display,
        )

    console.print(
        Panel(
            agents_table,
            title="[bold #d8bbff]Agents[/]",
            border_style="divider",
        )
    )


def _get_acd_state_color(state: str | None) -> str:
    """Get the color for an ACD state."""
    if state is None:
        return "label"
    state_colors = {
        "Available": "success",
        "Sign-In": "success",
        "Unavailable": "#ff5555",
        "Sign-Out": "#ff5555",
        "Wrap-Up": "#ffaa00",
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
