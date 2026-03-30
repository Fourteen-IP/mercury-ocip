from dataclasses import dataclass
from typing import cast

from mercury_ocip.automate.base_automation import BaseAutomation
from mercury_ocip.client import BaseClient
from mercury_ocip.commands.commands import (
    GroupCallingPlanAddDigitPatternRequest,
    GroupDepartmentGetListRequest18,
    GroupDepartmentGetListResponse18,
    GroupDepartmentKey,
    GroupGetListInServiceProviderRequest,
    GroupGetListInServiceProviderResponse,
    GroupIncomingCallingPlanModifyListRequest,
    IncomingCallingPlanDepartmentPermissionsModify,
    IncomingCallingPlanDigitPatternPermission,
    IncomingCallingPlanPermissionsModify,
)
from mercury_ocip.exceptions import MErrorResponse


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
    """Automation to block a number across all groups and their departments in an enterprise.

    For each group in the enterprise this automation:
      1. Adds the digit pattern via GroupCallingPlanAddDigitPatternRequest.
      2. Applies a deny permission at group level and for every department via
         GroupIncomingCallingPlanModifyListRequest.

    If BroadWorks rejects the operation for a specific group (MErrorResponse), that
    group is skipped with a warning and processing continues. System-level errors
    (MErrorUnknown, MErrorTimeOut) are always propagated.
    """

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
            try:
                self._dispatch(
                    GroupCallingPlanAddDigitPatternRequest(
                        service_provider_id=request.enterprise_id,
                        group_id=group_id,
                        name=pattern_name,
                        digit_pattern=request.number,
                    )
                )

                department_permissions = self._build_department_permissions(
                    enterprise_id=request.enterprise_id,
                    group_id=group_id,
                    digit_plan=digit_plan,
                )

                self._dispatch(
                    GroupIncomingCallingPlanModifyListRequest(
                        service_provider_id=request.enterprise_id,
                        group_id=group_id,
                        group_permissions=IncomingCallingPlanPermissionsModify(
                            digit_pattern_permission=[digit_plan],
                        ),
                        department_permissions=department_permissions,
                    )
                )

            except MErrorResponse as e:
                self.client.logger.warning(
                    f"Skipping group {group_id} due to an error: {e}"
                )

        return EnterpriseNumBlockResult(digit_plan=digit_plan)

    def _build_department_permissions(
        self,
        enterprise_id: str,
        group_id: str,
        digit_plan: IncomingCallingPlanDigitPatternPermission,
    ) -> list[IncomingCallingPlanDepartmentPermissionsModify]:
        """Build a deny permission entry for every department in a group.

        Args:
            enterprise_id: The service provider / enterprise ID.
            group_id: The group whose departments to target.
            digit_plan: The digit pattern permission to apply.

        Returns:
            A list of IncomingCallingPlanDepartmentPermissionsModify, one per department.
        """
        departments = self._get_departments_in_group(enterprise_id, group_id)
        return [
            IncomingCallingPlanDepartmentPermissionsModify(
                department_key=GroupDepartmentKey(
                    service_provider_id=enterprise_id,
                    group_id=group_id,
                    name=dept_name,
                ),
                digit_pattern_permission=[digit_plan],
            )
            for dept_name in departments
        ]

    def _get_departments_in_group(self, enterprise_id: str, group_id: str) -> list[str]:
        """Fetch all department names belonging to the given group.

        Args:
            enterprise_id: The service provider / enterprise ID.
            group_id: The group to query.

        Returns:
            A list of department name strings.
        """
        response = cast(
            GroupDepartmentGetListResponse18,
            self._dispatch(
                GroupDepartmentGetListRequest18(
                    service_provider_id=enterprise_id,
                    group_id=group_id,
                    include_enterprise_departments=False,
                )
            ),
        )
        return [
            row.get("department_name", "")
            for row in response.department_table.to_dict()
        ]

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
