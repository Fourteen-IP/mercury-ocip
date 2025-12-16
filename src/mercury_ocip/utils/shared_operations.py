from collections.abc import Callable, Iterable, Mapping
from typing import TypeVar, cast, List

from mercury_ocip.commands.base_command import OCICommand, ErrorResponse
from mercury_ocip.commands.commands import (
    GroupHuntGroupGetInstanceListResponse,
    UserGetListInGroupResponse,
    GroupCallCenterGetInstanceListResponse,
    GroupAutoAttendantGetInstanceListResponse,
    GroupHuntGroupGetInstanceResponse20,
    GroupCallCenterGetInstanceResponse22,
    GroupAutoAttendantGetInstanceResponse24,
)
from mercury_ocip.client import BaseClient
from mercury_ocip.libs.types import OCIResponse
from mercury_ocip.exceptions import MErrorResponse

SummaryResponse = TypeVar("SummaryResponse", bound=OCIResponse)


class SharedOperations:
    """Shared operations used in automations.

    This class holds commen functionality such as fetching all users from a group.

    These operations are used heavily in auatomations so reduce duplicated code they have been
    stored here.
    """

    def __init__(self, client: BaseClient) -> None:
        self.client = client

    def fetch_group_users(self, **kwargs) -> OCIResponse | None:
        """Get all users in a specific group.

        Args:
            **kwargs: Keyword args of the data class GroupUserGetListInGroupRequest22 command.

        Raises:
            TypeError: If mandatory values are not supplied the class from the command will raise and error.
            ValueError: If the command GroupUserGetListInGroupRequest22 is not found in the dispatch table

        Returns:
            OCIReponse: The command to get the users in the group
        """

        cmd = "UserGetListInGroupRequest"
        return self._execute_command(command_name=cmd, **kwargs)

    def fetch_user_details(
        self, service_provider_id: str, group_id: str
    ) -> List[OCIResponse[UserGetListInGroupResponse]]:
        """Get all users in a specific group.

        This differs to group_users as the response is a list of detailed objects including all
        user data where the other only includes high-level data.

        Args:
            **kwargs: Keyword args of the data class UserGetRequest23V2 command.

        Raises:
            TypeError: If mandatory values are not supplied the class from the command will raise and error.
            ValueError: If the command UserGetRequest23V2 is not found in the dispatch table

        Returns:
            OCIReponse: The command to get the users in the group
        """
        return self._collect_detail_responses(
            summary_fetcher=self.fetch_group_users,
            summary_kwargs={
                "service_provider_id": service_provider_id,
                "group_id": group_id,
            },
            summary_type=UserGetListInGroupResponse,
            table_attr="user_table",
            id_field="user_id",
            detail_command="UserGetRequest23V2",
        )

    def fetch_group_hunt_groups(self, **kwargs) -> OCIResponse | None:
        """Get all hunt groups in a specific group.

        Args:
            **kwargs: Keyword args of the data class GroupHuntGroupGetInstanceListRequest command.

        Raises:
            TypeError: If mandatory values are not supplied the class from the command will raise and error.
            ValueError: If the command GroupHuntGroupGetInstanceListRequest is not found in the dispatch table

        Returns:
            OCIReponse: The command to get the users in the group
        """

        cmd = "GroupHuntGroupGetInstanceListRequest"
        return self._execute_command(command_name=cmd, **kwargs)

    def fetch_hunt_group_details(
        self, service_provider_id: str, group_id: str
    ) -> List[OCIResponse[GroupHuntGroupGetInstanceResponse20]]:
        """Get all hunt groups in a specific group.

        This differs to group_hunt_groups as the response is a list of detailed objects including all
        hunt group data where the other only includes high-level data.

        Args:
            **kwargs: Keyword args of the data class GroupHuntGroupGetInstanceRequest20 command.

        Raises:
            TypeError: If mandatory values are not supplied the class from the command will raise and error.
            ValueError: If the command GroupHuntGroupGetInstanceRequest20 is not found in the dispatch table

        Returns:
            OCIReponse: The command to get the users in the group
        """
        return self._collect_detail_responses(
            summary_fetcher=self.fetch_group_hunt_groups,
            summary_kwargs={
                "service_provider_id": service_provider_id,
                "group_id": group_id,
            },
            summary_type=GroupHuntGroupGetInstanceListResponse,
            table_attr="hunt_group_table",
            id_field="service_user_id",
            detail_command="GroupHuntGroupGetInstanceRequest20",
        )

    def fetch_group_call_centers(self, **kwargs) -> OCIResponse | None:
        """Get all call centers in a specific group.

        Args:
            **kwargs: Keyword args of the data class GroupCallCenterGetInstanceListRequest command.

        Raises:
            TypeError: If mandatory values are not supplied the class from the command will raise and error.
            ValueError: If the command GroupCallCenterGetInstanceListRequest is not found in the dispatch table

        Returns:
            OCIReponse: The command to get the users in the group
        """

        cmd = "GroupCallCenterGetInstanceListRequest"
        return self._execute_command(command_name=cmd, **kwargs)

    def fetch_call_center_details(
        self, service_provider_id: str, group_id: str
    ) -> List[OCIResponse[GroupCallCenterGetInstanceResponse22]]:
        """Get all call centers in a specific group.

        This differs to group_call_centers as the response is a list of detailed objects including all
        call centers data where the other only includes high-level data.

        Args:
            **kwargs: Keyword args of the data class GroupCallCenterGetRequest23 command.

        Raises:
            TypeError: If mandatory values are not supplied the class from the command will raise and error.
            ValueError: If the command GroupCallCenterGetRequest23 is not found in the dispatch table

        Returns:
            OCIReponse: The command to get the users in the group
        """
        return self._collect_detail_responses(
            summary_fetcher=self.fetch_group_call_centers,
            summary_kwargs={
                "service_provider_id": service_provider_id,
                "group_id": group_id,
            },
            summary_type=GroupCallCenterGetInstanceListResponse,
            table_attr="call_center_table",
            id_field="service_user_id",
            detail_command="GroupCallCenterGetInstanceRequest22",
        )

    def fetch_group_auto_attendants(self, **kwargs) -> OCIResponse | None:
        """Get all call centers in a specific group.

        Args:
            **kwargs: Keyword args of the data class GroupAutoAttendantGetInstanceListRequest command.

        Raises:
            TypeError: If mandatory values are not supplied the class from the command will raise and error.
            ValueError: If the command GroupAutoAttendantGetInstanceListRequest is not found in the dispatch table

        Returns:
            OCIReponse: The command to get the users in the group
        """

        cmd = "GroupAutoAttendantGetInstanceListRequest"
        return self._execute_command(command_name=cmd, **kwargs)

    def fetch_auto_attendant_details(
        self, service_provider_id: str, group_id: str
    ) -> List[OCIResponse[GroupAutoAttendantGetInstanceResponse24]]:
        """Get all auto attendants in a specific group.

        This differs to group_auto_attendants as the response is a list of detailed objects including all
        call centers data where the other only includes high-level data.

        Args:
            **kwargs: Keyword args of the data class GroupAutoAttendantGetInstanceRequest24 command.

        Raises:
            TypeError: If mandatory values are not supplied the class from the command will raise and error.
            ValueError: If the command GroupAutoAttendantGetInstanceRequest24 is not found in the dispatch table

        Returns:
            OCIReponse: The command to get the users in the group
        """
        return self._collect_detail_responses(
            summary_fetcher=self.fetch_group_auto_attendants,
            summary_kwargs={
                "service_provider_id": service_provider_id,
                "group_id": group_id,
            },
            summary_type=GroupAutoAttendantGetInstanceListResponse,
            table_attr="auto_attendant_table",
            id_field="service_user_id",
            detail_command="GroupAutoAttendantGetInstanceRequest24",
        )

    def _collect_detail_responses(
        self,
        *,
        summary_fetcher: Callable[..., OCIResponse | ErrorResponse | None],
        summary_kwargs: dict[str, object],
        summary_type: type[SummaryResponse] | None,
        table_attr: str,
        id_field: str,
        detail_command: str,
        payload_builder: Callable[[Mapping[str, object]], dict[str, object]]
        | None = None,
    ) -> List[OCIResponse]:
        summary = summary_fetcher(**summary_kwargs)
        if summary is None:
            return []
        if isinstance(summary, ErrorResponse):
            raise MErrorResponse(message=summary.summary, context=summary.detail)
        if summary_type is not None and not isinstance(summary, summary_type):
            raise TypeError(
                f"Unexpected summary response type: {type(summary).__name__} (expected {summary_type})"
            )
        typed_summary: SummaryResponse = cast(SummaryResponse, summary)

        results: List[OCIResponse] = []
        rows: Iterable[Mapping[str, object]] = getattr(typed_summary, table_attr, [])
        rows = rows.to_dict() if hasattr(rows, "to_dict") else rows
        for row in rows:
            identifier = row.get(id_field)
            if identifier is None:
                continue
            payload = (
                payload_builder(row)
                if payload_builder is not None
                else {id_field: identifier}
            )
            response = self._execute_command(detail_command, **payload)
            if response is not None:
                current_value = getattr(response, id_field, None)
                if current_value is None:
                    setattr(response, id_field, identifier)
                results.append(response)
        return results

    def _get_command(self, command_name: str) -> type[OCICommand]:
        command_factory: type[OCICommand] | None = self.client._dispatch_table.get(
            command_name
        )
        if command_factory is None:
            raise ValueError(f"Command {command_name} not found in dispatch table.")
        return command_factory

    def _execute_command(self, command_name: str, **kwargs) -> OCIResponse | None:
        cmd: type[OCICommand] = self._get_command(command_name)
        return cast(OCIResponse | None, self.client.command(cmd(**kwargs)))
