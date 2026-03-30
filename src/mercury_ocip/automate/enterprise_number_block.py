from typing import cast

from attr import dataclass

from mercury_ocip.automate.base_automation import BaseAutomation
from mercury_ocip.client import BaseClient
from mercury_ocip.commands.commands import (
    GroupCallingPlanAddDigitPatternRequest,
    GroupGetListInServiceProviderRequest,
    GroupGetListInServiceProviderResponse,
    GroupIncomingCallingPlanModifyListRequest,
    IncomingCallingPlanDigitPatternPermission,
    IncomingCallingPlanPermissionsModify,
)


@dataclass(slots=True)
class EnterpriseNumBlockRequest:
    """Input for the EnterpriseNumBlock automation.

    Attributes:
        enterprise_id: The service provider / enterprise ID to target.
        number: The digit pattern (e.g. phone number) to block.
    """

    enterprise_id: str
    number: str


@dataclass(slots=True)
class EnterpriseNumBlockResult:
    """Result of the EnterpriseNumBlock automation.

    Attributes:
        digit_plan: The digit pattern permission that was applied to every group.
    """

    digit_plan: IncomingCallingPlanDigitPatternPermission


class EnterpriseNumBlock(
    BaseAutomation[EnterpriseNumBlockRequest, EnterpriseNumBlockResult]
):
    """Automation to block a number across all groups in an enterprise."""

    def __init__(self, client: BaseClient) -> None:
        super().__init__(client)

    def _run(self, request: EnterpriseNumBlockRequest) -> EnterpriseNumBlockResult:
        """Iterate every group in the enterprise and apply the block.

        Args:
            request: Contains the enterprise ID and number to block.

        Returns:
            EnterpriseNumBlockResult with the digit plan that was applied.
        """
        groups = self._get_groups_in_enterprise(request.enterprise_id)

        pattern_name = f"Block {request.number}"
        digit_plan = IncomingCallingPlanDigitPatternPermission(
            digit_pattern_name=pattern_name,
            allow=False,
        )

        for group_id in groups:
            # Register the digit pattern on the group's calling plan.
            self._dispatch(
                GroupCallingPlanAddDigitPatternRequest(
                    service_provider_id=request.enterprise_id,
                    group_id=group_id,
                    name=pattern_name,
                    digit_pattern=request.number,
                )
            )

            # Set the incoming calling plan permission to deny.
            self._dispatch(
                GroupIncomingCallingPlanModifyListRequest(
                    service_provider_id=request.enterprise_id,
                    group_id=group_id,
                    group_permissions=IncomingCallingPlanPermissionsModify(
                        digit_pattern_permission=[digit_plan],
                    ),
                )
            )

        return EnterpriseNumBlockResult(digit_plan=digit_plan)

    def _get_groups_in_enterprise(self, enterprise_id: str) -> list[str]:
        """Fetch all group IDs belonging to the given enterprise.

        Args:
            enterprise_id: The service provider / enterprise ID to query.

        Returns:
            A list of group ID strings.
        """
        response = cast(
            GroupGetListInServiceProviderResponse,
            self._dispatch(
                GroupGetListInServiceProviderRequest(service_provider_id=enterprise_id)
            ),
        )
        return [row.get("group_id", "") for row in response.group_table.to_dict()]
