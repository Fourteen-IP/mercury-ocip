from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, Optional, TypeVar, cast

from mercury_ocip.client import BaseClient
from mercury_ocip.utils.shared_operations import SharedOperations
from mercury_ocip.libs.types import OCIResponse
from mercury_ocip.commands.base_command import OCICommand, ErrorResponse
from mercury_ocip.exceptions import MErrorUnknown, MErrorResponse, MError

RequestT = TypeVar("RequestT")
PayloadT = TypeVar("PayloadT")


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
        self.logger = client.logger
        self.shared_ops = SharedOperations(client)

    def execute(self, request: RequestT) -> AutomationResult[PayloadT]:
        automation_name = self.__class__.__name__
        self.logger.info(f"Starting automation: {automation_name}")
        try:
            self._validate(request)
            self.logger.debug(f"Validation passed for {automation_name}")
            raw = self._run(request)
            self.logger.debug(f"Execution completed for {automation_name}")
            result = self._wrap(raw)
            self.logger.info(f"Automation {automation_name} completed successfully: {result.ok}")
            return result
        except Exception as e:
            self.logger.error(f"Automation {automation_name} failed: {str(e)}")
            raise

    def _validate(self, request: RequestT) -> None:
        """Optional quick checks before we hit the network."""
        return None

    @abstractmethod
    def _run(self, request: RequestT) -> PayloadT:
        """Do whatever the automation needs (single call, fan-out, aggregation, etc.)."""

    def _wrap(self, payload: PayloadT) -> AutomationResult[PayloadT]:
        """Standardise the outward result."""
        return AutomationResult(ok=payload is not None, payload=payload)

    def _dispatch(self, command: OCICommand) -> OCIResponse:
        """Send a single OCI command and normalise failures."""
        try:
            self.logger.debug(f"Dispatching command: {command.__class__.__name__}")
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
