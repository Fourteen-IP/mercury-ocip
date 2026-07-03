"""CLI core: command tree, tokenizer, completer, dispatcher and UI helpers.

The module-level `cli` object is the global command registry that all
command files register into:

    from mercury_ocip.cli.core import cli, operation

    @cli.command("automations find_alias", meta="Find the entity behind an alias")
    @cli.param("alias", meta="Alias Number")
    def _find_alias(alias: str): ...
"""

from mercury_ocip.cli.core.completer import MercuryCompleter, make_bottom_toolbar
from mercury_ocip.cli.core.dispatcher import dispatch as _dispatch
from mercury_ocip.cli.core.errors import (
    BadParamError,
    CLIError,
    CommandAborted,
    CommandSyntaxError,
    IncompleteCommandError,
    MissingParamError,
    TooManyArgsError,
    UnknownCommandError,
)
from mercury_ocip.cli.core.tree import CommandRegistry, CompletionContext, Param
from mercury_ocip.cli.core.ui import (
    Operation,
    append_status,
    debug,
    debug_enabled,
    gradient_text,
    kv_table,
    operation,
    quit_hint_active,
    report_header,
    section_panel,
    set_quit_hint,
    simple_table,
    status_icon,
)

cli = CommandRegistry()


def dispatch(line: str, interactive: bool = True):
    """Execute a command line against the global registry."""
    return _dispatch(cli, line, interactive=interactive)


__all__ = [
    "cli",
    "dispatch",
    "operation",
    "Operation",
    "debug",
    "debug_enabled",
    "set_quit_hint",
    "quit_hint_active",
    "report_header",
    "section_panel",
    "kv_table",
    "simple_table",
    "status_icon",
    "append_status",
    "gradient_text",
    "CommandRegistry",
    "CompletionContext",
    "Param",
    "MercuryCompleter",
    "make_bottom_toolbar",
    "CLIError",
    "CommandSyntaxError",
    "UnknownCommandError",
    "IncompleteCommandError",
    "MissingParamError",
    "BadParamError",
    "TooManyArgsError",
    "CommandAborted",
]
