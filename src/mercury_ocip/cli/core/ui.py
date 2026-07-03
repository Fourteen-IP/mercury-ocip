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
from typing import Iterator

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
        self._console.print(f"⚠ {message}", style="yellow")

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
