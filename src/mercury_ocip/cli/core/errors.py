class CLIError(Exception):
    """Base class for errors raised by the CLI core."""


class CommandSyntaxError(CLIError):
    """The input line could not be tokenized (e.g. unclosed quote)."""


class UnknownCommandError(CLIError):
    """The input did not resolve to a registered command."""

    def __init__(self, message: str, suggestions: list[str] | None = None):
        super().__init__(message)
        self.suggestions = suggestions or []


class IncompleteCommandError(CLIError):
    """The input resolved to a group, not an executable command."""

    def __init__(self, message: str, subcommands: list[str] | None = None):
        super().__init__(message)
        self.subcommands = subcommands or []


class MissingParamError(CLIError):
    """A required parameter was not provided."""


class BadParamError(CLIError):
    """A parameter value failed casting/validation."""


class TooManyArgsError(CLIError):
    """More arguments were provided than the command accepts."""


class CommandAborted(CLIError):
    """The user cancelled an interactive prompt (Ctrl+C / Ctrl+D)."""
