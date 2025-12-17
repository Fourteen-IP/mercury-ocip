from typing import Union, TypeVar
from mercury_ocip.commands.base_command import (
    ErrorResponse,
    SuccessResponse,
    OCIDataResponse,
    OCICommand,
)
from mercury_ocip.libs.basic_types import (
    RequestResult,
    ConnectResult,
    DisconnectResult,
    XMLDictResult,
)

__all__ = [
    "RequestResult",
    "ConnectResult",
    "DisconnectResult",
    "XMLDictResult",
    "OCIResponse",
    "CommandInput",
    "CommandResult",
]

T = TypeVar("T", bound=OCIDataResponse)

# Generic response type
type OCIResponse[T] = Union[ErrorResponse, SuccessResponse, T]

# What client.command() accepts and returns
type CommandInput = OCICommand
type CommandResult = Union[OCIResponse, None]
