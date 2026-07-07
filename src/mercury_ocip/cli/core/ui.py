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

from rich import box
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

_debug = False


def debug(enabled: bool) -> None:
    global _debug
    _debug = enabled


def debug_enabled() -> bool:
    return _debug


_quit_hint = False


def set_quit_hint(active: bool) -> None:
    """Arms/disarms the "press Ctrl+C again to quit" bottom-toolbar hint.

    Kept as toggleable state (like debug()) rather than a printed line, so
    the main loop's first Ctrl+C doesn't scroll a new line into the
    terminal — the toolbar just updates in place on the next prompt.
    """
    global _quit_hint
    _quit_hint = active


def quit_hint_active() -> bool:
    return _quit_hint


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

    def step(self, message: str, ok: bool = True) -> None:
        """Report one completed step of a multi-step operation.

        Prints a ✔/✘ line WITHOUT stopping the spinner, so successive steps
        stack above the live status while the operation continues. Pair with
        update() to describe the next step being worked on.
        """
        if ok:
            self._console.print(f"🗸 {message}", style="success")
        else:
            self._console.print(f"🗴 {message}", style="error")

    def success(self, message: str) -> None:
        self.stop()
        self._console.print(f"🗸 {message}", style="success")

    def fail(self, message: str) -> None:
        self.stop()
        self._console.print(f"🗴 {message}", style="error")

    def warn(self, message: str) -> None:
        self.stop()
        self._console.print(f"🛆 {message}", style="warning")

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
        # Fall back to the exception type when str(e) is empty (e.g. a bare
        # assert), and escape so bracketed text in server messages renders
        # literally instead of being parsed as Rich markup.
        detail = str(e).strip() or type(e).__name__
        console.print(f"✘ {escape(detail)}", style="error")
        if _debug:
            console.print(f"[dim]{escape(traceback.format_exc())}[/]")
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


def kv_table(
    items: Iterable[tuple[str, str]], columns: int = 1, label_width: int = 20
) -> Table:
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


def status_icon(
    ok: bool, true_style: str = "success", false_style: str = "error"
) -> str:
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


def _hex_to_rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)


def gradient_text(text: str, start: str, end: str) -> Text:
    """Colour each line of `text` along a gradient from `start` to `end` (hex).

    Used for the startup splash art so it reads as one deliberate piece of
    branding instead of a flat block of a single colour.
    """
    lines = text.split("\n")
    steps = max(len(lines) - 1, 1)
    c1, c2 = _hex_to_rgb(start), _hex_to_rgb(end)

    result = Text()
    for i, line in enumerate(lines):
        t = i / steps
        r, g, b = (round(c1[c] + (c2[c] - c1[c]) * t) for c in range(3))
        result.append(line, style=f"#{r:02x}{g:02x}{b:02x}")
        if i < len(lines) - 1:
            result.append("\n")
    return result
