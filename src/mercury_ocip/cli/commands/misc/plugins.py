import inspect

from prompt_toolkit.completion import Completer

from mercury_ocip.cli.core import CompletionContext, Param, cli, simple_table
from mercury_ocip.cli.globals import MERCURY_CLI
from mercury_ocip.utils.defines import to_snake_case

cli.describe("plugin", "Used to view and manage plugins")


@cli.command("plugin list", meta="List all available plugins")
def _list_plugins():
    plugins = MERCURY_CLI.agent().list_plugins()
    table = simple_table(
        [("Name", {"style": "value"}), ("Entry Point", {"style": "label"})],
        [(plugin.name, plugin.value) for plugin in plugins],
    )
    MERCURY_CLI.console().print(table)


def _adapt_source(source):
    """Convert a plugin-declared param source to a core ParamSource.

    Plugins may declare:
        - None / an 'Empty' sentinel  -> free text
        - a prompt_toolkit Completer  -> passed through
        - a static iterable of str    -> passed through
        - a callable                  -> wrapped; supports both the new
          (ctx) signature and the legacy action_completer
          (action, param, value) signature.
    """
    if source is None:
        return None
    if getattr(source, "__name__", "") == "Empty" or type(source).__name__ == "Empty":
        return None
    if isinstance(source, Completer):
        return source
    if callable(source):

        def adapted(ctx: CompletionContext):
            try:
                params = inspect.signature(source).parameters
            except (TypeError, ValueError):
                params = {}
            if len(params) >= 3:  # legacy (action, param, value) signature
                return source(None, None, ctx.partial)
            return source(ctx)

        return adapted
    return source


def _create_plugin_command(plugin_instance, command_class):
    """Create a command function that executes the plugin command.

    Args:
        plugin_instance: The instantiated plugin object
        command_class: The command class to instantiate

    Returns:
        A function that instantiates and executes the command
    """

    def command_function(**kwargs):
        # Exceptions propagate untouched so the dispatcher's caller (the
        # command loop) prints them once, in the themed style, and so
        # special-cased exception types (e.g. MErrorSocketTimeout) are
        # still recognised there.
        command_instance = command_class(plugin_instance)
        return command_instance.execute(**kwargs)

    return command_function


def load_plugins() -> None:
    for plugin in MERCURY_CLI.agent()._discoverable_plugins:
        plugin_class, plugin_instance, entry_point = plugin

        plugin_name = to_snake_case(plugin_class.__name__)
        cli.describe(f"plugin {plugin_name}", plugin_instance.description or "")

        if not hasattr(plugin_instance, "get_commands"):
            continue

        for command_name, command_class in plugin_instance.get_commands().items():
            command_func = _create_plugin_command(plugin_instance, command_class)

            cmd_params = getattr(command_class, "params", {}) or {}
            params = [
                Param(
                    name=param_name,
                    source=_adapt_source(param_info.get("source")),
                    cast=param_info.get("cast", str),
                    meta=param_info.get("help", param_info.get("description", "")),
                    required=param_info.get("required", True),
                    default=param_info.get("default"),
                    greedy=param_info.get("greedy", False),
                )
                for param_name, param_info in cmd_params.items()
            ]

            cli.register(
                f"plugin {plugin_name} {command_name}",
                command_func,
                meta=getattr(command_class, "description", ""),
                params=params,
            )
