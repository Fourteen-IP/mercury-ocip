from mercury_ocip.cli.globals import MERCURY_CLI
import traceback
import os

completer = MERCURY_CLI.completer()
console = MERCURY_CLI.console()

completer.bulk.display_meta = "Bulk operations for various entities"


def _cli_wrap_verification(bulk_command: str, entity_name: str, **kwargs):
    """
    Wrapper to handle bulk CSV operations with spinner and error handling.

    Args:
        bulk_command: The bulk method name to call on the bulk object.
        entity_name: The name of the entity being processed (for display purposes).
        **kwargs: Additional keyword arguments, expects 'file_path'.
    """

    file_path = kwargs.get("file_path")

    # Validate file before starting spinner
    if not file_path.lower().endswith(".csv"):
        console.print("✘ Provided file is not a CSV.", style="red")
        return

    if not os.path.exists(file_path):
        console.print(f"✘ File not found: {file_path}", style="red")
        return

    with console.status(
        "[cyan]Processing CSV...", spinner="dots", spinner_style="cyan"
    ) as status:
        try:
            bulk_obj = MERCURY_CLI.agent().bulk

            bulk_method = getattr(bulk_obj, bulk_command, None)

            if not bulk_method:
                raise ValueError(f"Bulk method {bulk_command} not found.")

            output = bulk_method(file_path)

            success_count = sum(1 for result in output if result.get("success", False))
            failed_rows = [
                result for result in output if not result.get("success", False)
            ]
            failure_count = len(output) - success_count

            status.stop()

            if failure_count == 0:
                console.print(
                    f"✔ All {success_count} {entity_name} processed successfully.",
                    style="green",
                )
            else:
                console.print(
                    f"✘ {failure_count} {entity_name} failed to process. {success_count} succeeded.",
                    style="red",
                )
                console.print("\n[bold]Failed rows details:[/]")
                for row in failed_rows:
                    row_index = (
                        row.get("index", "Unknown") + 1
                        if isinstance(row.get("index"), int)
                        else "Unknown"
                    )
                    error_msg = (
                        row.get("response") or row.get("error") or "Unknown error"
                    )
                    detail_msg = row.get("detail", "")
                    user_id = row.get("data", {}).get("user_id", "Unknown")

                    console.print(
                        f"\n  [yellow]Row {row_index}[/] (User: [cyan]{user_id}[/]):"
                    )
                    console.print(f"    [red]Error:[/] {error_msg}")
                    if detail_msg:
                        console.print(f"    [red]Detail:[/] {detail_msg}")

        except Exception as e:
            status.stop()
            error_details = traceback.format_exc()
            console.print(f"✘ Error processing CSV: {str(e)}", style="red")
            console.print(f"\n[dim]Full traceback:\n{error_details}[/]")
