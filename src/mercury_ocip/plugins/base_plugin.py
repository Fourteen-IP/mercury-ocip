from abc import ABC, abstractmethod
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
