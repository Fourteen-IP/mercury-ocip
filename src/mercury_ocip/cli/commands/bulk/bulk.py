import os

from prompt_toolkit.completion import PathCompleter

from mercury_ocip.cli.core import Param, cli, operation
from mercury_ocip.cli.globals import MERCURY_CLI

console = MERCURY_CLI.console()

cli.describe("bulk", "Bulk operations for various entities")


def register_bulk_csv_command(path: str, method: str, entity_name: str, meta: str):
    """Register a 'bulk <op> <entity> <file_path>' command that runs a CSV
    method on the agent's bulk object."""

    def _run(file_path: str):
        run_bulk_csv(method, entity_name, file_path)

    cli.register(
        path,
        _run,
        meta=meta,
        params=[Param("file_path", source=PathCompleter(), meta="Path to CSV")],
    )


def run_bulk_csv(bulk_command: str, entity_name: str, file_path: str):
    """Run a bulk CSV operation with spinner, validation and result reporting.

    Args:
        bulk_command: The bulk method name to call on the bulk object.
        entity_name: The name of the entity being processed (for display).
        file_path: Path to the CSV file.
    """
    if not file_path.lower().endswith(".csv"):
        console.print("✘ Provided file is not a CSV.", style="error")
        return

    if not os.path.exists(file_path):
        console.print(f"✘ File not found: {file_path}", style="error")
        return

    with operation("Processing CSV...") as op:
        bulk_obj = MERCURY_CLI.agent().bulk
        bulk_method = getattr(bulk_obj, bulk_command, None)

        if not bulk_method:
            raise ValueError(f"Bulk method {bulk_command} not found.")

        output = bulk_method(file_path)

        failed_rows = [r for r in output if not r.get("success", False)]
        success_count = len(output) - len(failed_rows)

        if not failed_rows:
            op.success(f"All {success_count} {entity_name} processed successfully.")
            return

        op.fail(
            f"{len(failed_rows)} {entity_name} failed to process. "
            f"{success_count} succeeded."
        )
        console.print("\n[bold]Failed rows details:[/]")
        for row in failed_rows:
            _print_failed_row(row)


def _print_failed_row(row: dict):
    row_index = (
        row.get("index", "Unknown") + 1
        if isinstance(row.get("index"), int)
        else "Unknown"
    )
    error_msg = row.get("response") or row.get("error") or "Unknown error"
    detail_msg = row.get("detail", "")
    data = row.get("data", {})
    identifier = (
        data.get("user_id")
        or data.get("service_user_id")
        or data.get("group_id")
        or "Unknown"
    )

    console.print(f"\n  [yellow]Row {row_index}[/] ([cyan]{identifier}[/]):")
    console.print(f"    [error]Error:[/] {error_msg}")
    if detail_msg:
        console.print(f"    [error]Detail:[/] {detail_msg}")
