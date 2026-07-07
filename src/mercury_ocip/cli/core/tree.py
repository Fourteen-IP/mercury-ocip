"""Command tree: the single source of truth for CLI commands.

Commands are registered with a path string ("bulk create hunt_group") and a
list of Params. The same tree drives completion (completer.py), execution
(dispatcher.py) and the help command.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Optional, Union

from prompt_toolkit.completion import Completer

from mercury_ocip.cli.core.errors import CLIError


@dataclass
class CompletionContext:
    """Passed to callable completion sources.

    Attributes:
        values: Raw string values of the command's earlier params, keyed by
            param name (e.g. group_id completions can read
            ctx.values["service_provider_id"]).
        partial: The token currently being typed, possibly empty.
        extra_tokens: For greedy params only — completed tokens already
            consumed by this param.
    """

    values: dict[str, str] = field(default_factory=dict)
    partial: str = ""
    extra_tokens: list[str] = field(default_factory=list)


# A completion source is one of:
#   None                      -> free text, no completions
#   list/tuple/set of str     -> static candidates
#   prompt_toolkit Completer  -> delegated (e.g. PathCompleter)
#   callable(ctx) -> iterable -> dynamic candidates
ParamSource = Union[None, Iterable[str], Completer, Callable[[CompletionContext], Iterable[str]]]


@dataclass
class Param:
    name: str
    source: ParamSource = None
    meta: str = ""
    cast: Callable[[str], Any] = str
    required: bool = True
    default: Any = None
    greedy: bool = False  # consumes all remaining tokens, joined by spaces


@dataclass
class Command:
    name: str
    func: Callable[..., Any]
    meta: str = ""
    params: list[Param] = field(default_factory=list)


@dataclass
class Group:
    name: str
    meta: str = ""
    children: dict[str, Union["Group", Command]] = field(default_factory=dict)


class CommandRegistry:
    """Registry and decorator API for CLI commands.

    Usage:
        @cli.command("bulk create hunt_group", meta="Bulk create hunt groups")
        @cli.param("file_path", source=PathCompleter(), meta="Path to CSV")
        def _bulk_hunt_group(file_path: str): ...

        cli.describe("bulk create", "Bulk create operations")
    """

    def __init__(self) -> None:
        self.root = Group(name="")

    # -- Registration -------------------------------------------------- #

    def command(self, path: str, meta: str = "") -> Callable:
        def decorator(func: Callable) -> Callable:
            params = list(reversed(getattr(func, "__cli_params__", [])))
            self.register(path, func, meta=meta, params=params)
            return func

        return decorator

    def param(
        self,
        name: str,
        source: ParamSource = None,
        meta: str = "",
        cast: Callable[[str], Any] = str,
        required: bool = True,
        default: Any = None,
        greedy: bool = False,
    ) -> Callable:
        def decorator(func: Callable) -> Callable:
            if not hasattr(func, "__cli_params__"):
                func.__cli_params__ = []
            # Stacked decorators run bottom-up; command() reverses the list
            # so params end up in declaration order.
            func.__cli_params__.append(
                Param(
                    name=name,
                    source=source,
                    meta=meta,
                    cast=cast,
                    required=required,
                    default=default,
                    greedy=greedy,
                )
            )
            return func

        return decorator

    def register(
        self,
        path: str,
        func: Callable,
        meta: str = "",
        params: Optional[list[Param]] = None,
    ) -> Command:
        """Register a command at a path (non-decorator form, used by plugins)."""
        parts = path.split()
        if not parts:
            raise CLIError("Command path cannot be empty")

        params = params or []
        greedy = [p for p in params if p.greedy]
        if greedy and (len(greedy) > 1 or params[-1] is not greedy[0]):
            raise CLIError(
                f"Command '{path}': only the last param may be greedy"
            )

        group = self._ensure_groups(parts[:-1])
        name = parts[-1]
        existing = group.children.get(name)
        if isinstance(existing, Group):
            raise CLIError(f"Cannot register command '{path}': it is a group")

        command = Command(name=name, func=func, meta=meta, params=params)
        group.children[name] = command
        return command

    def describe(self, path: str, meta: str) -> None:
        """Set the description on a group, creating it if needed."""
        group = self._ensure_groups(path.split())
        group.meta = meta

    def _ensure_groups(self, parts: list[str]) -> Group:
        node = self.root
        for part in parts:
            child = node.children.get(part)
            if child is None:
                child = Group(name=part)
                node.children[part] = child
            elif isinstance(child, Command):
                raise CLIError(
                    f"Cannot create group '{part}': a command with that name exists"
                )
            node = child
        return node

    # -- Lookup -------------------------------------------------------- #

    def resolve(self, tokens: list[str]) -> tuple[Union[Group, Command], list[str]]:
        """Walk the tree as far as tokens match; return (node, remaining tokens)."""
        node: Union[Group, Command] = self.root
        i = 0
        while i < len(tokens) and isinstance(node, Group):
            child = node.children.get(tokens[i])
            if child is None:
                break
            node = child
            i += 1
        return node, tokens[i:]
