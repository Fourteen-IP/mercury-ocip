from mercury_ocip.cli.core import cli, operation
from mercury_ocip.cli.globals import MERCURY_CLI
from mercury_ocip.cli.utils.service_group_id_callable import (
    group_ids,
    service_provider_ids,
)


@cli.command("automations find_alias", meta="Find the given entity behind an alias")
@cli.param("service_provider_id", source=service_provider_ids, meta="Service Provider ID")
@cli.param("group_id", source=group_ids, meta="Group ID")
@cli.param("alias", meta="Alias Number")
def _find_alias(service_provider_id: str, group_id: str, alias: str):
    """
    Find the entity behind a given alias.

    Args:
        service_provider_id: The ID of the service provider.
        group_id: The ID of the group to search in.
        alias: The alias number to look up.
    """
    with operation("Looking up alias...") as op:
        result = MERCURY_CLI.agent().automate.find_alias(
            group_id=group_id,
            service_provider_id=service_provider_id,
            alias=alias,
        )

        if result is None or not result.ok:
            op.fail(f"Alias '{alias}' not found.")
            return

        entity_id = getattr(result.payload.entity, "service_user_id", None) or getattr(
            result.payload.entity, "user_id", None
        )
        op.success(f"Alias '{alias}' found: {entity_id}")
