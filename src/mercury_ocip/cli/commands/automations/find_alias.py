from mercury_ocip.cli.globals import MERCURY_CLI
from action_completer import Empty
from mercury_ocip.cli.utils.service_group_id_callable import (
    _get_group_id_completions,
    _get_service_provider_id_completions,
)

console = MERCURY_CLI.console()
completer = MERCURY_CLI.completer()


@completer.automations.action(
    "find_alias", display_meta="Find the given entity behind an alias"
)
@completer.param(
    _get_service_provider_id_completions,
    display_meta="Service Provider ID",
    cast=str,
)
@completer.param(_get_group_id_completions, display_meta="Group ID", cast=str)
@completer.param(Empty, display="alias", display_meta="Alias Number", cast=str)
def _find_alias(service_provider_id: str, group_id: str, alias: str):
    """
    Find the entity behind a given alias.

    Args:
        alias_name: The name of the alias to look up.
    """
    with console.status(
        "[cyan]Looking up alias...", spinner="dots", spinner_style="cyan"
    ) as status:
        try:
            result = MERCURY_CLI.agent().automate.find_alias(
                group_id=group_id,
                service_provider_id=service_provider_id,
                alias=alias,
            )

            status.stop()

            if result is None:
                console.print(f"✘ Alias '{alias}' not found.", style="red")
                return

            if result.ok:
                entity_id = getattr(
                    result.payload.entity, "service_user_id", None
                ) or getattr(result.payload.entity, "user_id", None)

                console.print(f"✔ Alias '{alias}' found: {entity_id}", style="green")
            else:
                console.print(f"✘ Alias '{alias}' not found.", style="red")

        except Exception as e:
            status.stop()
            console.print(f"✘ {e}", style="red")
