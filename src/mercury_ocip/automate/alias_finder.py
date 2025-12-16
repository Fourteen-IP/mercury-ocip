import re
from dataclasses import dataclass, field
from typing import Optional, Callable, TypedDict, List, Iterable, Mapping

from mercury_ocip.automate.base_automation import BaseAutomation, AutomationResult
from mercury_ocip.client import BaseClient
from mercury_ocip.libs.types import OCIResponse


@dataclass(slots=True)
class AliasRequest:
    service_provider_id: str
    group_id: str
    alias: str


@dataclass(slots=True)
class AliasResult:
    found: bool = field(default=False)
    entity: Optional[OCIResponse] = None
    message: str = "Alias not found."


FetchDetailsCallable = Callable[[str, str], list[OCIResponse]]


class CheckedEntity(TypedDict):
    type: str
    func: FetchDetailsCallable


class AliasFinder(BaseAutomation[AliasRequest, AliasResult]):
    """Find alias assignments in a group"""

    def __init__(self, client: BaseClient) -> None:
        super().__init__(client)

    def _run(self, request: AliasRequest) -> AliasResult:
        """
        Execute the alias search across multiple entity types within a group.

        Iterates through Call Centers, Hunt Groups, Auto Attendants, and Users
        to locate an entity with the specified alias.

        Args:
            request: Contains service_provider_id, group_id, and alias to search for.

        Returns:
            AliasResult with found=True and the matching entity if located,
            otherwise found=False with a default message.
        """

        checked_entities: list[CheckedEntity] = [
            {
                "type": "Call Center",
                "func": self.shared_ops.fetch_call_center_details,
            },
            {
                "type": "Hunt Group",
                "func": self.shared_ops.fetch_hunt_group_details,
            },
            {
                "type": "Auto Attendant",
                "func": self.shared_ops.fetch_auto_attendant_details,
            },
            {
                "type": "User",
                "func": self.shared_ops.fetch_user_details,
            },
        ]

        # class defaults to alias not found.
        result = AliasResult()

        for e in checked_entities:
            matched_entity: OCIResponse | None = self._locate_alias(e["func"], request)
            if matched_entity:
                result.found = True
                result.entity = matched_entity
                result.message = "Alias found."
                break

        return result

    def _locate_alias(
        self,
        fetch_details: FetchDetailsCallable,
        request: AliasRequest,
    ) -> OCIResponse | None:
        """
        Search for an alias within a specific entity type.

        Fetches all entities of a given type and checks each for a matching alias.

        Args:
            fetch_details: Function to retrieve entities (e.g., fetch_user_details).
            request: Contains service_provider_id, group_id, and target alias.

        Returns:
            The OCIResponse entity containing the matching alias, or None if not found.
        """

        # func in v1 is _details() functions which all only take SP + GRP ID
        entities: List[OCIResponse] | [] = fetch_details(  # type: ignore
            service_provider_id=request.service_provider_id,  # type: ignore
            group_id=request.group_id,  # type: ignore
        )

        for entity in entities:
            for candidate in self._extract_alias_candidates(entity):
                if self._check_for_alias(candidate, request.alias):
                    return entity

        return None

    def _extract_alias_candidates(self, entity: object) -> list[str]:
        """
        Extract all alias values from an entity object.

        Handles entities with direct 'alias' attributes or aliases nested within
        'service_instance_profile' mappings. Supports single strings or iterables.

        Args:
            entity: The entity object to extract aliases from.

        Returns:
            List of alias strings found, or empty list if none exist.
        """

        sip = getattr(entity, "service_instance_profile", None)

        if hasattr(entity, "alias"):
            raw = getattr(entity, "alias")
        else:
            sip = getattr(entity, "service_instance_profile", None)
            raw = (
                sip.get("alias")
                if isinstance(sip, Mapping)
                else getattr(sip, "alias", None)
            )  # SIP can be dict or object due to Parser changes

        if raw is None:
            return []
        if isinstance(raw, str):
            return [raw]
        if isinstance(raw, Iterable):
            return [item for item in raw if isinstance(item, str)]
        return []

    def _check_for_alias(self, candidate_value: str, target_alias: str) -> bool:
        """
        Compares the supplied alias candidate with the target alias, ignoring the domain part.
        """
        if not isinstance(candidate_value, str):
            return False
        match = re.match(r"^([^\@]+)", candidate_value)
        if match:
            alias_candidate = match.group(1)
            return alias_candidate == target_alias
        return False

    def _wrap(self, payload: AliasResult) -> AutomationResult[AliasResult]:
        """
        Wrap the AliasResult in an AutomationResult container.

        Overrides the base implementation to set the 'ok' status and message
        based on whether the alias was found.

        Args:
            payload: The AliasResult containing search outcome.

        Returns:
            AutomationResult with ok and message fields populated from payload.
        """
        result = super()._wrap(payload)
        result.ok = payload.found
        result.message = payload.message
        return result
