from typing import Any, cast
from dataclasses import dataclass, field

from mercury_ocip.automate.base_automation import BaseAutomation
from mercury_ocip.client import BaseClient
from mercury_ocip.commands.commands import (
    GroupGetRequest22V5,
    GroupGetResponse22V5,
    GroupDnGetAssignmentListRequest18,
    GroupDnGetAssignmentListResponse18,
    GroupServiceGetAuthorizationListRequest,
    GroupServiceGetAuthorizationListResponse,
)
from mercury_ocip.libs.types import OCIResponse
from mercury_ocip.utils.defines import expand_phone_range


@dataclass(slots=True)
class GroupAuditRequest:
    service_provider_id: str
    group_id: str


@dataclass(slots=True)
class LicenseBreakdown:
    group_services_authorization_table: dict[str, str] = field(default_factory=dict)
    service_packs_authorization_table: dict[str, str] = field(default_factory=dict)
    user_services_authorization_table: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class GroupDns:
    total: int
    numbers: set[str]


@dataclass(slots=True)
class GroupAuditResult:
    group_details: GroupGetResponse22V5 | None = None
    license_breakdown: LicenseBreakdown | None = None
    group_dns: GroupDns | None = None


class GroupAuditor(BaseAutomation[GroupAuditRequest, GroupAuditResult]):
    """Audit a group to collect details, license breakdown, DNS information, and entity counts."""

    def __init__(self, client: BaseClient) -> None:
        super().__init__(client)

    def _run(self, request: GroupAuditRequest) -> GroupAuditResult:
        """
        Execute a comprehensive audit of a group.

        Collects group details, license breakdown, DNS information, and counts
        of various entity types (users, auto attendants, hunt groups, call centers).

        Args:
            request: Contains service_provider_id and group_id to audit.

        Returns:
            GroupAuditResult containing all collected audit information.
        """
        result = GroupAuditResult()
        result.group_details = self._fetch_group_details(request)
        result.license_breakdown = self._fetch_license_breakdown(request)
        result.group_dns = self._fetch_group_dns(request)
        return result

    def _fetch_group_details(self, request: GroupAuditRequest) -> GroupGetResponse22V5:
        """Fetch and return group details."""
        response: OCIResponse = self._dispatch(
            GroupGetRequest22V5(
                service_provider_id=request.service_provider_id,
                group_id=request.group_id,
            )
        )
        response = cast(GroupGetResponse22V5, response)
        return response

    def _fetch_license_breakdown(self, request: GroupAuditRequest) -> LicenseBreakdown:
        """Fetch license breakdown and enrich with usage quantities."""
        response: OCIResponse = self._dispatch(
            GroupServiceGetAuthorizationListRequest(
                service_provider_id=request.service_provider_id,
                group_id=request.group_id,
            )
        )
        response = cast(GroupServiceGetAuthorizationListResponse, response)
        breakdown: dict[str:Any] = response.to_dict()  # type: ignore
        parsed_results: dict[str, dict] = {}
        for key, value in breakdown.items():
            if not value:
                continue
            parsed_results[key] = {}
            for i in range(len(value)):
                usage = value[i].get("usage")
                if usage and usage != "0":
                    service_name = value[i].get("service_pack_name") or value[i].get(
                        "service_name"
                    )
                    if service_name:
                        parsed_results[key][service_name] = usage
        results = LicenseBreakdown(**parsed_results)
        return results

    def _fetch_group_dns(self, request: GroupAuditRequest) -> GroupDns:
        """Fetch and return DNS information."""
        response: OCIResponse = self._dispatch(
            GroupDnGetAssignmentListRequest18(
                service_provider_id=request.service_provider_id,
                group_id=request.group_id,
            )
        )
        response = cast(GroupDnGetAssignmentListResponse18, response)
        dns = set()
        for dn in response.dn_table.to_dict():
            phone_numbers = dn.get("phone_numbers") if dn.get("phone_numbers") else ""
            if " - " in phone_numbers:
                dns.update(expand_phone_range(phone_numbers))
                continue
            dns.add(phone_numbers)

        return GroupDns(total=len(dns), numbers=dns)
