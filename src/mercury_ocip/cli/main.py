import argparse
import os
import sys
from importlib import metadata
from urllib.parse import urlparse

from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.styles import Style
from rich.prompt import Prompt
from rich.text import Text

from mercury_ocip.cli.commands.misc.plugins import load_plugins
from mercury_ocip.cli.core import (
    CommandAborted,
    CommandSyntaxError,
    IncompleteCommandError,
    UnknownCommandError,
    cli,
    dispatch,
    gradient_text,
    make_bottom_toolbar,
    set_quit_hint,
)
from mercury_ocip.cli.core.errors import CLIError
from mercury_ocip.cli.globals import MERCURY_CLI, THEME_COLORS
from mercury_ocip.cli.utils.egg import main as egg_main  # noqa: F401
from mercury_ocip.exceptions import MError, MErrorSocketTimeout

SPLASH_ART = """
███╗   ███╗███████╗██████╗  ██████╗██╗   ██╗██████╗ ██╗   ██╗      ██████╗██╗     ██╗
████╗ ████║██╔════╝██╔══██╗██╔════╝██║   ██║██╔══██╗╚██╗ ██╔╝     ██╔════╝██║     ██║
██╔████╔██║█████╗  ██████╔╝██║     ██║   ██║██████╔╝ ╚████╔╝█████╗██║     ██║     ██║
██║╚██╔╝██║██╔══╝  ██╔══██╗██║     ██║   ██║██╔══██╗  ╚██╔╝ ╚════╝██║     ██║     ██║
██║ ╚═╝ ██║███████╗██║  ██║╚██████╗╚██████╔╝██║  ██║   ██║        ╚██████╗███████╗██║
╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝         ╚═════╝╚══════╝╚═╝
"""
SPLASH_ART_WIDTH = max(len(line) for line in SPLASH_ART.splitlines())

# CSS Style for the CLI
console = MERCURY_CLI.console()

PROMPT_STYLE = Style.from_dict(
    {
        "prompt": "ansicyan bold #c0fdff",
        "muted": THEME_COLORS["muted"],
    }
)


def _short_host(host: str) -> str:
    """Just the hostname, so a full SOAP endpoint URL doesn't dominate the prompt."""
    parsed = urlparse(host if "//" in host else f"//{host}")
    return parsed.hostname or host


def build_prompt_message():
    """Callable PromptSession message: re-evaluated on every prompt, so it
    reflects the live connection (including after a reconnect)."""
    client = MERCURY_CLI.client()
    host = getattr(client, "host", None) if client else None

    text = f"mercury ({_short_host(host)}) ❯ " if host else "mercury ❯ "
    return [("class:prompt", text)]


def parse_args(argv=None):
    """Parse CLI flags. Kept out of module import so importing this module
    (e.g. from tests) never consumes sys.argv."""
    parser = argparse.ArgumentParser()  # For non interactive commands
    parser.add_argument("--no-login", required=False, action="store_true")
    parser.add_argument("--username", required=False, type=str)
    parser.add_argument("--password-env", required=False, type=str)
    parser.add_argument("--host", required=False, type=str)
    parser.add_argument("--action", required=False, type=str)
    return parser.parse_args(argv)


def show_splash() -> None:
    """
    Prints out the SPLASH_ART and welcome message to the console.

    The full ASCII banner is 85 columns wide; on a narrower terminal Rich
    would silently crop each line to fit, mangling the art instead of
    shrinking it, so a compact text wordmark is used below that width.
    """

    version = metadata.version("mercury-ocip")
    if console.size.width >= SPLASH_ART_WIDTH:
        console.print(
            gradient_text(SPLASH_ART, "#deaaff", "#b288cc"),
            justify="center",
            overflow="crop",
            no_wrap=True,
        )
    else:
        console.print(
            Text("MERCURY CLI", style="header bold", justify="center"),
            justify="center",
        )
    divider_width = min(60, max(console.size.width - 4, 10))
    welcome_text = Text.assemble(
        (f"v{version}\n\n", "version"),
        ("─" * divider_width + "\n", "divider"),
        justify="center",
    )
    console.print(welcome_text, justify="center", overflow="crop", no_wrap=True)


def authenticate() -> None:
    """
    Prompts the user for authentication details and authenticates the mercury client.
    """

    username = Prompt.ask("[prompt]Username [/prompt]", console=console)
    password = Prompt.ask("[prompt]Password [/prompt]", password=True, console=console)
    host = Prompt.ask(
        "[prompt]URL [/prompt]",
        console=console,
    )

    if not host.endswith("/webservice/services/ProvisioningService"):
        suffix = "/webservice/services/ProvisioningService"

        suffix_append = Prompt.ask(
            f"[prompt]Append Provisioning Service suffix?[/prompt]\n"
            f"  {host}[dim]{suffix}[/dim]",
            console=console,
            choices=["y", "n"],
            default="y",
        )

        if suffix_append == "y":
            host += suffix

    MERCURY_CLI.get().client_auth(
        username=username, password=password, host=host, tls=True
    )  # Authenticate mercury client


def main():
    """
    Main entry point for the mercury_cli application.

    Handles user authentication, session creation, and command processing loop.
    """
    args = parse_args()
    show_splash()

    if args.username and args.password_env and args.host:
        try:
            password_env = os.getenv(args.password_env)

            if not password_env:
                raise ValueError("Failed to fetch environment variable")

            MERCURY_CLI.get().client_auth(
                username=args.username,
                password=password_env,
                host=args.host,
                tls=True,
            )

            if args.action:  # Run single action and exit
                dispatch(args.action, interactive=False)
                sys.exit()
        except Exception as e:
            console.print(f"[error]Authentication failed: {e}[/error]")
            sys.exit(1)
    elif not args.no_login:
        # Retry loop for interactive authentication.
        # MError covers recoverable issues (bad credentials, timeouts, etc.)
        # so we let the user try again. Any other exception is likely a
        # configuration or network problem we can't recover from, so we exit.
        while True:
            try:
                authenticate()
                break
            except MError as e:
                console.print(
                    f"[error]Authentication failed: {e} \n Please try again.\n [/error]"
                )
                continue
            except Exception as e:
                console.print(
                    f"[error]Authentication failed: {e} \n Please try again.\n [/error]"
                )
                sys.exit(1)

    MERCURY_CLI.get().session_create(  # Create terminal prompt session
        message=build_prompt_message,
        style=PROMPT_STYLE,
        refresh_interval=1,
        completer=MERCURY_CLI.completer(),
        auto_suggest=AutoSuggestFromHistory(),
        bottom_toolbar=make_bottom_toolbar(cli),
    )

    try:
        if args.no_login:
            console.print(
                "[yellow]Warning: You are running in no-login mode. There is no client session, no commands can be sent to the server.[/]"
            )
        else:
            load_plugins()
    except Exception as e:
        print(f"Plugins failed to load: {e}")

    command_loop()


def command_loop() -> None:
    """
    Main command processing loop for mercury_cli.
    Continuously prompts the user for commands and executes them.

    Ctrl+C at the prompt clears the current line and re-prompts (standard
    shell behaviour); a second Ctrl+C right after, with nothing typed in
    between, exits. Ctrl+D (EOF) always exits immediately.

    Raises:
        SystemExit: When the user exits the CLI (e.g., via Ctrl+D, or a
            second Ctrl+C).
        Exception: For any unexpected errors during command execution.

    Returns:
        None

    """

    def _exit():
        console.print("Exiting mercury_cli. Goodbye!")
        if MERCURY_CLI.client():
            MERCURY_CLI.client().disconnect()  # Mercury Client Cleanup
        sys.exit()

    interrupted = False
    while True:
        try:
            text = MERCURY_CLI.session().prompt()
            interrupted = False
            set_quit_hint(False)
        except KeyboardInterrupt:
            if interrupted:
                _exit()
            interrupted = True
            set_quit_hint(True)  # bottom toolbar shows the hint; no printed line
            continue
        except EOFError:
            _exit()

        try:
            match text.strip():
                case "":  # If command is empty, ignore and re-prompt
                    continue
                case "mercury":  # Hidden easter egg command
                    egg_main()
                    continue
                case _:  # Default case to run any other command
                    try:
                        dispatch(text)
                    except MErrorSocketTimeout:
                        MERCURY_CLI.client().authenticated = False
                    except CommandAborted:
                        pass  # User cancelled a prompt (Ctrl+C) — back to the loop
                    except UnknownCommandError as e:
                        console.print(
                            f"[error]{e}[/error] Type 'help' for a list of commands."
                        )
                    except IncompleteCommandError as e:
                        console.print(f"[error]{e}[/error]")
                        if e.subcommands:
                            console.print(f"Available: {', '.join(e.subcommands)}")
                    except (CommandSyntaxError, CLIError) as e:
                        console.print(f"[error]{e}[/error]")
                    except Exception as e:
                        console.print(f"[error]Error executing command: {e}[/error]")

        except Exception as e:
            console.print(f"[error]Error: {e}[/error]")
            pass  # Ignore errors so it doesnt crash the cli


if __name__ == "__main__":
    main()
