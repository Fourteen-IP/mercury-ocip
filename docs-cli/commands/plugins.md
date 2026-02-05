# Plugins

The plugin command manages and executes plugin extensions.

!!! note "Mercury OCIP Docs"
    The guide to plugin architecture and development can be found here:

    *[:octicons-link-16: Agent Documentation](https://mercury-docs.14ip.net/mercury-ocip/agent/plugins/)*

## Usage

```
plugin <action>
plugin <plugin_name> <command> [args...]
```

---

## Actions

### list

Lists all available plugins installed in the system.

**Example:**
```bash title="List Available Plugins"
plugin list
```
---
## Plugin Commands

Each plugin can define its own set of commands. Available commands depend on which plugins are installed.

**General format:**
```
plugin <plugin_name> <command> [args...]
```

!!! note "Plugin Discovery"
    Plugins are automatically discovered through entry points. The CLI loads plugin modules and exposes their commands dynamically.

---
## Output

Success: Plugin command executes and returns its result.
Failure: Shows error during plugin instantiation or command execution with traceback.

!!! warning "Plugin Errors"
    If a plugin fails to load, it's silently skipped during discovery. Only plugins that successfully instantiate are made available.