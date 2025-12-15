from mercury_ocip.client import BaseClient
from mercury_ocip.automate.alias_finder import AliasFinder, AliasRequest, AliasResult
from mercury_ocip.automate.group_auditor import (
    GroupAuditor,
    GroupAuditRequest,
    GroupAuditResult,
)
from mercury_ocip.automate.user_digest import (
    UserDigestResult,
    UserDigestRequest,
    UserDigest,
)
from mercury_ocip.automate.base_automation import AutomationResult


class AutomationTasks:
    """Main automation tasks handler"""

    def __init__(self, client: BaseClient):
        self.client = client
        self._alias_finder = AliasFinder(client)
        self._group_auditor = GroupAuditor(client)
        self._user_digest = UserDigest(client)

    def find_alias(
        self, service_provider_id: str, group_id: str, alias: str
    ) -> AutomationResult[AliasResult]:
        request = AliasRequest(
            service_provider_id=service_provider_id, group_id=group_id, alias=alias
        )
        return self._alias_finder.execute(request=request)

    def audit_group(
        self, service_provider_id: str, group_id: str
    ) -> AutomationResult[GroupAuditResult]:
        request = GroupAuditRequest(
            service_provider_id=service_provider_id, group_id=group_id
        )
        return self._group_auditor.execute(request=request)

    def user_digest(self, user_id: str) -> AutomationResult[UserDigestResult]:
        request = UserDigestRequest(user_id=user_id)
        return self._user_digest.execute(request=request)
