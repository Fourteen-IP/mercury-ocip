from typing import Optional, Type
import importlib.metadata
from importlib.metadata import EntryPoint
import inspect

from mercury_ocip.utils.defines import to_snake_case

from mercury_ocip.client import BaseClient
from mercury_ocip.bulk import BulkOperations
from mercury_ocip.automate import AutomationTasks
from mercury_ocip.plugins.base_plugin import BasePlugin


class Agent:
    __instance: Optional["Agent"] = None
    _installed_plugins: list[EntryPoint] = []

    @classmethod
    def get_instance(cls: Type["Agent"], client: BaseClient) -> "Agent":
        """
        Singleton implementation for Agent object.

        Args:
            client (BaseClient): Client object to be used in the scripts.

        Returns:
            Agent: The singleton instance of the Agent class.
        """
        if cls.__instance is None:
            cls.__instance = cls(client)
        return cls.__instance

    def __init__(self, client: BaseClient) -> None:
        if self.__instance is not None:
            raise Exception("Singleton cannot be instantiated more than once!")
        self.client = client
        self.logger = client.logger
        self.bulk = BulkOperations(client)
        self.automate = AutomationTasks(client)
        self.logger.info("Agent initialized")
        self.load_plugins()

    def load_plugins(self) -> None:
        entry_points = importlib.metadata.entry_points()
        plugin_group = entry_points.select(group="mercury_ocip.plugins")

        for entry_point in plugin_group:
            try:
                plugin_class = entry_point.load()

                # Check if it's actually a BasePlugin subclass
                if not (
                    inspect.isclass(plugin_class)
                    and issubclass(plugin_class, BasePlugin)
                    and plugin_class is not BasePlugin
                ):
                    continue

                plugin_instance = plugin_class(self.client)
                plugin_name = to_snake_case(
                    getattr(plugin_instance, "name", entry_point.name)
                )
                setattr(self, plugin_name, plugin_instance)
                self._installed_plugins.append(entry_point)
                self.logger.debug(f"Successfully loaded plugin: {entry_point.name}")
            except Exception as e:
                self.logger.error(f"Failed to load plugin {entry_point.name}: {e}")

    def list_plugins(self) -> list[EntryPoint]:
        return self._installed_plugins
