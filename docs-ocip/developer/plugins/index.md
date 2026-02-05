# Plugins

The agent supports a plugin architecture that allows developers to extend its functionality by creating custom plugins. Plugins can be used to add new features, integrate with external services, or modify existing behavior.

All plugins are discovered automatically at runtime using Python's entry point mechanism. This means that as long as a plugin is installed in the same environment as the agent, it will be detected and loaded without any additional configuration.

Since the CLI is essentially a wrapper around the main library, plugins created for the library will also be available in the CLI.

This runtime discovery, however, comes with some caveats. Plugins will not be shown by intellisense, and if there are any issues with the plugin (e.g., missing dependencies, errors during initialization), these will only be encountered at runtime when the plugin is loaded.

This was a specific choice to allow for confidential plugins that may not be publicly available to be used without requiring changes to the main codebase.

## Making a Plugin

Creating a plugin for the agent has been made to integrate with both tools, the main library and the CLI, because of this, some metadata is required, and some specifics steps needed to ensure your plugin is discoverable, and business logic is properly implemented.

This guide assumes you are not using the template repository. If you are using the template repository, you can skip the steps about setting up the project structure.

---

### Project Structure

!!! tip "Using UV"
    It is recommended to use UV to manage dependencies and setup the project. This can be achieved by running `uv init mercury-ocip-your-plugin-name` in your terminal. This will create a new directory with the necessary files to get started.

!!! warning "Naming Convention"
    Ensure that your module name begins with `mercury_ocip_` to comply with naming conventions, this helps in automatic discovery of plugins.

Your project structure should look like this:

```title="Project Structure"
mercury-ocip-your-plugin-name/
├── your_plugin_name
│   ├── __init__.py
│   └── code.py
├── .pythonversion
├── pyproject.toml
├── README.md
└── uv.lock
```

The amount of folders and files may vary depending on your setup, but the key part is having a main package folder (here `your_plugin_name`) containing your plugin code. However, it does not matter how many subfolders you have, as long as the entry point points to the correct location of your plugin class.

---

### pyproject.toml Configuration

Within your `pyproject.toml`, you need to define the entry points for your plugin. This is done under the `[tool.mercury_ocip.plugins]` section. Here is an example configuration:

```toml
[project.entry-points."mercury_ocip.plugins"]
your_plugin_name = "your_plugin_name.code:YourPluginClass"
```

As a more complete example, your `pyproject.toml` might look like this:

```toml
[project.entry-points."mercury_ocip.plugins"]
NumberMigration = "number_migration_plugin.code:NumberMigrationPlugin"
```

Inside the CLI, this will show as:

```title="plugins list"
Available Plugins:
- NumberMigration
```

!!! info
    If you really want to, you can have multiple plugins in the same package, just ensure that each entry point has a unique name and points to the correct class.

---

### Implementing the Plugin Class

In this section we will be following the example plugin, this is found at [mercury-ocip-example-plugin](https://github.com/Fourteen-IP/mercury-ocip-example-plugin).

First, you need to create a class for your plugin. This class should inherit from `mercury_ocip.plugins.BasePlugin`. This base class provides the necessary interface for the agent to interact with your plugin.

Here is the general setup:

```python
from mercury_ocip.plugins.base_plugin import BasePlugin

class ExamplePlugin(BasePlugin):
    """
    Example plugin demonstration.
    """

    name = "Example Plugin"
    version = "1.0.0"
    description = "Demonstrates the new plugin command structure."
```

The `name`, `version`, and `description` attributes provide metadata about your plugin. You can customize these to fit your plugin's purpose.

All business functions you want to reside in the plugin can be defined in here as normal functions:

```python
class ExamplePlugin(BasePlugin):
    """
    Example plugin demonstration.
    """

    name = "Example Plugin"
    version = "1.0.0"
    description = "Demonstrates the new plugin command structure."

    def greet_user(self, name: str) -> None:
        print(f"Hello, {name}! Welcome to Mercury OCIP.")

    def add_numbers(self, x: int, y: int) -> None:
        result = x + y
        print(f"{x} + {y} = {result}")

    def echo_string(self, string: str, etimes: int) -> None:
        for _ in range(etimes):
            print(string)
```

In this example, we have defined three methods: `greet_user`, `add_numbers`, and `echo_string`. These methods can be called by the agent when the plugin is loaded. 

However, to make these methods accessible via the CLI, we need to register them as commands.

---

### Implementing Plugin Commands

For commands to be properly displayed in autocomplete and help menus, they need to ineherit from `mercury_ocip.plugins.PluginCommand` and have their metadata defined.

The CLI library uses a custom ActionCompleter library for defining commands, and this introduces a new type I will explain here.

Lets "commandify" the previous methods:

```python
from mercury_ocip.plugins.base_plugin import BasePlugin, PluginCommand
from action_completer.types import Empty

class GreetCommand(PluginCommand):
    """
    Greet someone by name.
    """

    description = "Print a greeting for a user."
    params = {
        "name": {
            "cast": str,
            "source": None,  # Specify the source explicitly
            "description": "Name of the user to greet.",
            "help": "The name of the person you want to greet",  # Add help text
        }
    }

    def execute(self, name: str):
        return self.plugin.greet_user(name)

class EchoCommand(PluginCommand):
    """
    Echo a string a certain number of times.
    """

    description = "Echo a string a certain number of times."
    params = {
        "string": {
            "cast": str,  # Type to cast the parameter to
            "source": None,  # Where the autocomplete gets its data from
            "description": "String to echo.",  # Left hand side description
            "help": "The string you want to echo",  # right hand side help text
        },
        "etimes": {
            "cast": int,
            "source": [
                "1",
                "2",
                "3",
                "5",
                "10",
                "20",
                "50",
            ],
            "description": "Number of times to echo.",
            "help": "How many times to echo the string",
        },
    }

    def execute(self, string: str, etimes: int):
        return self.plugin.echo_string(string, etimes)

class AddCommand(PluginCommand):
    """
    Add two numbers.
    """

    description = "Add two integers."
    params = {
        "x": {
            "cast": int,
            "source": Empty,
            "description": "First number.",
            "help": "This is the first number to add.",
        },
        "y": {
            "cast": int,
            "source": Empty,
            "description": "Second number.",
            "help": "This is the second number to add.",
        },
    }

    def execute(self, x: int, y: int):
        return self.plugin.add_numbers(x, y)
```

Lets unpack the above code a bit, some aspects of the params dictionary can get hectic.

First of all, the first key is the parameter name, this has to match the name in the execute function.

The `cast` key defines the type the parameter should be cast to, this is important for ensuring the correct data type is used.

---

#### Source Key

The `source` key defines where the autocomplete gets its data from. This can be a list of strings for static options or a special value like `Empty` for no autocomplete. I will go through them here:

!!! note
    Source only defines the first part of autocomplete, there are 2 sections, the first left general description, and the second right side help text. Source only applies to the left side.

---

##### General Options

- `str` - A string value, can be anything, but any other value but the one specified will be rejected.
- `int` - An integer value, any non-integer will be rejected.
- `list` - A list of strings, the user must pick one of the options in the list.
- `None` - No autocomplete, the user can type anything.

---

##### Advanced and Custom Options

Source can also be a callable that returns a list of strings, see here for an example:

```python
def get_some_form_of_completions(
    action: Action, param: Optional[ActionParam] = None, value: str = ""
) -> Iterable[str]:
    for i in range(20):
        yield f"option_{i}"
```

Yield can be used, or you can return a list directly.

```python
def get_some_form_of_completions(
    action: Action, param: Optional[ActionParam] = None, value: str = ""
) -> List[str]:
    return [f"option_{i}" for i in range(20)]
```

To use this function as a source, you would do the following:

```python
class AddCommand(PluginCommand):
    """
    Add two numbers.
    """

    description = "Add two integers."
    params = {
        "x": {
            "cast": int,
            "source": get_some_form_of_completions,
            "description": "First number.",
            "help": "This is the first number to add.",
        },
        "y": {
            "cast": int,
            "source": get_some_form_of_completions,
            "description": "Second number.",
            "help": "This is the second number to add.",
        },
    }

    def execute(self, x: int, y: int):
        return self.plugin.add_numbers(x, y)
```

Lastly, the fun and custom type `Empty` can be used. This is a special type that is custom to the fork of ActionCompleter used in Mercury OCIP. This type indicates that any value can be provided, but an empty help box will be shown. This is useful for free text inputs where you want to indicate that the user can type anything, while retaining a help message. (But can also show a "source" of no options but with help text)

```python
class AddCommand(PluginCommand):
    """
    Add two numbers.
    """

    description = "Add two integers."
    params = {
        "x": {
            "cast": int,
            "source": Empty,
            "description": "First number.",
            "help": "This is the first number to add.",
        },
        "y": {
            "cast": int,
            "source": Empty,
            "description": "Second number.",
            "help": "This is the second number to add.",
        },
    }

    def execute(self, x: int, y: int):
        return self.plugin.add_numbers(x, y)
```

This looks something like this in the CLI:

```
plugin ExamplePlugin add ____
                        (First Number | This is the first number to add.)
```

or if you specify no description:

```
plugin ExamplePlugin add ____
                        (             | This is the first number to add.)
```

!!! tip "Empty vs None"
    Empty is different to None in that None provides no autocomplete and no help text, while Empty provides no autocomplete but does provide help text.

---

#### Executing Logic from Commands

Within the `execute` method of your command class, you can call methods from your main plugin class using `self.plugin`. This allows you to separate the command handling logic from the business logic of your plugin.

It is important to note that within the command class, you can access the parent plugin instance via \`self.plugin\`. This allows you to call any methods or access any attributes defined in your main plugin class.

---

#### Accessing the Client

Both the \`BasePlugin\` and \`PluginCommand\` classes provide access to the main agent client instance. This is crucial for plugins that need to interact with the OCI interface or other agent services.

!!! abstract "Client Access"
    - In BasePlugin: The client is available as self.client.
    - In PluginCommand: The client is available as self.plugin.client.

This allows you to execute OCI commands directly from your plugin logic. For example:

```python
from mercury_ocip.commands.commands import SystemSoftwareVersionGetRequest

class GetVersionCommand(PluginCommand):
    """
    Get the system software version.
    """
    description = "Get the system software version."
    params = {}

    def execute(self):
        response = self.plugin.client.command(SystemSoftwareVersionGetRequest())
        print(f"System Version: {response.version}")
```

This `self.plugin.client` is the same instance used by the main agent, so it shares the same session and connection.

---

### Registering Commands

Finally, to make these commands available to the agent, you need to register them in your plugin class by overriding the `get_commands` method:

```python
class ExamplePlugin(BasePlugin):
    """
    Example plugin demonstration.
    """

    name = "Example Plugin"
    version = "1.0.0"
    description = "Demonstrates the new plugin command structure."

    def get_commands(self) -> Dict[str, Type[PluginCommand]]:
        return {
            "greet": GreetCommand,
            "add": AddCommand,
            "echo": EchoCommand,
        }
```

Each command is registered with a unique name that will be used to invoke the command from the CLI.

---

### Final Example

Bringing it all together, here is how the complete plugin code might look:

```python
from mercury_ocip.plugins.base_plugin import BasePlugin, PluginCommand
from mercury_ocip.commands.commands import SystemSoftwareVersionGetRequest
from action_completer.types import Empty
from typing import Dict, Type


class GreetCommand(PluginCommand):
    """
    Greet someone by name.
    """

    description = "Print a greeting for a user."
    params = {
        "name": {
            "cast": str,
            "source": None,  # Specify the source explicitly
            "description": "Name of the user to greet.",
            "help": "The name of the person you want to greet",  # Add help text
        }
    }

    def execute(self, name: str):
        return self.plugin.greet_user(name)


class EchoCommand(PluginCommand):
    """
    Echo a string a certain number of times.
    """

    description = "Echo a string a certain number of times."
    params = {
        "string": {
            "cast": str,  # Type to cast the parameter to
            "source": None,  # Where the autocomplete gets its data from
            "description": "String to echo.",  # Left hand side description
            "help": "The string you want to echo",  # right hand side help text
        },
        "etimes": {
            "cast": int,
            "source": [
                "1",
                "2",
                "3",
                "5",
                "10",
                "20",
                "50",
            ],
            "description": "Number of times to echo.",
            "help": "How many times to echo the string",
        },
    }

    def execute(self, string: str, etimes: int):
        return self.plugin.echo_string(string, etimes)


class AddCommand(PluginCommand):
    """
    Add two numbers.
    """

    description = "Add two integers."
    params = {
        "x": {
            "cast": int,
            "source": Empty,
            "description": "First number.",
            "help": "This is the first number to add.",
        },
        "y": {
            "cast": int,
            "source": Empty,
            "description": "Second number.",
            "help": "This is the second number to add.",
        },
    }

    def execute(self, x: int, y: int):
        return self.plugin.add_numbers(x, y)


class GetVersionCommand(PluginCommand):
    """
    Get the system software version.
    """
    description = "Get the system software version."
    params = {}

    def execute(self):
        response = self.plugin.client.command(SystemSoftwareVersionGetRequest())
        print(f"System Version: {response.version}")


class ExamplePlugin(BasePlugin):
    """
    Example plugin demonstrating proper logic separation.
    """

    name = "Example Plugin"
    version = "1.0.0"
    description = "Demonstrates the new plugin command structure."

    def get_commands(self) -> Dict[str, Type[PluginCommand]]:
        return {
            "greet": GreetCommand,
            "add": AddCommand,
            "echo": EchoCommand,
            "version": GetVersionCommand,
        }

    # --- Business Logic Layer ---

    def greet_user(self, name: str) -> None:
        print(f"Hello, {name}! Welcome to Mercury OCIP.")

    def add_numbers(self, x: int, y: int) -> None:
        result = x + y
        print(f"{x} + {y} = {result}")

    def echo_string(self, string: str, etimes: int) -> None:
        for _ in range(etimes):
            print(string)
```

In this final example, we have defined four command classes: `GreetCommand`, `EchoCommand`, `AddCommand`, and `GetVersionCommand`. Each command class is responsible for handling its own parameters and executing the corresponding logic by calling methods from the `ExamplePlugin` class or interacting with the client directly.

Quickly looking at the pyproject.toml again, it would look like this:

```toml
[project.entry-points."mercury_ocip.plugins"]
ExamplePlugin = "plugin.main:ExamplePlugin"
```

And in the CLI it would show as:

```title="plugins list"
Available Plugins:
- ExamplePlugin
```

Alongside any exposed command autocompleting after:

```
plugin ExamplePlugin ...
```

And that is it! You have successfully created a plugin for the Mercury OCIP agent that integrates with both the main library and the CLI, complete with properly defined commands and business logic separation.

For reference, you can check out the [example plugin repository](https://github.com/mercury-ocip/example-plugin)