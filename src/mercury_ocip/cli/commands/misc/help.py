from mercury_ocip.cli.globals import MERCURY_CLI
from typing import Optional, Iterable
from rich.tree import Tree
from rich.text import Text
from action_completer import Action, ActionParam
from action_completer.utils import get_fragments

completer = MERCURY_CLI.completer()
console = MERCURY_CLI.console()


def _walk_tree(node, path: list[str]):
    """Walk the command tree following the given path. Returns (node, remaining_path)."""
    current = node
    for i, part in enumerate(path):
        if hasattr(current, "children") and isinstance(current.children, dict):
            if part in current.children and part not in "params":
                current = current.children[part]
            else:
                return current, path[i:]
        else:
            return current, path[i:]
    return current, []


def _get_completions_for_node(node) -> list[str]:
    """Get valid command names from a node's children."""
    if hasattr(node, "children") and isinstance(node.children, dict):
        return [
            name
            for name, child in node.children.items()
            if name not in "params" and getattr(child, "display_meta", None)
        ]
    return []


def _help_completer(
    action: Action, param: Optional[ActionParam] = None, value: str = ""
) -> Iterable[str]:
    """Provide completions for help command based on current input."""
    buffer_text = MERCURY_CLI.session().default_buffer.document.text
    fragments = get_fragments(buffer_text)

    # fragments[0] is "help", rest is the command path
    command_path = fragments[1:] if len(fragments) > 1 else []

    # Walk to the current node
    node, remaining = _walk_tree(completer.root, command_path)

    # If we're mid-word, filter completions
    if remaining:
        partial = remaining[-1] if remaining else ""
        completions = _get_completions_for_node(node)
        return [c for c in completions if c.startswith(partial)]

    return _get_completions_for_node(node)


def _print_node_help(node, path: str):
    """Print help for a single node."""
    description = getattr(node, "display_meta", None) or "No description"
    console.print(f"\n[bold cyan]{path}[/bold cyan]")
    console.print(f"  {description}")

    # Show params if it's an executable action
    if (
        hasattr(node, "params")
        and isinstance(node.params, (list, tuple))
        and node.params
    ):
        console.print("\n[bold]Parameters:[/bold]")
        for p in node.params:
            name = getattr(p, "display", None) or "arg"
            desc = getattr(p, "display_meta", None) or "No description"
            console.print(f"  [magenta]<{name}>[/magenta] - {desc}")

    # Show subcommands if it has children
    children = _get_completions_for_node(node)
    if children:
        console.print("\n[bold]Subcommands:[/bold]")
        for name in sorted(children):
            child = node.children[name]
            child_desc = getattr(child, "display_meta", None) or ""
            console.print(f"  [yellow]{name}[/yellow] - {child_desc}")


def _print_all_commands(node, prefix: str = "", tree: Tree = None, root: bool = True):
    """Recursively print all commands as a tree."""
    if root:
        tree = Tree("[bold cyan]commands[/bold cyan]")

    children = _get_completions_for_node(node)
    for name in sorted(children):
        child = node.children[name]
        desc = getattr(child, "display_meta", None) or ""
        label = Text()
        label.append(name, style="bold yellow")
        if desc:
            label.append(f" - {desc}", style="dim")
        branch = tree.add(label)

        # Recurse
        grandchildren = _get_completions_for_node(child)
        if grandchildren:
            _print_all_commands(child, f"{prefix}{name} ", branch, root=False)

    if root:
        console.print()
        console.print("[bold]Mercury CLI - Available Commands[/bold]")
        console.print(tree)
        console.print("\n[dim]Use [cyan]help <command>[/cyan] for details[/dim]")


@completer.action("help", display_meta="Gives a list of all commands")
@completer.param(_help_completer, cast=str, display_meta="Command path")
def _help(command_path: Optional[str] = None):
    """Show help for commands."""

    buffer_text = MERCURY_CLI.session().default_buffer.document.text
    fragments = get_fragments(buffer_text)

    # fragments[0] is "help", rest is the command path
    path_parts = fragments[1:] if len(fragments) > 1 else []

    if path_parts:
        node, remaining = _walk_tree(completer.root, path_parts)

        if remaining:
            console.print(f"[red]Unknown command:[/red] {' '.join(path_parts)}")
            return

        _print_node_help(node, " ".join(path_parts))
    else:
        _print_all_commands(completer.root)
