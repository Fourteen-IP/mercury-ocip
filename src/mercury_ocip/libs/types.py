from typing import Union
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

# Response types from OCI
type OCIResponse = Union[ErrorResponse, SuccessResponse, OCIDataResponse]

# What client.command() accepts and returns
type CommandInput = OCICommand
type CommandResult = Union[OCIResponse, None]
