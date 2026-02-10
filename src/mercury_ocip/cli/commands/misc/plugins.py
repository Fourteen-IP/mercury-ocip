from action_completer.types import Empty
from action_completer.completer import ActionCompleter, ActionParam
from mercury_ocip.cli.globals import MERCURY_CLI
from mercury_ocip.utils.defines import to_snake_case

completer: ActionCompleter = MERCURY_CLI.completer()

plugin_group = completer.group("plugin", display_meta="Used to view and manage plugins")


@plugin_group.action("list", display_meta="List all available plugins")
def _list_plugins():
    plugins = MERCURY_CLI.agent().list_plugins()
    for plugin in plugins:
        print(plugin.name)


def _create_plugin_command(plugin_instance, command_class, full_command_name):
    """Create a command function that executes the plugin command.

    Args:
        plugin_instance: The instantiated plugin object
        command_class: The command class to instantiate
        full_command_name: Full name for reference (e.g., 'module.Plugin.command')

    Returns:
        A function that instantiates and executes the command
    """

    def command_function(*args, **kwargs):
        try:
            command_instance = command_class(plugin_instance)
        except Exception as e:
            print(f"Error instantiating command class {command_class}: {e}")
            raise

        # If args are provided, we need to map them to the expected param names
        if args and not kwargs:
            # Get param names from command class
            param_names = (
                list(command_class.params.keys())
                if hasattr(command_class, "params")
                else []
            )
            kwargs = dict(zip(param_names, args))

        try:
            return command_instance.execute(**kwargs)
        except Exception as e:
            print(f"Error executing command {full_command_name}: {e}")
            raise

    return command_function


def load_plugins() -> None:
    for plugin in MERCURY_CLI.agent()._discoverable_plugins:
        plugin_class, plugin_instance, entry_point = plugin

        named_group = plugin_group.group(
            to_snake_case(plugin_class.__name__),
            display_meta=f"{plugin_instance.description}",
        )

        if hasattr(plugin_instance, "get_commands"):
            commands = plugin_instance.get_commands()

            for command_name, command_class in commands.items():
                full_command_name = f"{plugin_class.__name__}.{command_name}"

                command_func = _create_plugin_command(
                    plugin_instance, command_class, full_command_name
                )

                cmd_description = getattr(command_class, "description", "")
                cmd_params = getattr(command_class, "params", {})

                action_params = []

                for param_name, param_info in cmd_params.items():
                    if (
                        source := param_info.get("source", None)
                    ) is not Empty or callable(source):
                        param_name = (
                            None  # Hide from display if source is Empty or callable
                        )

                    action_params.append(
                        ActionParam(
                            source=param_info.get("source", None),
                            cast=param_info.get("cast", str),
                            display=param_name,
                            display_meta=param_info.get(
                                "help", param_info.get("description", "")
                            ),
                        )
                    )

                named_group.action(
                    command_name, display_meta=cmd_description, params=action_params
                )(command_func)
