from mercury_ocip.automate.user_digest import UserDetailsResult
from mercury_ocip.automate.user_digest import UserDigestResult
from mercury_ocip.cli.core import cli, operation
from mercury_ocip.cli.globals import MERCURY_CLI
from mercury_ocip.automate.base_automation import AutomationResult

from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich import box
from rich.text import Text

console = MERCURY_CLI.console()


def _format_user_digest_output(result: AutomationResult[UserDigestResult]) -> None:
    """
    Display a beautifully formatted user digest using Rich.
    """

    try:
        user_details: UserDetailsResult = result.payload.user_details
        user_info = user_details.user_info

        # Header
        _print_header()

        # Main info sections
        _print_basic_info(user_info, user_details)
        _print_call_forwarding(user_details)
        _print_voicemail_forwarding(user_details)
        _print_memberships(result)
        _print_devices(user_details)

    except AttributeError as e:
        console.print(f"Error: Missing data field - {e}", style="red")
    except Exception as e:
        console.print(f"Error displaying user digest: {e}", style="red")


def _print_header() -> None:
    """Print the header panel."""
    console.print(
        Panel(
            Text("User Digest Report", style="header", justify="center"),
            style="divider",
        )
    )


def _print_basic_info(user_info, user_details) -> None:
    """Print basic user information in a 3-column layout."""
    info_table = Table(box=None, show_header=False, padding=(0, 2), expand=True)
    info_table.add_column(style="label", width=18)
    info_table.add_column(style="value")
    info_table.add_column(style="label", width=18)
    info_table.add_column(style="value")
    info_table.add_column(style="label", width=18)
    info_table.add_column(style="value")

    # Row 1: Name, Extension, DND Status
    dnd_status = "🔇 ON" if user_details.dnd_status == "true" else "🔊 OFF"
    dnd_color = "#ff5555" if user_details.dnd_status == "true" else "success"

    info_table.add_row(
        "Name",
        f"{user_info.first_name} {user_info.last_name}",
        "Extension",
        user_info.extension,
        "DND",
        f"[{dnd_color}]{dnd_status}[/]",
    )

    # Row 2: ID, Phone, Trunked
    info_table.add_row(
        "ID",
        user_info.user_id or "N/A",
        "Phone",
        user_info.phone_number,
        "Trunked",
        "✓" if user_info.trunk_addressing is not None else "✗",
    )

    # Row 3: Service Provider, Group, CLID
    info_table.add_row(
        "Service Provider",
        user_info.service_provider_id,
        "Group",
        user_info.group_id,
        "CLID",
        user_info.calling_line_id_phone_number,
    )

    console.print(
        Panel(
            info_table,
            title="[bold #d8bbff]Basic Info[/]",
            border_style="divider",
        )
    )


def _print_call_forwarding(user_details) -> None:
    """Print call forwarding information."""

    forward_text = Text(justify="center")
    for i, fwd in enumerate(user_details.forwards.user_forwarding):
        if i > 0:
            forward_text.append(" | ", style="separator")
        forward_text.append(f"{fwd.variant.replace('_', ' ').title()}: ", style="label")
        if fwd.is_active == "true":
            dest = (
                ""
                if fwd.variant == "Selective"
                else ((f"({fwd.forward_to_phone_number})") or "—")
            )
            forward_text.append(f"✓ {dest}", style="success")
        else:
            forward_text.append("✗", style="error")
    console.print(
        Panel(
            forward_text,
            title="[bold #d8bbff]Call Forwards[/]",
            border_style="divider",
        )
    )

    # Selective forwards
    selective_forwards = [
        f
        for f in user_details.forwards.user_forwarding
        if f.is_active == "true" and f.variant == "Selective" and f.selective_criteria
    ]

    if selective_forwards:
        for fwd in selective_forwards:
            selective_table = Table(box=box.SIMPLE, show_header=True, expand=True)
            selective_table.add_column("Criteria Name", style="value")
            selective_table.add_column("Forward To", style="success")
            selective_table.add_column("Time Schedule", style="label")
            selective_table.add_column("Call From", style="label")

            if fwd.selective_criteria and fwd.selective_criteria.row:
                for row in fwd.selective_criteria.row:
                    selective_table.add_row(
                        row.col[1] if len(row.col) > 1 else "N/A",
                        row.col[6] if len(row.col) > 6 else "N/A",
                        row.col[2] if len(row.col) > 2 else "N/A",
                        row.col[3] if len(row.col) > 3 else "N/A",
                    )

            console.print(
                Panel(
                    selective_table,
                    title="[bold #d8bbff]Selective Call Forwarding[/]",
                    border_style="divider",
                ),
            )


def _print_voicemail_forwarding(user_details) -> None:
    """Print voicemail forwarding information."""
    vm_forwards = user_details.forwards.voicemail_forwarding

    if vm_forwards:
        forward_text = Text(justify="center")
        for i, fwd in enumerate(vm_forwards):
            if i > 0:
                forward_text.append(" | ", style="separator")
            forward_text.append(
                f"{fwd.variant.replace('voice_mail', 'vm').replace('_', ' ').title()}: ",
                style="label",
            )
            if fwd.is_active == "true":
                forward_text.append("✓", style="success")
            else:
                forward_text.append("✗", style="error")
        console.print(
            Panel(
                forward_text,
                title="[bold #d8bbff]VM Forwards[/]",
                border_style="divider",
            )
        )


def _print_memberships(
    result: AutomationResult[UserDigestResult],
) -> None:
    """Print membership information in a tree view."""
    membership_tree = Tree(Text("Memberships", style="subheader"))

    # Call Centers
    if result.payload.call_center_membership:
        cc_branch = membership_tree.add(Text("📞 Call Centers", style="version"))
        for cc in result.payload.call_center_membership:
            acd_state_color = (
                "success" if cc.agent_acd_state == "Available" else "#ffaa00"
            )
            acd_available_color = (
                "success" if cc.agent_cc_available == "true" else "#ff5555"
            )
            cc_branch.add(
                f"[value]{cc.call_center_name}[/] - "
                f"[label]{cc.call_center_id}[/] - "
                f"[{acd_state_color}]{cc.agent_acd_state}[/] - "
                f"[{acd_available_color}]Available for CC {'✓' if cc.agent_cc_available == 'true' else '✗'}[/]"
            )

    # Hunt Groups
    if result.payload.hunt_group_membership:
        hg_branch = membership_tree.add(Text("🎯 Hunt Groups", style="version"))
        for hg in result.payload.hunt_group_membership:
            hg_branch.add(
                f"[value]{hg.hunt_group_name}[/] - [label]{hg.hunt_group_id}[/]"
            )

    # Pickup Groups
    if result.payload.call_pickup_group_membership:
        cpu = result.payload.call_pickup_group_membership
        pu_branch = membership_tree.add(Text("📫 Call Pickup Groups", style="version"))
        pu_branch.add(f"[value]{cpu.call_pickup_group_name}")

    console.print(Panel(membership_tree, border_style="divider"))


def _print_devices(user_details) -> None:
    """Print registered devices information."""
    if user_details.devices:
        device_table = Table(
            box=box.SIMPLE, show_header=True, padding=(0, 2), expand=True
        )
        device_table.add_column("Device Name", style="value", min_width=20)
        device_table.add_column("Type", style="label", min_width=15)
        device_table.add_column("Lineport", style="label", min_width=15)
        device_table.add_column("Registered", style="label", min_width=15)

        for device in user_details.devices:
            device_table.add_row(
                device.device_name or "N/A",
                device.device_type or "N/A",
                device.line_port or "N/A",
                device.is_registered == "[success]✓" or "[error]✗",
            )

        console.print(
            Panel(
                device_table,
                title="[bold #d8bbff]Devices[/]",
                border_style="divider",
            )
        )


@cli.command("automations user_digest", meta="Perform a comprehensive audit of a user")
@cli.param("user_id", meta="User ID")
def _user_digest(user_id: str):
    """
    Perform a comprehensive audit of a user.

    Args:
        user_id: The ID of the user to audit.
    """
    with operation("Performing user digest...") as op:
        result = MERCURY_CLI.agent().automate.user_digest(
            user_id=user_id,
        )

        if result.ok:
            op.stop()
            _format_user_digest_output(result)
        else:
            op.fail(f"User digest failed for User ID '{user_id}'.")
