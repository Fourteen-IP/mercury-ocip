"""Dynamic completion sources for service provider / group / service pack params.

Each source receives a CompletionContext whose `values` dict holds the raw
values of the command's earlier params, so cross-param lookups (group ids for
a chosen service provider) are plain dictionary reads — no buffer parsing.

Results are cached briefly so the completion menu doesn't fire a server
request on every keystroke.
"""

import time
from typing import Any, Iterable

from mercury_ocip.cli.core import CompletionContext
from mercury_ocip.cli.globals import MERCURY_CLI
from mercury_ocip.commands.commands import (
    GroupGetListInServiceProviderPagedSortedListRequest,
    GroupServiceGetAuthorizedListRequest,
    ServiceProviderGetListRequest,
)

_CACHE_TTL_SECONDS = 30.0
_cache: dict[Any, tuple[float, list[str]]] = {}


def _cached(key: Any, fetch) -> list[str]:
    now = time.monotonic()
    hit = _cache.get(key)
    if hit and now - hit[0] < _CACHE_TTL_SECONDS:
        return hit[1]
    try:
        values = sorted(fetch())
    except Exception:
        return []  # completion must never break the prompt
    _cache[key] = (now, values)
    return values


def clear_cache() -> None:
    _cache.clear()


def service_provider_ids(ctx: CompletionContext) -> Iterable[str]:
    """Complete service provider / enterprise IDs."""

    def fetch() -> list[str]:
        response = MERCURY_CLI.client().command(ServiceProviderGetListRequest())
        table = (
            response.service_provider_table.to_dict()
            if response.service_provider_table
            else []
        )
        return [sp.get("service_provider_id", "") for sp in table]

    return _cached("service_providers", fetch)


def group_ids(ctx: CompletionContext) -> Iterable[str]:
    """Complete group IDs for the already-typed service_provider_id param."""
    service_provider_id = ctx.values.get("service_provider_id")
    if not service_provider_id:
        return []

    def fetch() -> list[str]:
        response = MERCURY_CLI.client().command(
            GroupGetListInServiceProviderPagedSortedListRequest(
                service_provider_id=service_provider_id
            )
        )
        table = response.group_table.to_dict() if response.group_table else []
        return [g.get("group_id", "") for g in table]

    return _cached(("groups", service_provider_id), fetch)


def group_service_packs(ctx: CompletionContext) -> Iterable[str]:
    """Complete service pack names; needs service_provider_id and group_id params."""
    service_provider_id = ctx.values.get("service_provider_id")
    group_id = ctx.values.get("group_id")
    if not service_provider_id or not group_id:
        return []

    def fetch() -> list[str]:
        response = MERCURY_CLI.client().command(
            GroupServiceGetAuthorizedListRequest(
                service_provider_id=service_provider_id, group_id=group_id
            )
        )
        return list(response.service_pack_name or [])

    return _cached(("service_packs", service_provider_id, group_id), fetch)
