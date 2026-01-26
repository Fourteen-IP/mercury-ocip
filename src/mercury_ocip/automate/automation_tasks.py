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
        self.logger = client.logger
        self._alias_finder = AliasFinder(client)
        self._group_auditor = GroupAuditor(client)
        self._user_digest = UserDigest(client)
        self.logger.debug("AutomationTasks initialized")

    def find_alias(
        self, service_provider_id: str, group_id: str, alias: str
    ) -> AutomationResult[AliasResult]:
        self.logger.info(f"Executing find_alias automation for {service_provider_id}/{group_id}/{alias}")
        request = AliasRequest(
            service_provider_id=service_provider_id, group_id=group_id, alias=alias
        )
        result = self._alias_finder.execute(request=request)
        self.logger.debug(f"find_alias automation completed with status: {result.ok}  | Time Saved: 20")
        return result

    def audit_group(
        self, service_provider_id: str, group_id: str
    ) -> AutomationResult[GroupAuditResult]:
        self.logger.info(f"Executing audit_group automation for {service_provider_id}/{group_id}")
        request = GroupAuditRequest(
            service_provider_id=service_provider_id, group_id=group_id
        )
        result = self._group_auditor.execute(request=request)
        self.logger.debug(f"audit_group automation completed with status: {result.ok}  | Time Saved: 35")
        return result

    def user_digest(self, user_id: str) -> AutomationResult[UserDigestResult]:
        self.logger.info(f"Executing user_digest automation for {user_id}")
        request = UserDigestRequest(user_id=user_id)
        result = self._user_digest.execute(request=request)
        self.logger.debug(f"user_digest automation completed with status: {result.ok}  | Time Saved: 25")
        return result
