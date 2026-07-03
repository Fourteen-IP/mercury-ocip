from mercury_ocip.cli.core import (
    cli,
    kv_table,
    operation,
    report_header,
    section_panel,
    simple_table,
)
from mercury_ocip.cli.globals import MERCURY_CLI
from mercury_ocip.cli.utils.service_group_id_callable import (
    group_ids,
    service_provider_ids,
)
from mercury_ocip.automate.base_automation import AutomationResult

from rich.text import Text

console = MERCURY_CLI.console()


def _format_audit_output(result: AutomationResult) -> None:
    """Format and display audit result using Rich."""

    audit = result.payload

    console.print(report_header("Group Audit Report"))

    # Group Details Section
    if audit.group_details:
        details = audit.group_details

        rows = [
            ("Group Name", details.group_name or "N/A"),
            ("Group ID", details.group_id or "N/A"),
            ("Service Provider ID", details.service_provider_id or "N/A"),
            ("Default Domain", details.default_domain or "N/A"),
        ]

        if hasattr(details, "user_count") and hasattr(details, "user_limit"):
            rows.append(("User Count", f"{details.user_count} / {details.user_limit}"))

        rows.append(
            (
                "Time Zone",
                details.time_zone_display_name or details.time_zone or "N/A",
            )
        )

        if hasattr(details, "calling_line_id_name"):
            rows.append(("Calling Line ID Name", details.calling_line_id_name or "N/A"))

        if hasattr(details, "calling_line_id_phone_number"):
            rows.append(
                (
                    "Calling Line ID Phone",
                    details.calling_line_id_phone_number or "N/A",
                )
            )

        if hasattr(details, "calling_line_id_display_phone_number"):
            rows.append(
                (
                    "Display Phone Number",
                    details.calling_line_id_display_phone_number or "N/A",
                )
            )

        console.print(
            section_panel(kv_table(rows, label_width=30), title="Group Details")
        )

    # License Breakdown - Group Services
    if (
        audit.license_breakdown
        and audit.license_breakdown.group_services_authorization_table
    ):
        console.print(
            section_panel(
                _authorization_table(
                    audit.license_breakdown.group_services_authorization_table
                ),
                title="Group Services Authorization",
            )
        )

    # License Breakdown - Service Packs
    if (
        audit.license_breakdown
        and audit.license_breakdown.service_packs_authorization_table
    ):
        console.print(
            section_panel(
                _authorization_table(
                    audit.license_breakdown.service_packs_authorization_table
                ),
                title="Service Packs Authorization",
            )
        )

    # License Breakdown - User Services
    if (
        audit.license_breakdown
        and audit.license_breakdown.user_services_authorization_table
    ):
        console.print(
            section_panel(
                _authorization_table(
                    audit.license_breakdown.user_services_authorization_table
                ),
                title="User Services Authorization",
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

        console.print(section_panel(dns_text, title="Group Directory Numbers"))
    else:
        console.print(
            section_panel(
                Text("Directory number information not available", style="label"),
                title="Group Directory Numbers",
            )
        )


def _authorization_table(table: dict):
    return simple_table(
        [("Service", {"style": "label"}), ("Count", {"style": "value", "justify": "right"})],
        [(service, count) for service, count in sorted(table.items())],
    )


@cli.command("automations group_audit", meta="Perform a comprehensive audit of a group")
@cli.param("service_provider_id", source=service_provider_ids, meta="Service Provider ID")
@cli.param("group_id", source=group_ids, meta="Group ID")
def _group_audit(service_provider_id: str, group_id: str):
    """
    Perform a comprehensive audit of a group.

    Args:
        service_provider_id: The ID of the service provider.
        group_id: The ID of the group to audit.
    """
    with operation("Performing group audit...") as op:
        result = MERCURY_CLI.agent().automate.audit_group(
            service_provider_id=service_provider_id,
            group_id=group_id,
        )

        if result.ok:
            op.stop()
            _format_audit_output(result)
        else:
            op.fail(f"Group audit failed for Group ID '{group_id}'.")
