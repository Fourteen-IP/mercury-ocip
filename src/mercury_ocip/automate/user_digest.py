from typing import cast, Optional, Dict
from dataclasses import dataclass, field

from mercury_ocip.automate.base_automation import BaseAutomation
from mercury_ocip.client import BaseClient
from mercury_ocip.commands.commands import (
    UserGetRequest23V2,
    UserGetResponse23V2,
    UserCallForwardingAlwaysGetRequest,
    UserCallForwardingBusyGetRequest,
    UserCallForwardingNoAnswerGetRequest13mp16,
    UserCallForwardingNotReachableGetRequest,
    UserCallForwardingSelectiveGetRequest16,
    UserCallForwardingSelectiveGetResponse16,
    UserDoNotDisturbGetRequest,
    UserAccessDeviceDeviceActivationGetListRequest,
    UserAccessDeviceDeviceActivationGetListResponse,
)
from mercury_ocip.libs.types import OCIResponse
from mercury_ocip.commands.base_command import ErrorResponse, SuccessResponse, OCITable


@dataclass(slots=True)
class UserDigestRequest:
    user_id: str


@dataclass(slots=True)
class ForwardingDetails:
    is_active: bool
    forward_to_phone_number: Optional[str] = None
    selective_criteria: Optional[OCITable] = None


@dataclass(slots=True)
class DeviceDetails:
    device_name: str
    device_type: str
    line_port: str
    activation_status: str


@dataclass(slots=True)
class UserDetailsResult:
    user_info: Optional[UserGetResponse23V2] = None
    forwards: list[ForwardingDetails] = field(default_factory=list)
    dnd_status: Optional[bool] = None
    regstered_devices: Dict[str, str] = field(default_factory=dict)


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


class UserDigest(BaseAutomation):
    """Automation to generate a digest of user information."""

    def __init__(self, client: BaseClient) -> None:
        super().__init__(client)
        self.forwarding_details = []

    def _run(self, request: UserDigestRequest) -> UserDigestResult:
        """
        Execute the user digest automation.

        Collects and summarizes user information based on the provided request.

        Args:
            request: Contains parameters for generating the user digest.

        Returns:
            UserDigestResult containing the summarized user information.
        """
        return UserDigestResult(
            user_details=self._fetch_user_details(user_id=request.user_id)
        )

    def _fetch_user_details(self, user_id: str) -> UserDetailsResult:
        """Fetch detailed information about the user."""

        try:
            user_details: OCIResponse[UserGetResponse23V2] = self._dispatch(
                UserGetRequest23V2(user_id=user_id)
            )

            if isinstance(user_details, ErrorResponse):
                raise ValueError(
                    f"Failed to fetch user details for {user_id}: {user_details.summary}"
                )

            forwarding_details = self._fetch_forwarding_details(user_id=user_id)

            dnd_response = self._dispatch(UserDoNotDisturbGetRequest(user_id=user_id))

            if isinstance(dnd_response, ErrorResponse):
                raise ValueError(
                    f"Failed to fetch DND status for {user_id}: {dnd_response.summary}"
                )

            device_details = self._fetch_device_details(user_id=user_id)

        except Exception as e:
            raise ValueError(f"Error fetching user details for {user_id}: {e}")

        return UserDetailsResult(
            user_info=cast(UserGetResponse23V2, user_details),
            forwards=forwarding_details,
            dnd_status=dnd_response.is_active
            if not isinstance(dnd_response, (ErrorResponse, SuccessResponse))
            else None,
            regstered_devices={
                device.device_name: device.activation_status
                for device in device_details
            },
        )

    def _fetch_forwarding_details(self, user_id: str) -> list[ForwardingDetails]:
        """Fetch call forwarding settings for the user."""

        user_forwarding_requests = [
            UserCallForwardingAlwaysGetRequest(user_id=user_id),
            UserCallForwardingBusyGetRequest(user_id=user_id),
            UserCallForwardingNoAnswerGetRequest13mp16(user_id=user_id),
            UserCallForwardingNotReachableGetRequest(user_id=user_id),
            UserCallForwardingSelectiveGetRequest16(user_id=user_id),
        ]

        for forwarding_request in user_forwarding_requests:
            try:
                forwarding_response = self._dispatch(forwarding_request)
            except Exception as e:
                print(f"Error fetching forwarding details for {user_id}: {e}")
                continue

            if isinstance(forwarding_response, ErrorResponse) or isinstance(
                forwarding_response, SuccessResponse
            ):
                continue

            if isinstance(
                forwarding_response, UserCallForwardingSelectiveGetResponse16
            ):
                self.forwarding_details.append(
                    ForwardingDetails(
                        is_active=forwarding_response.is_active,
                        selective_criteria=forwarding_response.criteria_table,
                    )
                )
            else:
                self.forwarding_details.append(
                    ForwardingDetails(
                        is_active=forwarding_response.is_active,
                        forward_to_phone_number=forwarding_response.forward_to_phone_number,
                    )
                )

        return self.forwarding_details

    def _fetch_device_details(self, user_id: str) -> list[DeviceDetails]:
        """Fetch registered device details for the user."""

        device_details: OCIResponse[UserAccessDeviceDeviceActivationGetListResponse] = (
            self._dispatch(
                UserAccessDeviceDeviceActivationGetListRequest(user_id=user_id)
            )
        )

        device_details_list = []

        if isinstance(device_details, ErrorResponse) or isinstance(
            device_details, SuccessResponse
        ):
            return device_details_list

        for device in device_details.access_device_table.to_dict():
            device_name = device.get("device_name", "Unknown Device")
            device_type = device.get("device_type", "Unknown Type")
            line_port = device.get("line_port", "Unknown Line Port")
            activation_status = device.get("activation_status", "Unknown Status")

            device_details_list.append(
                DeviceDetails(
                    device_name=device_name,
                    device_type=device_type,
                    line_port=line_port,
                    activation_status=activation_status,
                )
            )

        return device_details_list
