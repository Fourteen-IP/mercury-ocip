"""Shared output helpers for CLI commands.

The operation() context manager owns the spinner lifecycle, the final
success/failure line, and exception rendering — so command bodies only
contain the actual work:

    with operation("Blocking number...") as op:
        result = agent.automate.block_number_in_enterprise(...)
        if result.ok:
            op.success(f"Blocked {number} in {count} groups")
        else:
            op.fail(f"Failed to block {number}")

Any exception raised inside the block is caught, printed in the standard
error style and suppressed (the CLI keeps running). Set debug(True) to
include full tracebacks.
"""

import traceback
from contextlib import contextmanager
from typing import Iterable, Iterator

from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

_debug = False


def debug(enabled: bool) -> None:
    global _debug
    _debug = enabled


def debug_enabled() -> bool:
    return _debug


def _console():
    # Imported lazily to avoid a circular import (globals imports core).
    from mercury_ocip.cli.globals import MERCURY_CLI

    return MERCURY_CLI.console()


class Operation:
    def __init__(self, console, status):
        self._console = console
        self._status = status
        self._stopped = False

    def stop(self) -> None:
        """Stop the spinner (e.g. before printing custom panels)."""
        if not self._stopped:
            self._status.stop()
            self._stopped = True

    def update(self, message: str) -> None:
        self._status.update(f"[cyan]{message}")

    def success(self, message: str) -> None:
        self.stop()
        self._console.print(f"✔ {message}", style="success")

    def fail(self, message: str) -> None:
        self.stop()
        self._console.print(f"✘ {message}", style="error")

    def warn(self, message: str) -> None:
        self.stop()
        self._console.print(f"⚠ {message}", style="warning")

    def print(self, *args, **kwargs) -> None:
        self.stop()
        self._console.print(*args, **kwargs)


@contextmanager
def operation(message: str) -> Iterator[Operation]:
    console = _console()
    status = console.status(f"[cyan]{message}", spinner="dots", spinner_style="cyan")
    op = Operation(console, status)
    status.start()
    try:
        yield op
    except Exception as e:
        op.stop()
        console.print(f"✘ {e}", style="error")
        if _debug:
            console.print(f"[dim]{traceback.format_exc()}[/]")
    finally:
        op.stop()


def report_header(title: str) -> Panel:
    """The centred title panel every automation report opens with."""
    return Panel(Text(title, style="header", justify="center"), style="divider")


def section_panel(content, title: str | None = None) -> Panel:
    """A bordered section panel with a themed (accent) title.

    Replaces the repeated `Panel(..., title="[bold #d8bbff]X[/]",
    border_style="divider")` pattern so panel styling lives in one place.
    """
    kwargs = {"border_style": "divider"}
    if title:
        kwargs["title"] = f"[accent]{title}[/]"
    return Panel(content, **kwargs)


def kv_table(items: Iterable[tuple[str, str]], columns: int = 1, label_width: int = 20) -> Table:
    """A borderless label/value table, `columns` label/value pairs per row.

    `items` is a flat sequence of (label, value) pairs; it's chunked into
    rows of `columns` pairs each (the last row is padded if ragged).
    """
    table = Table(box=None, show_header=False, padding=(0, 2), expand=True)
    for _ in range(columns):
        table.add_column(style="label", width=label_width)
        table.add_column(style="value")

    items = list(items)
    for i in range(0, len(items), columns):
        row_items = items[i : i + columns]
        cells: list[str] = []
        for label, value in row_items:
            cells.append(label)
            cells.append(value)
        cells.extend([""] * (columns * 2 - len(cells)))
        table.add_row(*cells)
    return table


def simple_table(
    columns: Iterable[str | tuple[str, dict]], rows: Iterable[Iterable]
) -> Table:
    """A headered `box.SIMPLE` table.

    Each entry in `columns` is either a header string, or a
    `(header, add_column_kwargs)` tuple for styled/justified/min-width columns.
    """
    table = Table(box=box.SIMPLE, show_header=True, expand=True)
    for col in columns:
        if isinstance(col, tuple):
            header, kwargs = col
        else:
            header, kwargs = col, {}
        table.add_column(header, **kwargs)

    for row in rows:
        table.add_row(*("" if cell is None else str(cell) for cell in row))
    return table


def status_icon(ok: bool, true_style: str = "success", false_style: str = "error") -> str:
    """A themed ✓/✗ marker, replacing ad-hoc emoji/hex-coded status text.

    Returns Rich *markup* (e.g. "[success]✓[/]") — safe to drop into an
    f-string passed to console.print()/Panel()/Table cells/Tree labels,
    which all parse markup. It is NOT safe to pass to Text.append(), which
    treats the string as literal characters instead of parsing the tags —
    use append_status() for that.
    """
    return f"[{true_style}]✓[/]" if ok else f"[{false_style}]✗[/]"


def append_status(
    text: Text, ok: bool, true_style: str = "success", false_style: str = "error"
) -> None:
    """Append a themed ✓/✗ glyph to a rich Text object.

    Text.append() doesn't parse markup (unlike Panel/Table/Tree), so
    status_icon()'s markup string would print its tags literally here —
    this applies the style directly instead.
    """
    text.append("✓" if ok else "✗", style=true_style if ok else false_style)
