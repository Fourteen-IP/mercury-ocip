from typing import cast, Optional, TypeVar
from dataclasses import dataclass, field

from mercury_ocip.automate.base_automation import BaseAutomation
from mercury_ocip.client import BaseClient
from mercury_ocip.commands.commands import (
    GroupCallCenterGetInstanceRequest22,
    GroupCallCenterGetInstanceResponse22,
    GroupCallCenterGetAgentListRequest,
    GroupCallCenterGetAgentListResponse,
    GroupCallCenterGetInstanceQueueStatusRequest,
    GroupCallCenterGetInstanceQueueStatusResponse,
    UserCallCenterGetRequest23,
    UserCallCenterGetResponse23,
)
from mercury_ocip.libs.types import OCIResponse
from mercury_ocip.commands.base_command import (
    ErrorResponse,
    SuccessResponse,
    OCIDataResponse,
)

T = TypeVar("T", bound=OCIDataResponse)


@dataclass(slots=True)
class CallCenterDigestRequest:
    """Request parameters for fetching call center digest."""

    service_user_id: str


@dataclass(slots=True)
class CallCenterConfig:
    """General configuration settings for the call center."""

    service_user_id: str
    name: str
    type: str  # Basic, Standard, Premium
    policy: str  # Circular, Regular, Simultaneous, Uniform, Weighted
    routing_type: Optional[str] = None  # Priority Based, Skill Based
    queue_length: int = 0
    enable_video: bool = False
    allow_agent_logoff: bool = False
    allow_call_waiting_for_agents: bool = False
    wrap_up_seconds: Optional[int] = None
    phone_number: Optional[str] = None
    extension: Optional[str] = None


@dataclass(slots=True)
class AgentDetails:
    """Details about an agent assigned to the call center."""

    user_id: str
    last_name: str
    first_name: str
    phone_number: Optional[str] = None
    extension: Optional[str] = None
    department: Optional[str] = None
    email_address: Optional[str] = None
    skill_level: Optional[int] = None
    weight: Optional[int] = None
    is_available: bool = False


@dataclass(slots=True)
class AgentACDStatus:
    """ACD state information for a specific agent."""

    user_id: str
    acd_state: Optional[str] = None  # Sign-In, Sign-Out, Available, Unavailable, Wrap-Up
    unavailable_code: Optional[str] = None
    guard_timer_seconds: int = 0


@dataclass(slots=True)
class QueueStatus:
    """Current queue status for the call center."""

    number_of_calls_queued: int = 0
    agents_staffed: list[dict] = field(default_factory=list)


@dataclass(slots=True)
class CallCenterDigestResult:
    """Complete digest of call center information."""

    config: Optional[CallCenterConfig] = None
    agents: list[AgentDetails] = field(default_factory=list)
    agent_acd_statuses: list[AgentACDStatus] = field(default_factory=list)
    queue_status: Optional[QueueStatus] = None


class CallCenterDigest(BaseAutomation[CallCenterDigestRequest, CallCenterDigestResult]):
    """Automation to generate a digest of call center information."""

    def __init__(self, client: BaseClient) -> None:
        super().__init__(client)

    def _run(self, request: CallCenterDigestRequest) -> CallCenterDigestResult:
        """
        Execute the call center digest automation.

        Args:
            request: Contains the service_user_id of the call center to digest.

        Returns:
            CallCenterDigestResult containing call center config, agents, and queue status.
        """
        config = self._fetch_call_center_config(request.service_user_id)

        agents, agent_acd_statuses = self._fetch_agents_with_status(
            request.service_user_id
        )

        queue_status = self._fetch_queue_status(request.service_user_id)

        return CallCenterDigestResult(
            config=config,
            agents=agents,
            agent_acd_statuses=agent_acd_statuses,
            queue_status=queue_status,
        )

    def _fetch_call_center_config(self, service_user_id: str) -> CallCenterConfig:
        """Fetch the call center instance configuration."""
        response: OCIResponse[GroupCallCenterGetInstanceResponse22] = self._dispatch(
            GroupCallCenterGetInstanceRequest22(service_user_id=service_user_id)
        )
        response = self._clean_response(response)

        return CallCenterConfig(
            service_user_id=service_user_id,
            name=response.service_instance_profile.name,
            type=response.type,
            policy=response.policy,
            routing_type=response.routing_type,
            queue_length=response.queue_length,
            enable_video=response.enable_video,
            allow_agent_logoff=response.allow_agent_logoff,
            allow_call_waiting_for_agents=response.allow_call_waiting_for_agents,
            wrap_up_seconds=response.wrap_up_seconds,
            phone_number=response.service_instance_profile.phone_number,
            extension=response.service_instance_profile.extension,
        )

    def _fetch_agents_with_status(
        self, service_user_id: str
    ) -> tuple[list[AgentDetails], list[AgentACDStatus]]:
        """Fetch agents and their ACD status for this call center."""
        response: OCIResponse[GroupCallCenterGetAgentListResponse] = self._dispatch(
            GroupCallCenterGetAgentListRequest(service_user_id=service_user_id)
        )
        response = self._clean_response(response)

        agents: list[AgentDetails] = []
        acd_statuses: list[AgentACDStatus] = []

        for row in response.agent_table.to_dict():
            user_id = row.get("user_id", "")

            # Get agent's availability for this specific call center
            is_available = False
            acd_state: Optional[str] = None
            unavailable_code: Optional[str] = None
            guard_timer_seconds = 0

            try:
                user_cc_response: OCIResponse[UserCallCenterGetResponse23] = (
                    self._dispatch(UserCallCenterGetRequest23(user_id=user_id))
                )
                user_cc_response = self._clean_response(user_cc_response)

                # Global ACD state for the agent
                acd_state = user_cc_response.agent_acd_state
                unavailable_code = user_cc_response.agent_unavailable_code
                guard_timer_seconds = user_cc_response.guard_timer_seconds

                # Find availability for this specific call center
                for cc_row in user_cc_response.call_center_table.to_dict():
                    if cc_row.get("service_user_id") == service_user_id:
                        is_available = cc_row.get("available", "false").lower() == "true"
                        break

            except Exception as e:
                self.logger.warning(f"Failed to get ACD status for {user_id}: {e}")

            # Convert skill_level and weight from string to int if present
            skill_level_str = row.get("skill_level")
            weight_str = row.get("weight")

            agents.append(
                AgentDetails(
                    user_id=user_id,
                    last_name=row.get("last_name", ""),
                    first_name=row.get("first_name", ""),
                    phone_number=row.get("phone_number"),
                    extension=row.get("extension"),
                    department=row.get("department"),
                    email_address=row.get("email_address"),
                    skill_level=int(skill_level_str) if skill_level_str else None,
                    weight=int(weight_str) if weight_str else None,
                    is_available=is_available,
                )
            )

            acd_statuses.append(
                AgentACDStatus(
                    user_id=user_id,
                    acd_state=acd_state,
                    unavailable_code=unavailable_code,
                    guard_timer_seconds=guard_timer_seconds,
                )
            )

        return agents, acd_statuses

    def _fetch_queue_status(self, service_user_id: str) -> Optional[QueueStatus]:
        """Fetch the current queue status for the call center."""
        try:
            response: OCIResponse[GroupCallCenterGetInstanceQueueStatusResponse] = (
                self._dispatch(
                    GroupCallCenterGetInstanceQueueStatusRequest(
                        service_user_id=service_user_id
                    )
                )
            )
            response = self._clean_response(response)

            return QueueStatus(
                number_of_calls_queued=response.number_of_calls_queued_now,
                agents_staffed=response.agents_currently_staffed.to_dict(),
            )
        except Exception as e:
            self.logger.warning(f"Failed to get queue status for {service_user_id}: {e}")
            return None

    def _clean_response(self, response: OCIResponse[T]) -> T:
        """Validate and return the response data."""
        if isinstance(response, ErrorResponse):
            raise ValueError(f"Error in response: {response.summary}")
        if isinstance(response, SuccessResponse):
            raise ValueError("Received a success response without data.")
        return cast(T, response)
