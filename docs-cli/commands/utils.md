# Utilities

Utility commands for CLI management and system information.

## Usage

```asciinema-player
{
    "file": "/assets/asciinema/utils.cast",
    "title": "Utilities Showcase",
    "mkap_theme": "none",
    "theme": "dracula",
    "fit": "width",
    "cols": 120,
    "rows": 24,
    "autoplay": true
}
```


```
<command> [args...]
```

---

## Commands

### help

Display available commands or detailed help for a specific command.

**Usage:**
```
help [command_name]
```

**Example:**
```bash title="List All Commands"
help
```

```bash title="Get Help for Specific Command"
help bulk
```

---

### sysver

Display the current system software version from the connected BroadWorks server.

**Usage:**
```
sysver
```

**Output:**
```
Current system version: <version>
```
---
### exit

Gracefully disconnect from the server and exit the CLI.

**Usage:**
```
exit
```
---
### clear

Clear the terminal screen.

**Usage:**
```
clear
```