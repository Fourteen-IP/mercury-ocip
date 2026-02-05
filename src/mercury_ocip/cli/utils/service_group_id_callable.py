from typing import Iterable, Optional
from action_completer.types import ActionParam, Action
from action_completer.utils import get_fragments
from mercury_ocip.commands.commands import (
    GroupGetListInServiceProviderPagedSortedListRequest,
    GroupGetListInServiceProviderPagedSortedListResponse,
    ServiceProviderGetListRequest,
    ServiceProviderGetListResponse,
    GroupServiceGetAuthorizedListRequest,
    GroupServiceGetAuthorizedListResponse,
)
from mercury_ocip.cli.globals import MERCURY_CLI


def _get_group_id_completions(
    action: Action, param: Optional[ActionParam] = None, value: str = ""
) -> Iterable[str]:
    """
    Provides dynamic completions for the 'group_id' parameter based on the selected 'service_provider_id'.

    Args:
        action (Action): The action for which completions are being provided.
        param (ActionParam): The parameter for which completions are being provided.
        value (str): The current input value for the parameter.

    Returns:
        Iterable[str]: A list of possible completions for the 'group_id' parameter.
    """

    buffer_text = MERCURY_CLI.session().default_buffer.document.text
    fragments = get_fragments(buffer_text)

    group_param_index = next(
        (
            i
            for i, p in enumerate(action.params)
            if p.source == _get_group_id_completions
        ),
        -1,
    )
    sp_param_index = next(
        (
            i
            for i, p in enumerate(action.params)
            if p.source == _get_service_provider_id_completions
        ),
        -1,
    )

    if group_param_index == -1 or sp_param_index == -1:
        return []

    offset = group_param_index - sp_param_index
    fragment_index = len(fragments) - 1 - offset

    if 0 <= fragment_index < len(fragments):
        service_provider_id = fragments[fragment_index]
    else:
        service_provider_id = None

    if not service_provider_id:
        return []

    try:
        groups: GroupGetListInServiceProviderPagedSortedListResponse = (
            MERCURY_CLI.client().command(
                GroupGetListInServiceProviderPagedSortedListRequest(
                    service_provider_id=service_provider_id
                )
            )
        )

        group_table = groups.group_table.to_dict() if groups.group_table else []

        group_ids = [g.get("group_id", "") for g in group_table]
        if value:
            group_ids = [gid for gid in group_ids if str(gid).startswith(value)]
        return group_ids
    except Exception:
        return []


def _get_service_provider_id_completions(
    action: Action, param: Optional[ActionParam] = None, value: str = ""
) -> Iterable[str]:
    """
    Provides dynamic completions for the 'service_provider_id' parameter.

    Args:
        action (Action): The action for which completions are being provided.
        param (ActionParam): The parameter for which completions are being provided.
        value (str): The current input value for the parameter.

    Returns:
        Iterable[str]: A list of possible completions for the 'service_provider_id' parameter.
    """
    service_providers: Optional[ServiceProviderGetListResponse] = None
    try:
        service_providers = MERCURY_CLI.client().command(
            ServiceProviderGetListRequest()
        )

        service_provider_table = (
            service_providers.service_provider_table.to_dict()
            if service_providers.service_provider_table
            else []
        )
    except Exception:
        return []

    try:
        sp_ids = [sp.get("service_provider_id", "") for sp in service_provider_table]
        if value:
            sp_ids = [sid for sid in sp_ids if str(sid).startswith(value)]
        return sp_ids
    except Exception:
        return []

def _get_group_service_pack_completions(
    action: Action, param: Optional[ActionParam] = None, value: str = ""
) -> Iterable[str]:
    """
    Provide completions for a group's service packs.

    This function needs both the selected `service_provider_id` and the
    `group_id` (from other params) so it looks up those values from the
    current buffer fragments.
    """

    buffer_text = MERCURY_CLI.session().default_buffer.document.text
    fragments = get_fragments(buffer_text)

    # Indexes for the params we depend on
    group_param_index = next(
        (
            i
            for i, p in enumerate(action.params)
            if p.source == _get_group_id_completions
        ),
        -1,
    )
    sp_param_index = next(
        (
            i
            for i, p in enumerate(action.params)
            if p.source == _get_service_provider_id_completions
        ),
        -1,
    )
    current_param_index = next(
        (
            i
            for i, p in enumerate(action.params)
            if p.source == _get_group_service_pack_completions
        ),
        -1,
    )

    if group_param_index == -1 or sp_param_index == -1 or current_param_index == -1:
        return []

    # Helper to get a fragment value for a target param index relative to the current param
    def _fragment_for(target_index: int) -> Optional[str]:
        offset = current_param_index - target_index
        fragment_index = len(fragments) - 1 - offset
        if 0 <= fragment_index < len(fragments):
            return fragments[fragment_index]
        return None

    service_provider_id = _fragment_for(sp_param_index)
    group_id = _fragment_for(group_param_index)

    # If we don't yet have both ids, we can't provide completions
    if not service_provider_id or not group_id:
        return []

    try:
        service_table: GroupServiceGetAuthorizedListResponse = (
            MERCURY_CLI.client().command(
                GroupServiceGetAuthorizedListRequest(
                    service_provider_id=service_provider_id,
                    group_id=group_id
                )
            )
        )

        return service_table.service_pack_name
    except Exception:
        return []

    return []