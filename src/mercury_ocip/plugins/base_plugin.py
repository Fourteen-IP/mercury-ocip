from abc import ABC, abstractmethod
from contextlib import AbstractContextManager
from typing import Dict, Generic, Type, TypeVar, Any
from mercury_ocip.client import BaseClient

TPlugin = TypeVar("TPlugin", bound="BasePlugin")


class CLIAccessMixin:
    """Lazy access to the CLI's UI helpers for plugins and their commands.

    Everything here imports the CLI at call time only, so the core library
    (used standalone, without the CLI) has no hard dependency on it.
    """

    @property
    def console(self):
        """The CLI's themed Rich console."""
        from mercury_ocip.cli.globals import MERCURY_CLI

        return MERCURY_CLI.console()

    @property
    def prompt_session(self):
        """The CLI's prompt-toolkit session, for commands that need to prompt."""
        from mercury_ocip.cli.globals import MERCURY_CLI

        return MERCURY_CLI.session()

    def operation(self, message: str) -> AbstractContextManager:
        """The same spinner/success/fail helper native CLI commands use.

        Usage:
            with self.operation("Doing the thing...") as op:
                op.update("Working on step one...")
                ...
                op.step("Step one done")
                ...
                op.success("Done")

        Note: operations don't nest (one live spinner at a time) — the code
        that owns the workflow should own the operation.
        """
        from mercury_ocip.cli.core import operation

        return operation(message)


class PluginCommand(CLIAccessMixin, ABC, Generic[TPlugin]):
    name: str
    description: str
    params: dict[str, dict[str, Any]] = {}

    def __init__(self, plugin: TPlugin):
        self.plugin = plugin
        self.client = plugin.client

    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> None:
        """Run the command.

        Concrete commands should declare the real parameters by name, e.g.
        ``def execute(self, service_provider_id: str, group_id: str) -> None``.
        The CLI invokes commands with keyword arguments matching ``params``.
        """


class BasePlugin(CLIAccessMixin, ABC):
    """Base class for Mercury OCIP plugins."""

    name: str = ""
    version: str = "0.0.0"
    description: str = ""

    def __init__(self, client: BaseClient):
        self.client = client

    @abstractmethod
    def get_commands(self) -> Dict[str, Type[PluginCommand]]:
        """Return a dictionary of command names to command classes."""
        pass
