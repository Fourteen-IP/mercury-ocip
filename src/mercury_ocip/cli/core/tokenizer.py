"""Windows-friendly shell-style tokenizer.

Rules:
    - Tokens split on runs of unquoted whitespace.
    - Single or double quotes group words into one token: "my file.csv".
    - Backslashes are literal (so C:\\temp\\file.csv works unquoted).
    - A quote may open mid-token: name="a b" -> 'name=a b'.
"""

from dataclasses import dataclass

from mercury_ocip.cli.core.errors import CommandSyntaxError

QUOTES = "\"'"


@dataclass
class TokenizedLine:
    """Result of tokenizing a (possibly incomplete) input line.

    Attributes:
        tokens: The parsed tokens, quotes stripped.
        last_token_start: Raw string index where the final token begins
            (including its opening quote), or None if the line ends on
            whitespace / is empty — i.e. the cursor would start a new token.
        open_quote: The unclosed quote character, if any.
    """

    tokens: list[str]
    last_token_start: int | None
    open_quote: str | None

    @property
    def in_token(self) -> bool:
        return self.last_token_start is not None


def _tokenize(line: str) -> TokenizedLine:
    tokens: list[str] = []
    current: list[str] = []
    quote: str | None = None
    token_start: int | None = None

    for i, ch in enumerate(line):
        if quote:
            if ch == quote:
                quote = None
            else:
                current.append(ch)
        elif ch in QUOTES:
            quote = ch
            if token_start is None:
                token_start = i
        elif ch.isspace():
            if token_start is not None:
                tokens.append("".join(current))
                current = []
                token_start = None
        else:
            if token_start is None:
                token_start = i
            current.append(ch)

    if token_start is not None:
        tokens.append("".join(current))

    return TokenizedLine(tokens=tokens, last_token_start=token_start, open_quote=quote)


def tokenize(line: str) -> list[str]:
    """Tokenize a complete line for execution. Raises on unclosed quotes."""
    result = _tokenize(line)
    if result.open_quote:
        raise CommandSyntaxError(
            f"Unclosed {result.open_quote} quote in command. "
            f"Add a closing {result.open_quote} or remove the opening one."
        )
    return result.tokens


def tokenize_incomplete(line: str) -> TokenizedLine:
    """Tokenize a line still being typed (for completion). Never raises."""
    return _tokenize(line)


def quote_arg(value: str) -> str:
    """Quote a value for insertion into the command line if it needs it."""
    if not value or any(ch.isspace() for ch in value) or value[0] in QUOTES:
        quote = "'" if '"' in value else '"'
        return f"{quote}{value}{quote}"
    return value
