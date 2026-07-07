"""Unit tests for the cli/core command tree, tokenizer, completer and dispatcher."""

import pytest
from prompt_toolkit.completion import CompleteEvent
from prompt_toolkit.document import Document

from mercury_ocip.cli.core.completer import MercuryCompleter, param_hint_fragments
from mercury_ocip.cli.core.dispatcher import dispatch
from mercury_ocip.cli.core.errors import (
    CLIError,
    CommandSyntaxError,
    IncompleteCommandError,
    MissingParamError,
    TooManyArgsError,
    UnknownCommandError,
)
from mercury_ocip.cli.core.tokenizer import quote_arg, tokenize, tokenize_incomplete
from mercury_ocip.cli.core.tree import CommandRegistry


# -- Tokenizer ---------------------------------------------------------- #


class TestTokenize:
    def test_simple_split(self):
        assert tokenize("bulk create user file.csv") == [
            "bulk",
            "create",
            "user",
            "file.csv",
        ]

    def test_double_quotes_group_words(self):
        assert tokenize('bulk create user "my file.csv"') == [
            "bulk",
            "create",
            "user",
            "my file.csv",
        ]

    def test_single_quotes_group_words(self):
        assert tokenize("set_address '10 Downing St' London") == [
            "set_address",
            "10 Downing St",
            "London",
        ]

    def test_backslashes_are_literal(self):
        assert tokenize(r"bulk create user C:\temp\file.csv") == [
            "bulk",
            "create",
            "user",
            r"C:\temp\file.csv",
        ]

    def test_quote_opening_mid_token(self):
        assert tokenize('name="a b"') == ["name=a b"]

    def test_empty_quotes_produce_empty_token(self):
        assert tokenize('cmd ""') == ["cmd", ""]

    def test_multiple_spaces_collapse(self):
        assert tokenize("a   b\t c") == ["a", "b", "c"]

    def test_empty_line(self):
        assert tokenize("") == []
        assert tokenize("   ") == []

    def test_unclosed_quote_raises(self):
        with pytest.raises(CommandSyntaxError):
            tokenize('bulk create "unclosed')

    def test_other_quote_char_inside_quotes(self):
        assert tokenize("say \"it's fine\"") == ["say", "it's fine"]


class TestTokenizeIncomplete:
    def test_mid_token(self):
        result = tokenize_incomplete("bulk cre")
        assert result.tokens == ["bulk", "cre"]
        assert result.in_token
        assert result.last_token_start == 5

    def test_after_space_starts_new_token(self):
        result = tokenize_incomplete("bulk ")
        assert result.tokens == ["bulk"]
        assert not result.in_token

    def test_unclosed_quote_does_not_raise(self):
        result = tokenize_incomplete('user "my fi')
        assert result.tokens == ["user", "my fi"]
        assert result.open_quote == '"'
        assert result.last_token_start == 5  # includes the opening quote

    def test_empty(self):
        result = tokenize_incomplete("")
        assert result.tokens == []
        assert not result.in_token


class TestQuoteArg:
    def test_plain_value_unquoted(self):
        assert quote_arg("file.csv") == "file.csv"

    def test_value_with_space_quoted(self):
        assert quote_arg("my file.csv") == '"my file.csv"'

    def test_value_containing_double_quote_uses_single(self):
        assert quote_arg('say "hi" now') == "'say \"hi\" now'"

    def test_empty_value_quoted(self):
        assert quote_arg("") == '""'


# -- Tree / registration ------------------------------------------------- #


def make_registry():
    reg = CommandRegistry()

    @reg.command("bulk create hunt_group", meta="Create hunt groups")
    @reg.param("file_path", meta="Path to CSV")
    def _hunt_group(file_path: str):
        return ("hunt_group", file_path)

    @reg.command("automations group_audit", meta="Audit a group")
    @reg.param("service_provider_id", source=["SP_One", "SP_Two"], meta="SP ID")
    @reg.param("group_id", source=_group_ids, meta="Group ID")
    def _group_audit(service_provider_id: str, group_id: str):
        return ("audit", service_provider_id, group_id)

    @reg.command("count", meta="Casts to int")
    @reg.param("n", cast=int)
    def _count(n: int):
        return n * 2

    @reg.command("help", meta="Help")
    @reg.param("command_path", required=False, default="", greedy=True)
    def _help(command_path: str):
        return command_path

    reg.describe("bulk create", "Bulk create operations")
    return reg


def _group_ids(ctx):
    if ctx.values.get("service_provider_id") == "SP_One":
        return ["GroupA", "GroupB"]
    return []


class TestRegistry:
    def test_params_in_declaration_order(self):
        reg = make_registry()
        node, remaining = reg.resolve(["automations", "group_audit"])
        assert remaining == []
        assert [p.name for p in node.params] == ["service_provider_id", "group_id"]

    def test_describe_sets_group_meta(self):
        reg = make_registry()
        node, _ = reg.resolve(["bulk", "create"])
        assert node.meta == "Bulk create operations"

    def test_resolve_partial_path_returns_group(self):
        reg = make_registry()
        node, remaining = reg.resolve(["bulk", "nope"])
        assert node.name == "bulk"
        assert remaining == ["nope"]

    def test_group_command_name_conflict_raises(self):
        reg = make_registry()
        with pytest.raises(CLIError):
            reg.describe("count sub", "count is already a command")

    def test_greedy_must_be_last(self):
        reg = CommandRegistry()
        with pytest.raises(CLIError):

            @reg.command("bad")
            @reg.param("rest", greedy=True)
            @reg.param("after")
            def _bad(rest, after):
                pass


# -- Dispatcher ----------------------------------------------------------- #


class TestDispatch:
    def test_executes_with_args(self):
        reg = make_registry()
        result = dispatch(reg, "bulk create hunt_group groups.csv")
        assert result == ("hunt_group", "groups.csv")

    def test_quoted_arg_with_spaces(self):
        reg = make_registry()
        result = dispatch(reg, 'bulk create hunt_group "my groups.csv"')
        assert result == ("hunt_group", "my groups.csv")

    def test_cast_applied(self):
        reg = make_registry()
        assert dispatch(reg, "count 21") == 42

    def test_bad_cast_raises(self):
        reg = make_registry()
        from mercury_ocip.cli.core.errors import BadParamError

        with pytest.raises(BadParamError):
            dispatch(reg, "count nope")

    def test_unknown_command_suggests(self):
        reg = make_registry()
        with pytest.raises(UnknownCommandError) as exc:
            dispatch(reg, "bulk create hunt_gruop x.csv")
        assert "hunt_group" in exc.value.suggestions

    def test_group_without_subcommand(self):
        reg = make_registry()
        with pytest.raises(IncompleteCommandError) as exc:
            dispatch(reg, "bulk create")
        assert "hunt_group" in exc.value.subcommands

    def test_too_many_args(self):
        reg = make_registry()
        with pytest.raises(TooManyArgsError):
            dispatch(reg, "count 1 2")

    def test_missing_param_non_interactive(self):
        reg = make_registry()
        with pytest.raises(MissingParamError):
            dispatch(reg, "bulk create hunt_group", interactive=False)

    def test_missing_param_prompts_interactively(self, monkeypatch):
        reg = make_registry()
        prompts = []

        def fake_prompt(message, **kwargs):
            prompts.append(message)
            return "GroupA"

        monkeypatch.setattr(
            "mercury_ocip.cli.core.dispatcher.pt_prompt", fake_prompt
        )
        result = dispatch(reg, "automations group_audit SP_One")
        assert result == ("audit", "SP_One", "GroupA")
        assert len(prompts) == 1
        assert "Group ID" in prompts[0]

    def test_greedy_param_joins_tokens(self):
        reg = make_registry()
        assert dispatch(reg, "help bulk create hunt_group") == "bulk create hunt_group"

    def test_greedy_param_optional_default(self):
        reg = make_registry()
        assert dispatch(reg, "help") == ""

    def test_empty_line_is_noop(self):
        reg = make_registry()
        assert dispatch(reg, "   ") is None


# -- Completer ------------------------------------------------------------ #


def completions_for(reg, text):
    completer = MercuryCompleter(reg)
    doc = Document(text, cursor_position=len(text))
    return list(completer.get_completions(doc, CompleteEvent()))


class TestCompleter:
    def test_root_commands(self):
        reg = make_registry()
        names = [c.text for c in completions_for(reg, "")]
        assert "bulk" in names and "automations" in names

    def test_partial_group_name(self):
        reg = make_registry()
        names = [c.text for c in completions_for(reg, "bu")]
        assert names == ["bulk"]
        assert completions_for(reg, "bu")[0].start_position == -2

    def test_subgroup_children(self):
        reg = make_registry()
        names = [c.text for c in completions_for(reg, "bulk create ")]
        assert names == ["hunt_group"]

    def test_static_param_source(self):
        reg = make_registry()
        names = [c.text for c in completions_for(reg, "automations group_audit ")]
        assert names == ["SP_One", "SP_Two"]

    def test_dynamic_source_sees_earlier_values(self):
        reg = make_registry()
        names = [
            c.text for c in completions_for(reg, "automations group_audit SP_One ")
        ]
        assert names == ["GroupA", "GroupB"]
        # Different SP -> source returns nothing
        assert completions_for(reg, "automations group_audit SP_Two ") == []

    def test_candidates_with_spaces_inserted_quoted(self):
        reg = CommandRegistry()

        @reg.command("pick")
        @reg.param("name", source=["Sales Team", "Support"])
        def _pick(name):
            return name

        comps = completions_for(reg, "pick Sa")
        assert comps[0].text == '"Sales Team"'

    def test_no_completions_past_last_param(self):
        reg = make_registry()
        assert completions_for(reg, "count 1 ") == []

    def test_unknown_path_yields_nothing(self):
        reg = make_registry()
        assert completions_for(reg, "nonsense sub ") == []

    def test_broken_callable_source_is_safe(self):
        reg = CommandRegistry()

        def boom(ctx):
            raise RuntimeError("completion sources must never crash the prompt")

        @reg.command("risky")
        @reg.param("x", source=boom)
        def _risky(x):
            return x

        assert completions_for(reg, "risky ") == []


def _styles_by_label(frags):
    """Map stripped fragment text -> style, for readable assertions."""
    return {t.strip(): s for s, t in frags if t.strip()}


class TestParamHintToolbar:
    def test_no_hint_while_still_in_command_path(self):
        reg = make_registry()
        assert param_hint_fragments(reg, "") is None
        assert param_hint_fragments(reg, "bulk cre") is None
        assert param_hint_fragments(reg, "bulk create ") is None

    def test_first_param_highlighted_after_command(self):
        reg = make_registry()
        frags = param_hint_fragments(reg, "automations group_audit ")
        text = "".join(t for _, t in frags)
        styles = _styles_by_label(frags)
        assert "<service_provider_id>" in text
        assert "SP ID" in text  # current param's meta shown
        assert styles["<service_provider_id>"] == "bold underline"
        assert styles["<group_id>"] == ""

    def test_highlight_moves_and_stays_while_typing(self):
        reg = make_registry()
        # Mid-typing the second param: it stays highlighted
        frags = param_hint_fragments(reg, "automations group_audit SP_One Grou")
        styles = _styles_by_label(frags)
        assert styles["<group_id>"] == "bold underline"
        assert styles["<service_provider_id>"] == ""

    def test_greedy_param_stays_current(self):
        reg = make_registry()
        frags = param_hint_fragments(reg, "help bulk create hunt")
        styles = _styles_by_label(frags)
        assert styles["<command_path>"] == "bold underline"


def _wide_registry():
    reg = CommandRegistry()

    @reg.command("wide", meta="Command with a wide signature")
    @reg.param("alpha_param", meta="First parameter description")
    @reg.param("beta_param", meta="Second parameter description")
    @reg.param("gamma_param", meta="Third parameter description")
    @reg.param("delta_param", meta="Fourth parameter description")
    def _wide(alpha_param, beta_param, gamma_param, delta_param):
        return None

    return reg


class TestToolbarScrolling:
    def test_no_trim_when_it_fits(self):
        reg = _wide_registry()
        frags = param_hint_fragments(reg, "wide ", width=500)
        text = "".join(t for _, t in frags)
        assert "…" not in text
        assert "<alpha_param>" in text and "<delta_param>" in text

    def test_width_none_never_trims(self):
        reg = _wide_registry()
        frags = param_hint_fragments(reg, "wide ")
        assert "…" not in "".join(t for _, t in frags)

    def test_trims_to_width_and_keeps_current_param_visible(self):
        reg = _wide_registry()
        frags = param_hint_fragments(reg, "wide a b c ", width=40)
        text = "".join(t for _, t in frags)
        assert len(text) <= 40
        assert "<delta_param>" in text  # current param on screen
        assert text.startswith("… ")  # earlier params trimmed away
        styles = _styles_by_label(frags)
        assert styles["<delta_param>"] == "bold underline"

    def test_start_of_signature_trims_right_only(self):
        reg = _wide_registry()
        frags = param_hint_fragments(reg, "wide ", width=40)
        text = "".join(t for _, t in frags)
        assert len(text) <= 40
        assert "<alpha_param>" in text
        assert not text.startswith("…")
        assert text.endswith(" …")

    def test_middle_param_trims_both_sides(self):
        reg = _wide_registry()
        frags = param_hint_fragments(reg, "wide a b ", width=40)
        text = "".join(t for _, t in frags)
        assert len(text) <= 40
        assert "<gamma_param>" in text
        assert text.startswith("… ") and text.endswith(" …")
