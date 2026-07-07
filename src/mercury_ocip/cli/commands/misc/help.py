from rich.text import Text
from rich.tree import Tree

from mercury_ocip.cli.core import cli, CompletionContext
from mercury_ocip.cli.core.tree import Command, Group
from mercury_ocip.cli.globals import MERCURY_CLI

console = MERCURY_CLI.console()


def _help_path_completions(ctx: CompletionContext):
    """Complete the next segment of a command path, e.g. 'help bulk cre<tab>'."""
    node, remaining = cli.resolve(ctx.extra_tokens)
    if remaining or isinstance(node, Command):
        return []
    return sorted(node.children)


def _print_command_help(command: Command, path: str) -> None:
    console.print(f"\n[bold cyan]{path}[/bold cyan]")
    console.print(f"  {command.meta or 'No description'}")

    if command.params:
        console.print("\n[bold]Parameters:[/bold]")
        for param in command.params:
            optional = "" if param.required else " (optional)"
            console.print(
                f"  [magenta]<{param.name}>[/magenta]{optional} - "
                f"{param.meta or 'No description'}"
            )

    usage = " ".join([path] + [f"<{p.name}>" for p in command.params])
    console.print(f"\n[bold]Usage:[/bold] {usage}")


def _print_group_help(group: Group, path: str) -> None:
    console.print(f"\n[bold cyan]{path}[/bold cyan]")
    console.print(f"  {group.meta or 'No description'}")

    console.print("\n[bold]Subcommands:[/bold]")
    for name in sorted(group.children):
        child = group.children[name]
        console.print(f"  [yellow]{name}[/yellow] - {child.meta or ''}")


def _print_all_commands() -> None:
    tree = Tree("[bold cyan]commands[/bold cyan]")
    _add_children(cli.root, tree)

    console.print()
    console.print("[bold]Mercury CLI - Available Commands[/bold]")
    console.print(tree)
    console.print("\n[dim]Use [cyan]help <command>[/cyan] for details[/dim]")


def _add_children(group: Group, tree: Tree) -> None:
    for name in sorted(group.children):
        child = group.children[name]
        label = Text()
        label.append(name, style="bold yellow")
        if child.meta:
            label.append(f" - {child.meta}", style="dim")
        branch = tree.add(label)

        if isinstance(child, Group):
            _add_children(child, branch)


@cli.command("help", meta="Gives a list of all commands")
@cli.param(
    "command_path",
    source=_help_path_completions,
    meta="Command path",
    required=False,
    default="",
    greedy=True,
)
def _help(command_path: str = ""):
    """Show help for all commands or a specific command path."""
    parts = command_path.split()

    if not parts:
        _print_all_commands()
        return

    node, remaining = cli.resolve(parts)
    if remaining:
        console.print(f"[error]Unknown command:[/error] {command_path}")
        return

    path = " ".join(parts)
    if isinstance(node, Command):
        _print_command_help(node, path)
    else:
        _print_group_help(node, path)
