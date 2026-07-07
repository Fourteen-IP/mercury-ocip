"""Execute a command line against the command tree."""

import difflib
from typing import Any, Iterable

from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.shortcuts import prompt as pt_prompt

from mercury_ocip.cli.core.completer import _resolve_candidates
from mercury_ocip.cli.core.errors import (
    BadParamError,
    CommandAborted,
    IncompleteCommandError,
    MissingParamError,
    TooManyArgsError,
    UnknownCommandError,
)
from mercury_ocip.cli.core.tokenizer import tokenize
from mercury_ocip.cli.core.tree import (
    Command,
    CommandRegistry,
    CompletionContext,
    Group,
    Param,
)


def dispatch(registry: CommandRegistry, line: str, interactive: bool = True) -> Any:
    """Tokenize, resolve and execute a command line.

    Args:
        registry: The command tree.
        line: The raw input line.
        interactive: If True, prompt for missing required params instead of
            raising MissingParamError.
    """
    tokens = tokenize(line)
    if not tokens:
        return None

    node, remaining = registry.resolve(tokens)

    if isinstance(node, Group):
        matched_path = tokens[: len(tokens) - len(remaining)]
        if remaining:
            raise UnknownCommandError(
                _unknown_message(node, matched_path, remaining[0]),
                suggestions=_suggest(node, remaining[0]),
            )
        raise IncompleteCommandError(
            f"'{' '.join(matched_path) or 'mercury_cli'}' needs a subcommand.",
            subcommands=sorted(node.children),
        )

    kwargs = _bind_params(node, remaining, interactive)
    return node.func(**kwargs)


def _bind_params(
    command: Command, args: list[str], interactive: bool
) -> dict[str, Any]:
    params = command.params

    if not params:
        if args:
            raise TooManyArgsError(
                f"'{command.name}' takes no arguments, got: {' '.join(args)}"
            )
        return {}

    has_greedy = params[-1].greedy
    if not has_greedy and len(args) > len(params):
        expected = ", ".join(p.name for p in params)
        raise TooManyArgsError(
            f"'{command.name}' takes {len(params)} argument(s) ({expected}), "
            f"got {len(args)}."
        )

    kwargs: dict[str, Any] = {}
    raw_values: dict[str, str] = {}

    for i, param in enumerate(params):
        if param.greedy:
            raw = " ".join(args[i:])
            if not raw and param.required:
                raw = _prompt_value(param, raw_values, interactive)
            elif not raw:
                kwargs[param.name] = param.default
                continue
        elif i < len(args):
            raw = args[i]
        elif param.required:
            raw = _prompt_value(param, raw_values, interactive)
        else:
            kwargs[param.name] = param.default
            continue

        raw_values[param.name] = raw
        try:
            kwargs[param.name] = param.cast(raw)
        except (ValueError, TypeError) as e:
            raise BadParamError(
                f"Invalid value for {param.name}: {raw!r} ({e})"
            )

    return kwargs


def _prompt_value(
    param: Param, earlier_values: dict[str, str], interactive: bool
) -> str:
    if not interactive:
        raise MissingParamError(
            f"Missing required argument: {param.name}"
            + (f" ({param.meta})" if param.meta else "")
        )

    label = param.meta or param.name.replace("_", " ")
    completer = _SingleParamCompleter(param, earlier_values)

    while True:
        try:
            raw = pt_prompt(
                f"  {label}: ",
                completer=completer,
                complete_while_typing=True,
            ).strip()
        except (KeyboardInterrupt, EOFError):
            raise CommandAborted("Cancelled.")
        if raw:
            return raw


class _SingleParamCompleter(Completer):
    """Completes one param's values in a standalone prompt."""

    def __init__(self, param: Param, earlier_values: dict[str, str]):
        self.param = param
        self.earlier_values = earlier_values

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        if isinstance(self.param.source, Completer):
            yield from self.param.source.get_completions(document, complete_event)
            return

        partial = document.text_before_cursor
        ctx = CompletionContext(values=dict(self.earlier_values), partial=partial)
        for candidate in _resolve_candidates(self.param, ctx):
            if candidate.startswith(partial):
                yield Completion(
                    candidate,
                    start_position=-len(partial),
                    display_meta=self.param.meta,
                )


def _suggest(group: Group, attempted: str) -> list[str]:
    return difflib.get_close_matches(attempted, list(group.children), n=3, cutoff=0.5)


def _unknown_message(group: Group, path: list[str], attempted: str) -> str:
    where = f" under '{' '.join(path)}'" if path else ""
    message = f"Unknown command '{attempted}'{where}."
    matches = _suggest(group, attempted)
    if matches:
        message += f" Did you mean: {', '.join(matches)}?"
    return message
