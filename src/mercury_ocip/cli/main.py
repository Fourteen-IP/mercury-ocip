import argparse
import os
import sys
from importlib import metadata

from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.styles import Style
from rich.prompt import Prompt
from rich.text import Text

from mercury_ocip.cli.commands.misc.plugins import load_plugins
from mercury_ocip.cli.globals import MERCURY_CLI
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

# CSS Style for the CLI
console = MERCURY_CLI.console()

parser = argparse.ArgumentParser()  # For non interactive commands
parser.add_argument("--no-login", required=False, action="store_true")
parser.add_argument("--username", required=False, type=str)
parser.add_argument("--password-env", required=False, type=str)
parser.add_argument("--host", required=False, type=str)
parser.add_argument("--action", required=False, type=str)
args = parser.parse_args()


def show_splash() -> None:
    """
    Prints out the SPLASH_ART and welcome message to the console.
    """

    version = metadata.version("mercury-ocip")
    welcome_text = Text.assemble(
        (SPLASH_ART, "header"),
        ("\nWelcome to mercury_cli ", "subheader"),
        (f"v{version}\n\n", "version"),
        ("─" * 60 + "\n", "divider"),
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
                MERCURY_CLI.completer().run_action(args.action)
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
        message="mercury_cli >>> ",
        style=Style.from_dict({"prompt": "ansicyan bold #c0fdff"}),
        refresh_interval=1,
        completer=MERCURY_CLI.completer(),
        auto_suggest=AutoSuggestFromHistory(),
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

    Raises:
        SystemExit: When the user exits the CLI (e.g., via Ctrl+C or EOF).
        Exception: For any unexpected errors during command execution.

    Returns:
        None

    """
    while True:
        try:
            text = MERCURY_CLI.session().prompt()
            match text.strip():
                case "":  # If command is empty, ignore and re-prompt
                    continue
                case "mercury":  # Hidden easter egg command
                    egg_main()
                    continue
                case _:  # Default case to run any other command
                    try:
                        MERCURY_CLI.completer().run_action(text)
                    except MErrorSocketTimeout:
                        MERCURY_CLI.client().authenticated = False
                    except ValueError as ve:
                        # Check if this is actually a "command not found" error
                        if (
                            "not found" in str(ve).lower()
                            or "no action" in str(ve).lower()
                        ):
                            console.print(
                                f"[error]Unknown command \"{text}\". Type 'help' for a list of commands.[/error]"
                            )
                        else:
                            # Other ValueError (like spinner terminal size issues)
                            console.print(f"[error]Error: {ve}[/error]")
                    except Exception as e:
                        console.print(f"[error]Error executing command: {e}[/error]")

        except (KeyboardInterrupt, EOFError):
            console.print("Exiting mercury_cli. Goodbye!")
            MERCURY_CLI.client().disconnect()  # Mercury Client Cleanup
            sys.exit()

        except Exception as e:
            console.print(f"[error]Error: {e}[/error]")
            pass  # Ignore errors so it doesnt crash the cli


if __name__ == "__main__":
    main()
