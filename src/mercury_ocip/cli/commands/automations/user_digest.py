from mercury_ocip.automate.user_digest import UserDetailsResult
from mercury_ocip.automate.user_digest import UserDigestResult
from mercury_ocip.cli.core import (
    append_status,
    cli,
    kv_table,
    operation,
    report_header,
    section_panel,
    simple_table,
    status_icon,
)
from mercury_ocip.cli.globals import MERCURY_CLI
from mercury_ocip.automate.base_automation import AutomationResult

from rich.tree import Tree
from rich.text import Text

console = MERCURY_CLI.console()


def _format_user_digest_output(result: AutomationResult[UserDigestResult]) -> None:
    """
    Display a beautifully formatted user digest using Rich.
    """

    try:
        user_details: UserDetailsResult = result.payload.user_details
        user_info = user_details.user_info

        console.print(report_header("User Digest Report"))

        _print_basic_info(user_info, user_details)
        _print_call_forwarding(user_details)
        _print_voicemail_forwarding(user_details)
        _print_memberships(result)
        _print_devices(user_details)

    except AttributeError as e:
        console.print(f"Error: Missing data field - {e}", style="error")
    except Exception as e:
        console.print(f"Error displaying user digest: {e}", style="error")


def _print_basic_info(user_info, user_details) -> None:
    """Print basic user information in a 3-column layout."""
    dnd_active = user_details.dnd_status == "true"
    dnd_display = f"{status_icon(not dnd_active)} {'ON' if dnd_active else 'OFF'}"

    rows = [
        ("Name", f"{user_info.first_name} {user_info.last_name}"),
        ("Extension", user_info.extension),
        ("DND", dnd_display),
        ("ID", user_info.user_id or "N/A"),
        ("Phone", user_info.phone_number),
        ("Trunked", status_icon(user_info.trunk_addressing is not None)),
        ("Service Provider", user_info.service_provider_id),
        ("Group", user_info.group_id),
        ("CLID", user_info.calling_line_id_phone_number),
    ]

    console.print(
        section_panel(kv_table(rows, columns=3, label_width=18), title="Basic Info")
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
    console.print(section_panel(forward_text, title="Call Forwards"))

    # Selective forwards
    selective_forwards = [
        f
        for f in user_details.forwards.user_forwarding
        if f.is_active == "true" and f.variant == "Selective" and f.selective_criteria
    ]

    if selective_forwards:
        for fwd in selective_forwards:
            rows = []
            if fwd.selective_criteria and fwd.selective_criteria.row:
                for row in fwd.selective_criteria.row:
                    rows.append(
                        (
                            row.col[1] if len(row.col) > 1 else "N/A",
                            row.col[6] if len(row.col) > 6 else "N/A",
                            row.col[2] if len(row.col) > 2 else "N/A",
                            row.col[3] if len(row.col) > 3 else "N/A",
                        )
                    )

            selective_table = simple_table(
                [
                    ("Criteria Name", {"style": "value"}),
                    ("Forward To", {"style": "success"}),
                    ("Time Schedule", {"style": "label"}),
                    ("Call From", {"style": "label"}),
                ],
                rows,
            )

            console.print(
                section_panel(selective_table, title="Selective Call Forwarding")
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
            append_status(forward_text, fwd.is_active == "true")
        console.print(section_panel(forward_text, title="VM Forwards"))


def _print_memberships(
    result: AutomationResult[UserDigestResult],
) -> None:
    """Print membership information in a tree view."""
    membership_tree = Tree(Text("Memberships", style="subheader"))

    # Call Centers
    if result.payload.call_center_membership:
        cc_branch = membership_tree.add(Text("Call Centers", style="accent"))
        for cc in result.payload.call_center_membership:
            acd_state_color = (
                "success" if cc.agent_acd_state == "Available" else "warning"
            )
            cc_available = cc.agent_cc_available == "true"
            cc_branch.add(
                f"[value]{cc.call_center_name}[/] - "
                f"[label]{cc.call_center_id}[/] - "
                f"[{acd_state_color}]{cc.agent_acd_state}[/] - "
                f"Available for CC {status_icon(cc_available)}"
            )

    # Hunt Groups
    if result.payload.hunt_group_membership:
        hg_branch = membership_tree.add(Text("Hunt Groups", style="accent"))
        for hg in result.payload.hunt_group_membership:
            hg_branch.add(
                f"[value]{hg.hunt_group_name}[/] - [label]{hg.hunt_group_id}[/]"
            )

    # Pickup Groups
    if result.payload.call_pickup_group_membership:
        cpu = result.payload.call_pickup_group_membership
        pu_branch = membership_tree.add(Text("Call Pickup Groups", style="accent"))
        pu_branch.add(f"[value]{cpu.call_pickup_group_name}")

    console.print(section_panel(membership_tree))


def _print_devices(user_details) -> None:
    """Print registered devices information."""
    if user_details.devices:
        device_table = simple_table(
            [
                ("Device Name", {"style": "value", "min_width": 20}),
                ("Type", {"style": "label", "min_width": 15}),
                ("Lineport", {"style": "label", "min_width": 15}),
                ("Registered", {"min_width": 15}),
            ],
            [
                (
                    device.device_name or "N/A",
                    device.device_type or "N/A",
                    device.line_port or "N/A",
                    status_icon(device.is_registered),
                )
                for device in user_details.devices
            ],
        )

        console.print(section_panel(device_table, title="Devices"))


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
