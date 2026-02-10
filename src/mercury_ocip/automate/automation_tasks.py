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
from mercury_ocip.automate.call_center_digest import (
    CallCenterDigest,
    CallCenterDigestRequest,
    CallCenterDigestResult,
)
from mercury_ocip.automate.base_automation import AutomationResult


class AutomationTasks:
    """Main automation tasks handler"""

    def __init__(self, client: BaseClient):
        self.client = client
        self._alias_finder = AliasFinder(client)
        self._group_auditor = GroupAuditor(client)
        self._user_digest = UserDigest(client)
        self._call_center_digest = CallCenterDigest(client)
        self.client.logger.debug("AutomationTasks initialized")

    def find_alias(
        self, service_provider_id: str, group_id: str, alias: str
    ) -> AutomationResult[AliasResult]:
        self.client.logger.info(
            f"Executing find_alias automation for {service_provider_id}/{group_id}/{alias}"
        )
        request = AliasRequest(
            service_provider_id=service_provider_id, group_id=group_id, alias=alias
        )
        result = self._alias_finder.execute(request=request)

        self.client.logger.info(
            msg="find_alias automation completed",
            extra={
                "event": {
                    "type": "execution",
                    "category": "automation",
                    "outcome": "success" if result.ok else "failure",
                },
                "log": {"type": "performance", "command": "find_alias"},
                "metrics": {"time_saved_ms": 600000},
            },
        )
        return result

    def audit_group(
        self, service_provider_id: str, group_id: str
    ) -> AutomationResult[GroupAuditResult]:
        self.client.logger.info(
            f"Executing audit_group automation for {service_provider_id}/{group_id}"
        )

        request = GroupAuditRequest(
            service_provider_id=service_provider_id, group_id=group_id
        )
        result = self._group_auditor.execute(request=request)

        self.client.logger.info(
            msg="audit_group automation completed",
            extra={
                "event": {
                    "type": "execution",
                    "category": "automation",
                    "outcome": "success" if result.ok else "failure",
                },
                "log": {"type": "performance", "command": "audit_group"},
                "metrics": {"time_saved_ms": 900000},
            },
        )

        return result

    def user_digest(self, user_id: str) -> AutomationResult[UserDigestResult]:
        self.client.logger.info(f"Executing user_digest automation for {user_id}")
        request = UserDigestRequest(user_id=user_id)
        result = self._user_digest.execute(request=request)

        self.client.logger.info(
            msg="user_digest automation completed",
            extra={
                "event": {
                    "type": "execution",
                    "category": "automation",
                    "outcome": "success" if result.ok else "failure",
                },
                "log": {"type": "performance", "command": "user_digest"},
                "metrics": {"time_saved_ms": 900000},
            },
        )

        return result

    def call_center_digest(
        self, service_user_id: str
    ) -> AutomationResult[CallCenterDigestResult]:
        self.client.logger.info(
            f"Executing call_center_digest automation for {service_user_id}"
        )
        request = CallCenterDigestRequest(service_user_id=service_user_id)
        result = self._call_center_digest.execute(request=request)

        self.client.logger.info(
            msg="call_center_digest automation completed",
            extra={
                "event": {
                    "type": "execution",
                    "category": "automation",
                    "outcome": "success" if result.ok else "failure",
                },
                "log": {"type": "performance", "command": "call_center_digest"},
                "metrics": {"time_saved_ms": 1000000},
            },
        )

        return result
