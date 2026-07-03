from abc import ABC, abstractmethod
from contextlib import AbstractContextManager
from typing import Dict, Type, Any
from mercury_ocip.client import BaseClient


class PluginCommand(ABC):
    name: str
    description: str
    params: dict[str, dict[str, Any]] = {}

    def __init__(self, plugin: "BasePlugin"):
        self.plugin = plugin
        self.client = plugin.client

    @abstractmethod
    def execute(self, **kwargs):
        pass

    @property
    def console(self):
        """The CLI's themed Rich console, for plugins that want it.

        Optional: `execute()` can keep using plain `print()` if it doesn't
        care about theming. Only import the CLI lazily here so the core
        library (used standalone, without the CLI) has no hard dependency
        on it.
        """
        from mercury_ocip.cli.globals import MERCURY_CLI

        return MERCURY_CLI.console()

    def operation(self, message: str) -> AbstractContextManager:
        """The same spinner/success/fail helper native CLI commands use.

        Usage:
            with self.operation("Doing the thing...") as op:
                ...
                op.success("Done")
        """
        from mercury_ocip.cli.core import operation

        return operation(message)


class BasePlugin(ABC):
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
