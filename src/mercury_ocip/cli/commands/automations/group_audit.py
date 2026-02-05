from mercury_ocip.cli.globals import MERCURY_CLI
from mercury_ocip.cli.utils.service_group_id_callable import (
    _get_group_id_completions,
    _get_service_provider_id_completions,
)
from mercury_ocip.automate.base_automation import AutomationResult

from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.text import Text

console = MERCURY_CLI.console()
completer = MERCURY_CLI.completer()


def _format_audit_output(result: AutomationResult) -> None:
    """Format and display audit result using Rich."""

    audit = result.payload

    # Header
    console.print(
        Panel(
            Text("Group Audit Report", style="header", justify="center"),
            style="divider",
        )
    )

    # Group Details Section
    if audit.group_details:
        details = audit.group_details

        details_table = Table(box=None, show_header=False, padding=(0, 2), expand=True)
        details_table.add_column(style="label", width=30)
        details_table.add_column(style="value")

        details_table.add_row("Group Name", details.group_name or "N/A")
        details_table.add_row("Group ID", details.group_id or "N/A")
        details_table.add_row(
            "Service Provider ID", details.service_provider_id or "N/A"
        )
        details_table.add_row("Default Domain", details.default_domain or "N/A")

        if hasattr(details, "user_count") and hasattr(details, "user_limit"):
            details_table.add_row(
                "User Count", f"{details.user_count} / {details.user_limit}"
            )

        details_table.add_row(
            "Time Zone", details.time_zone_display_name or details.time_zone or "N/A"
        )

        if hasattr(details, "calling_line_id_name"):
            details_table.add_row(
                "Calling Line ID Name", details.calling_line_id_name or "N/A"
            )

        if hasattr(details, "calling_line_id_phone_number"):
            details_table.add_row(
                "Calling Line ID Phone", details.calling_line_id_phone_number or "N/A"
            )

        if hasattr(details, "calling_line_id_display_phone_number"):
            details_table.add_row(
                "Display Phone Number",
                details.calling_line_id_display_phone_number or "N/A",
            )

        console.print(
            Panel(
                details_table,
                title="[bold #d8bbff]Group Details[/]",
                border_style="divider",
            )
        )

    # License Breakdown - Group Services
    if (
        audit.license_breakdown
        and audit.license_breakdown.group_services_authorization_table
    ):
        services_table = Table(box=box.SIMPLE, show_header=True, expand=True)
        services_table.add_column("Service", style="label")
        services_table.add_column("Count", style="value", justify="right")

        for service, count in sorted(
            audit.license_breakdown.group_services_authorization_table.items()
        ):
            services_table.add_row(service, str(count))

        console.print(
            Panel(
                services_table,
                title="[bold #d8bbff]Group Services Authorization[/]",
                border_style="divider",
            )
        )

    # License Breakdown - Service Packs
    if (
        audit.license_breakdown
        and audit.license_breakdown.service_packs_authorization_table
    ):
        packs_table = Table(box=box.SIMPLE, show_header=True, expand=True)
        packs_table.add_column("Service Pack", style="label")
        packs_table.add_column("Count", style="value", justify="right")

        for pack, count in sorted(
            audit.license_breakdown.service_packs_authorization_table.items()
        ):
            packs_table.add_row(pack, str(count))

        console.print(
            Panel(
                packs_table,
                title="[bold #d8bbff]Service Packs Authorization[/]",
                border_style="divider",
            )
        )

    # License Breakdown - User Services
    if (
        audit.license_breakdown
        and audit.license_breakdown.user_services_authorization_table
    ):
        user_services_table = Table(box=box.SIMPLE, show_header=True, expand=True)
        user_services_table.add_column("User Service", style="label")
        user_services_table.add_column("Count", style="value", justify="right")

        for service, count in sorted(
            audit.license_breakdown.user_services_authorization_table.items()
        ):
            user_services_table.add_row(service, str(count))

        console.print(
            Panel(
                user_services_table,
                title="[bold #d8bbff]User Services Authorization[/]",
                border_style="divider",
            )
        )

    # Group DNs
    if audit.group_dns:
        dns_text = Text()
        dns_text.append("Total DNs: ", style="label")
        dns_text.append(f"{audit.group_dns.total}\n\n", style="value")

        if audit.group_dns.numbers:
            sorted_numbers = sorted(
                audit.group_dns.numbers,
                key=lambda x: int(x) if x.isdigit() else float("inf"),
            )
            numbers_str = ", ".join(sorted_numbers)
            dns_text.append(numbers_str, style="value")
        else:
            dns_text.append("No directory numbers found", style="label")

        console.print(
            Panel(
                dns_text,
                title="[bold #d8bbff]Group Directory Numbers[/]",
                border_style="divider",
            )
        )
    else:
        console.print(
            Panel(
                Text("Directory number information not available", style="label"),
                title="[bold #d8bbff]Group Directory Numbers[/]",
                border_style="divider",
            )
        )


@completer.automations.action(
    "group_audit", display_meta="Perform a comprehensive audit of a group"
)
@completer.param(
    _get_service_provider_id_completions,
    display_meta="Service Provider ID",
    cast=str,
)
@completer.param(_get_group_id_completions, display_meta="Group ID", cast=str)
def _group_audit(service_provider_id: str, group_id: str):
    """
    Perform a comprehensive audit of a group.

    Args:
        service_provider_id: The ID of the service provider.
        group_id: The ID of the group to audit.
    """
    with console.status(
        "[cyan]Performing group audit...", spinner="dots", spinner_style="cyan"
    ) as status:
        try:
            result = MERCURY_CLI.agent().automate.audit_group(
                service_provider_id=service_provider_id,
                group_id=group_id,
            )

            if result.ok:
                status.stop()
                _format_audit_output(result)
            else:
                status.stop()
                console.print(
                    f"✘ Group audit failed for Group ID '{group_id}'.", style="red"
                )

        except Exception as e:
            status.stop()
            console.print(f"✘ {e}", style="red")
