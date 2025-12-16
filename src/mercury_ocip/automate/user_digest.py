from typing import cast, Optional, TypeVar, Union
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
    UserGetRegistrationListRequest,
    UserGetRegistrationListResponse,
    UserCallCenterGetRequest23,
    UserCallCenterGetResponse23,
)
from mercury_ocip.libs.types import OCIResponse
from mercury_ocip.commands.base_command import ErrorResponse, SuccessResponse, OCITable
from mercury_ocip.utils.defines import to_snake_case

T = TypeVar("T")


@dataclass(slots=True)
class UserDigestRequest:
    user_id: str


@dataclass(slots=True)
class ForwardingDetails:
    variant: str
    is_active: bool
    forward_to_phone_number: Optional[str] = None
    selective_criteria: Optional[OCITable] = None


@dataclass(slots=True)
class DeviceDetails:
    device_name: str
    endpoint_type: str
    line_port: str


@dataclass(slots=True)
class UserDetailsResult:
    user_info: Optional[UserGetResponse23V2] = None
    forwards: list[ForwardingDetails] = field(default_factory=list)
    dnd_status: Optional[bool] = None
    registered_devices: list[DeviceDetails] = field(default_factory=list)


@dataclass(slots=True)
class CallCentreDetails:
    call_center_id: str
    call_center_name: str
    call_center_type: str
    agent_acd_state: str | None = None
    agent_cc_available: str | None = None


@dataclass(slots=True)
class HuntGroupDetails:
    hunt_group_id: str
    hunt_group_name: str
    extension: str | None = None
    hunt_group_busy: bool = False


@dataclass(slots=True)
class CallPickupGroupDetails:
    call_pickup_group_id: str
    call_pickup_group_name: str


@dataclass(slots=True)
class UserDigestResult:
    user_details: Optional[UserDetailsResult] = None
    call_center_membership: Optional[list[CallCentreDetails]] = None
    hunt_group_membership: Optional[list[HuntGroupDetails]] = None
    call_pickup_group_membership: Optional[list[CallPickupGroupDetails]] = None


class UserDigest(BaseAutomation):
    """Automation to generate a digest of user information."""

    def __init__(self, client: BaseClient) -> None:
        super().__init__(client)
        self.forwarding_details = []
        self.user_details: Optional[UserDetailsResult] = None

    def _run(self, request: UserDigestRequest) -> UserDigestResult:
        """
        Execute the user digest automation.

        Collects and summarizes user information based on the provided request.

        Args:
            request: Contains parameters for generating the user digest.

        Returns:
            UserDigestResult containing the summarized user information.
        """
        self.user_details = self._fetch_user_details(
            user_id=request.user_id
        )  # We need to use this for service_provider_id/group_id later

        return UserDigestResult(
            user_details=self.user_details,
            call_center_membership=self._fetch_call_center_membership(
                user_id=request.user_id
            ),
            hunt_group_membership=self._fetch_hunt_group_membership(
                user_id=request.user_id
            ),
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
            registered_devices=device_details,
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

            forwarding_variant = to_snake_case(
                type(forwarding_request)
                .__name__.removeprefix("UserCallForwarding")
                .removesuffix("13mp16")
                .removesuffix("GetRequest")
            )

            if isinstance(
                forwarding_response, UserCallForwardingSelectiveGetResponse16
            ):
                self.forwarding_details.append(
                    ForwardingDetails(
                        variant="Selective",
                        is_active=forwarding_response.is_active,
                        selective_criteria=forwarding_response.criteria_table,
                    )
                )
            else:
                self.forwarding_details.append(
                    ForwardingDetails(
                        variant=forwarding_variant,
                        is_active=forwarding_response.is_active,
                        forward_to_phone_number=forwarding_response.forward_to_phone_number,
                    )
                )

        return self.forwarding_details

    def _fetch_device_details(self, user_id: str) -> list[DeviceDetails]:
        """Fetch registered device details for the user."""

        device_details_list = []

        try:
            device_details: OCIResponse[UserGetRegistrationListResponse] = (
                self._dispatch(UserGetRegistrationListRequest(user_id=user_id))
            )

        except Exception as e:
            print(f"Error fetching device details for {user_id}: {e}")
            return []

        if isinstance(device_details, ErrorResponse) or isinstance(
            device_details, SuccessResponse
        ):
            return device_details_list

        device_table = device_details.registration_table.to_dict()

        if len(device_table) == 0:
            return device_details_list

        for device in device_table:
            device_name = device.get("device_name", "Unknown Device")
            endpoint_type = device.get("endpoint_type", "Unknown Type")
            line_port = device.get("line/port", "No Active Line Port")

            device_details_list.append(
                DeviceDetails(
                    device_name=device_name,
                    endpoint_type=endpoint_type,
                    line_port=line_port,
                )
            )

        return device_details_list

    def _fetch_call_center_membership(self, user_id: str) -> list[CallCentreDetails]:
        """Fetch call center membership details for the user."""

        call_center_list = []

        try:
            cc_response: OCIResponse[UserCallCenterGetResponse23] = self._dispatch(
                UserCallCenterGetRequest23(user_id=user_id)
            )

            if isinstance(cc_response, ErrorResponse) or isinstance(
                cc_response, SuccessResponse
            ):
                return []

            cc_table = cc_response.call_center_table.to_dict()

            if len(cc_table) == 0:
                return []

            for call_center in cc_table:
                call_center_id = call_center.get("service_user_id", "Unknown ID")
                call_center_name = call_center.get("service_instance_profile", {}).get(
                    "name", "Unknown Name"
                )
                call_center_type = call_center.get("type", "Unknown Type")
                agent_available_level = call_center.get("available", "")

                call_center_list.append(
                    CallCentreDetails(
                        call_center_id=call_center_id,
                        call_center_name=call_center_name,
                        call_center_type=call_center_type,
                        agent_cc_available=agent_available_level,
                        agent_acd_state=cc_response.agent_acd_state,
                    )
                )

        except Exception as e:
            print(f"Error fetching call center membership for {user_id}: {e}")
            return []

        return call_center_list

    def _fetch_hunt_group_membership(self, user_id: str) -> list[HuntGroupDetails]:
        """Fetch hunt group membership details for the user."""

        try:
            if not self.user_details or not self.user_details.user_info:
                raise ValueError("User details not loaded.")

            service_provider_id = self.user_details.user_info.service_provider_id
            group_id = self.user_details.user_info.group_id

            hunt_group_response = self.shared_ops.fetch_hunt_group_details(
                service_provider_id=service_provider_id, group_id=group_id
            )

            hunt_group_list = []

            for hunt_group in hunt_group_response:
                hunt_group = self._clean_response(hunt_group)

                hunt_group_id = hunt_group.get("service_user_id", "")

                for agent in detailed_hunt_group.agent_user_table.to_dict():
                    if agent.get("user_id") == user_id:
                        hunt_group_list.append(
                            HuntGroupDetails(
                                hunt_group_id=hunt_group_id,
                                hunt_group_name=detailed_hunt_group.service_instance_profile.name,
                                extension=detailed_hunt_group.service_instance_profile.extension,
                                hunt_group_busy=detailed_hunt_group.enable_group_busy,
                            )
                        )
        except Exception as e:
            print(f"Error fetching hunt group membership for {user_id}: {e}")
            return []
        return hunt_group_list

    def _clean_response(self, response: OCIResponse[T]) -> T:
        """Cleans the response object by removing non relevant potential types."""
        if isinstance(response, ErrorResponse):
            raise ValueError(f"Error in response: {response.summary}")
        if isinstance(response, SuccessResponse):
            raise ValueError("Received a success response without data.")
        return response
