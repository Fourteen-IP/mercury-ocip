from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, Optional, TypeVar, cast

from mercury_ocip.client import BaseClient
from mercury_ocip.utils.shared_operations import SharedOperations
from mercury_ocip.commands.base_command import OCIRequest, OCIResponse, ErrorResponse
from mercury_ocip.exceptions import MErrorUnknown, MErrorResponse, MError

RequestT = TypeVar("RequestT")
PayloadT = TypeVar("PayloadT")
ResponseT = TypeVar("ResponseT", bound=OCIResponse)


@dataclass(slots=True)
class AutomationResult(Generic[PayloadT]):
    ok: bool = True
    payload: Optional[PayloadT] = None
    message: str = "Successful."
    notes: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.notes is None:
            self.notes: dict[str, Any] = {}


class BaseAutomation(ABC, Generic[RequestT, PayloadT]):
    """Minimal contract all automations follow."""

    def __init__(self, client: BaseClient) -> None:
        self.client = client
        self.shared_ops = SharedOperations(client)

    def execute(self, request: RequestT) -> AutomationResult[PayloadT]:
        self._validate(request)
        raw = self._run(request)
        return self._wrap(raw)

    def _validate(self, request: RequestT) -> None:
        """Optional quick checks before we hit the network."""
        return None

    @abstractmethod
    def _run(self, request: RequestT) -> PayloadT:
        """Do whatever the automation needs (single call, fan-out, aggregation, etc.)."""

    def _wrap(self, payload: PayloadT) -> AutomationResult[PayloadT]:
        """Standardise the outward result."""
        return AutomationResult(ok=payload is not None, payload=payload)

    def _dispatch(self, command: OCIRequest) -> OCIResponse:
        """Send a single OCI command and normalise failures."""
        try:
            response = self.client.command(command)
        except MError:
            raise  # upstream already wrapped it correctly
        except Exception as exc:
            raise MErrorUnknown(
                message=f"{command.__class__.__name__} failed unexpectedly",
                context=exc,
            )

        if response is None:
            raise MErrorUnknown(
                message=f"{command.__class__.__name__} returned no payload",
                context=None,
            )

        if isinstance(response, ErrorResponse):
            raise MErrorResponse(
                message=response.summary,
                context=response.detail,
            )

        return cast(OCIResponse, response)

    def _dispatch_cast(
        self, command: OCIRequest, response_type: type[ResponseT]
    ) -> ResponseT:
        """
        Dispatch and cast the response to the expected type.

        Args:
            command: The OCI request to send
            response_type: The expected response type class

        Returns:
            The response cast to ResponseT with full IntelliSense

        Example:
            user_info = self._dispatch_cast(
                UserGetRequest23V2(user_id="user"),
                UserGetResponse23V2
            )
        """
        response = self._dispatch(command)
        return cast(ResponseT, response)
