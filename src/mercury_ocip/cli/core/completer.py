"""prompt_toolkit completer driven by the command tree."""

from typing import Iterable, Optional

from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document

from mercury_ocip.cli.core.tokenizer import quote_arg, tokenize_incomplete
from mercury_ocip.cli.core.tree import (
    Command,
    CommandRegistry,
    CompletionContext,
    Group,
    Param,
)
from mercury_ocip.cli.core.ui import quit_hint_active


class MercuryCompleter(Completer):
    def __init__(self, registry: CommandRegistry):
        self.registry = registry

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        text = document.text_before_cursor
        line = tokenize_incomplete(text)

        if line.in_token:
            partial = line.tokens[-1]
            consumed = line.tokens[:-1]
            # Length of the raw text being replaced (includes any opening quote)
            replace_len = len(text) - line.last_token_start
        else:
            partial = ""
            consumed = line.tokens
            replace_len = 0

        node, remaining = self.registry.resolve(consumed)

        if isinstance(node, Group):
            if remaining:  # consumed tokens that match nothing
                return
            yield from self._complete_group(node, partial, replace_len)
            return

        yield from self._complete_param(node, remaining, partial, replace_len, document)

    def _complete_group(
        self, group: Group, partial: str, replace_len: int
    ) -> Iterable[Completion]:
        for name, child in sorted(group.children.items()):
            if name.startswith(partial):
                yield Completion(
                    name,
                    start_position=-replace_len,
                    display_meta=child.meta,
                )

    def _complete_param(
        self,
        command: Command,
        arg_tokens: list[str],
        partial: str,
        replace_len: int,
        document: Document,
    ) -> Iterable[Completion]:
        param, ctx = _current_param(command, arg_tokens, partial)
        if param is None:
            return

        if param.source is None:
            # Free-text param: no candidates. (An empty-text "hint" completion
            # doesn't work — prompt_toolkit drops a lone completion that
            # inserts nothing. The bottom toolbar shows the param hint instead.)
            return

        if isinstance(param.source, Completer):
            # Delegate (e.g. PathCompleter) with a sub-document containing
            # just the partial token; segment-relative positions still apply.
            sub_doc = Document(partial, cursor_position=len(partial))
            yield from param.source.get_completions(
                sub_doc, CompleteEvent(completion_requested=True)
            )
            return

        candidates = _resolve_candidates(param, ctx)
        for candidate in candidates:
            if candidate.startswith(partial):
                yield Completion(
                    quote_arg(candidate),
                    start_position=-replace_len,
                    display=candidate,
                    display_meta=param.meta,
                )


def _current_param(
    command: Command, arg_tokens: list[str], partial: str
) -> tuple[Optional[Param], CompletionContext]:
    """Work out which param the cursor is on and build its context."""
    params = command.params
    if not params:
        return None, CompletionContext()

    index = len(arg_tokens)
    if index >= len(params):
        last = params[-1]
        if not last.greedy:
            return None, CompletionContext()
        values = {p.name: arg_tokens[i] for i, p in enumerate(params[:-1])}
        return last, CompletionContext(
            values=values,
            partial=partial,
            extra_tokens=arg_tokens[len(params) - 1 :],
        )

    values = {p.name: arg_tokens[i] for i, p in enumerate(params[:index])}
    return params[index], CompletionContext(values=values, partial=partial)


def param_hint_fragments(registry: CommandRegistry, text: str):
    """Build bottom-toolbar fragments showing the resolved command's signature,
    with the param currently being typed highlighted and described.

    Returns None when the input doesn't resolve to a command yet (the
    completion menu covers group/command names).
    """
    line = tokenize_incomplete(text)
    consumed = line.tokens[:-1] if line.in_token else line.tokens

    node, remaining = registry.resolve(consumed)
    if not isinstance(node, Command):
        return None

    current = len(remaining)  # index of the param being typed / expected next
    fragments = [("", " "), ("bold", node.name)]

    for i, param in enumerate(node.params):
        label = f"<{param.name}>"
        is_current = i == current or (param.greedy and current >= i)
        if is_current:
            fragments.append(("", "  "))
            fragments.append(("bold underline", label))
            if param.meta:
                fragments.append(("", f" — {param.meta}"))
        else:
            fragments.append(("", f"  {label}"))

    return fragments


def make_bottom_toolbar(registry: CommandRegistry):
    """Toolbar callable for PromptSession showing live parameter hints."""

    def toolbar():
        from prompt_toolkit.application import get_app

        text = get_app().current_buffer.document.text_before_cursor

        # An armed "press Ctrl+C again to quit" takes over the (otherwise
        # idle) toolbar on an empty line; typing anything falls straight
        # through to the normal hints below instead of fighting for space.
        if quit_hint_active() and not text:
            return [("class:muted", " Press Ctrl+C again to quit ")]

        fragments = param_hint_fragments(registry, text)
        if fragments is None:
            fragments = [("", " Tab: complete · 'help' lists all commands")]
        return fragments

    return toolbar


def _resolve_candidates(param: Param, ctx: CompletionContext) -> list[str]:
    source = param.source
    if source is None:
        return []
    if callable(source):
        try:
            return [str(c) for c in source(ctx)]
        except Exception:
            return []  # never let a completion source break the prompt
    try:
        return [str(c) for c in source]
    except TypeError:
        return []
