from typing import Union, TypeVar
from mercury_ocip.commands.base_command import (
    ErrorResponse,
    SuccessResponse,
    OCIDataResponse,
    OCIRequest,
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
    "CommandInput",
    "CommandResult",
]

# What Client Sends
type CommandInput = OCIRequest

# What it Receives - runtime could be any response type
type CommandResult = Union[ErrorResponse, SuccessResponse, OCIDataResponse, None]
