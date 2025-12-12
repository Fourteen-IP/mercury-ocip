from typing import cast, Optional, Dict
from dataclasses import dataclass, field

from mercury_ocip.automate.base_automation import BaseAutomation
from mercury_ocip.client import BaseClient
from mercury_ocip.commands.commands import (
    UserGetRequest23V2,
    UserGetResponse23V2,
    UserAssignedServicesGetListRequest,
    UserAssignedServicesGetListResponse,
    UserCallCenterGetRequest23,
    UserCallCenterGetResponse23
)


@dataclass(slots=True)
class UserDigestRequest:
    user_id: str


@dataclass(slots=True)
class UserDetailsResult:
    user_info: Optional[UserGetResponse23V2] = None
    forwards: Dict[str, str] = field(default_factory=dict)
    dnd_status: Optional[bool] = None
    regstered_devices: Dict[str, str] = field(default_factory=dict)
    assigned_services: Dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class CallCentreDetails:
    call_center_id: str
    call_center_name: str
    agent_level: str


@dataclass(slots=True)
class HuntGroupDetails:
    hunt_group_id: str
    hunt_group_name: str
    extension: str


@dataclass(slots=True)
class CallPickupGroupDetails:
    call_pickup_group_id: str
    call_pickup_group_name: str


@dataclass(slots=True)
class UserDigestResult:
    user_details: Optional[UserDetailsResult] = None
    call_center_membership: Optional[CallCentreDetails] = None
    hunt_group_membership: Optional[HuntGroupDetails] = None
    call_pickup_group_membership: Optional[CallPickupGroupDetails] = None


class UserDigestAutomation(BaseAutomation):
    """Automation to generate a digest of user information."""

    def __init__(self, client: BaseClient) -> None:
        super().__init__(client)

    def _run(self, request: UserDigestRequest) -> UserDigestResult:
        """
        Execute the user digest automation.

        Collects and summarizes user information based on the provided request.

        Args:
            request: Contains parameters for generating the user digest.

        Returns:
            UserDigestResult containing the summarized user information.
        """
        result = UserDigestResult()

    def _fetch_user_details(self, user_id: str) -> UserDetailsResult:
        """Fetch detailed information about the user."""
        
        try:
            user_details = self.client.command(UserGetRequest23V2(user_id=user_id))

            user_services = self.client.command(UserAssignedServicesGetListRequest(user_id=user_id))

            {'serviceName': 'Do Not Disturb', 'isActive': 'false'}
            

        return

    def _fetch_user_assigned_services(
        self, user_id: str
    ) -> UserAssignedServicesGetListResponse:
        """Fetch the list of services assigned to the user."""
        command = UserAssignedServicesGetListRequest(user_id=user_id)
        response = self.client.command(command)
        return cast(UserAssignedServicesGetListResponse, response)
