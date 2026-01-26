import attr
import sys
import logging
import hashlib
import uuid
from typing import Dict, Type, Union
import inspect
from abc import ABC, abstractmethod
import importlib

from mercury_ocip.commands import commands
from mercury_ocip.commands.base_command import OCICommand as BWKSCommand
from mercury_ocip.commands.base_command import OCIType as BWKSType
from mercury_ocip.commands.base_command import ErrorResponse as BWKSErrorResponse
from mercury_ocip.commands.base_command import SuccessResponse as BWKSSucessResponse
from mercury_ocip.requester import (
    create_requester,
    BaseRequester,
    SyncSOAPRequester,
    SyncTCPRequester,
)
from mercury_ocip.exceptions import MError
from mercury_ocip.utils.parser import Parser
from mercury_ocip.libs.types import (
    RequestResult,
    XMLDictResult,
    CommandInput,
    CommandResult,
)

type ClientResult = Union[None, BWKSCommand]  # Inlined To Prevent Circular Definition


@attr.s(slots=True, kw_only=True)
class BaseClient(ABC):
    """Base class for all clients
    - Host: The host of the server
    - Username: The username of the user
    - Password: The password of the user
    - Conn_type: The type of connection to the server
    - User_agent: The user agent of the client
    - Timeout: The timeout of the client
    - Logger: The logger of the client
    - Log_level: The log level for the default logger (default is WARNING)
    - Authenticated: Whether the client is authenticated
    - Session_id: The session id of the client
    - Dispatch_table: The dispatch table of the client
    """

    host: str = attr.ib()
    username: str = attr.ib()
    password: str = attr.ib()
    port: int = attr.ib(default=2209)
    conn_type: str = attr.ib(default="TCP")
    user_agent: str = attr.ib(default="Broadworks SDK")
    timeout: int = attr.ib(default=30)
    logger: logging.Logger = attr.ib(default=None)
    log_level: int = attr.ib(default=logging.WARNING)
    authenticated: bool = attr.ib(default=False)
    session_id: str = attr.ib(default=str(uuid.uuid4()))
    tls: bool = attr.ib(default=True)

    _dispatch_table: Dict[str, Type[BWKSCommand]] = attr.ib(default=None)
    _type_table: Dict[str, Type[BWKSType]] = attr.ib(default=None)
    _requester: BaseRequester = attr.ib(default=None)

    def __attrs_post_init__(self):
        if self.conn_type not in ["TCP", "SOAP"]:
            raise ValueError(
                f"conn_type must be 'TCP' or 'SOAP', got '{self.conn_type}'"
            )

        self._set_up_dispatch_table()
        self.logger = self.logger or self._set_up_logging()
        self.plugins: list[importlib.ModuleType] = []
        self._requester = create_requester(
            conn_type=self.conn_type,
            host=self.host,
            port=self.port,
            timeout=self.timeout,
            logger=self.logger,
            session_id=self.session_id,
            tls=self.tls,
        )
        if not self.async_mode:
            self.authenticate()

    @property
    @abstractmethod
    def async_mode(self) -> bool:
        """Whether the client is in async mode"""
        pass

    @abstractmethod
    def command(self, command: CommandInput) -> CommandResult:
        """Executes command class from .commands lib"""
        pass

    @abstractmethod
    def raw_command(self, command: str, **kwargs: str) -> CommandResult:
        """Executes raw command specified by end user - instantiates class command"""
        pass

    @abstractmethod
    def authenticate(
        self,
    ) -> CommandResult:
        """Authenticates client with username and password in client"""
        pass

    @abstractmethod
    def _receive_response(self, response: RequestResult) -> CommandResult:
        """Receives response from requester and returns BWKSCommand"""
        pass

    def disconnect(self) -> None:
        """Disconnects from the server

        Call this method at the end of your program to disconnect from the server.
        """
        pass

    def _set_up_dispatch_table(self):
        """Set up the dispatch table for the client"""
        self._dispatch_table = {}

        # Add all OCI commands and types
        for module in [commands]:
            for _, cls in inspect.getmembers(module, inspect.isclass):
                self._dispatch_table[cls.__name__] = cls

        # manually append as we handle ErrorResponse & SucessResponse in base_command
        for cls in [BWKSErrorResponse, BWKSSucessResponse]:
            self._dispatch_table[cls.__name__] = cls

    def _set_up_logging(self):
        """Common logging setup for all clients"""
        logger = logging.getLogger(__name__)
        logger.setLevel(self.log_level)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        logger.addHandler(console_handler)
        return logger


class Client(BaseClient):
    """Connection to a BroadWorks server

    Args:
        host (str): URL or IP address of server. Depends on connection type. If SOAP DO NOT include '?wsdl' in the end of the URL.
        username (str): The username of the user
        password (str): The password of the user
        conn_type (str): Either 'TCP' or 'SOAP'. TCP is the default.

        port (int): The port of the server. Default is 2209. Only used in TCP mode.
        secure (bool): Whether the connection is secure. Default is True. Only used in TCP mode. Password is hashed if not secure.

        timeout (int): The timeout of the client. Default is 30 seconds.
        user_agent (str): The user agent of the client, used for logging. Default is 'Thor\'s Hammer'.
        logger (logging.Logger): The logger of the client. Default is None.
        log_level (int): The log level for the default logger. Default is logging.WARNING.

    Attributes:
        authenticated (bool): Whether the client is authenticated
        session_id (str): The session id of the client
        _dispatch_table (dict): The dispatch table of the client

    Raises:
        Exception: If the client fails to authenticate
    """

    _requester: Union[SyncTCPRequester, SyncSOAPRequester]  # type: ignore

    async def __enter__(self):
        self.authenticate()
        return self

    async def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        return False

    @property
    def async_mode(self) -> bool:
        return False

    def command(self, command: CommandInput) -> CommandResult:
        """
        Executes all requests to the server.
        If the client is not authenticated, it will authenticate first.

        Args:
            command (BWKSCommand): The command class to execute

        Returns:
            BWKSCommand: The response from the server
        """
        if not self.authenticated:
            self.authenticate()
        self.logger.info(f"Executing command: {command.__class__.__name__}")
        self.logger.debug(f"Command: {command.to_dict()}")
        response = self._requester.send_request(command.to_xml())
        return self._receive_response(response)

    def raw_command(self, command: str, **kwargs: str) -> CommandResult:
        """
        Executes raw command specified by end user - instantiates class command.

        Args:
            command (str): The command to execute
            **kwargs: The arguments to pass to the command

        Returns:
            BWKSCommand: The response from the server

        Raises:
            ValueError: If the command is not found in the dispatch table
        """
        command_class = self._dispatch_table.get(command)
        if not command_class:
            self.logger.error(f"Command {command} not found in dispatch table")
            raise ValueError(f"Command {command} not found in dispatch table")
        return self.command(command_class(**kwargs))

    def authenticate(self) -> CommandResult:
        """
        Authenticates client with username and password in client.

        Note: Directly send request to requester to avoid double authentication

        Returns:
            BWKSCommand: The response from the server

        Raises:
            THError: If the command is not found in the dispatch table
        """
        # If client is already authenticated, return
        if self.authenticated:
            return

        if self.session_id == "":
            self.session_id = str(uuid.uuid4())

        # Default to 22V5 login request - recommended
        if not (login_request_class := self._dispatch_table.get("LoginRequest22V5")):
            raise ValueError("LoginRequest22V5 not found in dispatch table")
        request = login_request_class(user_id=self.username, password=self.password)

        if not self.tls:
            # Hashing password needed when not over secure connection

            if not (auth_request := self._dispatch_table.get("AuthenticationRequest")):
                raise ValueError("AuthenticationRequest not found in dispatch table")

            auth_resp = self._receive_response(
                self._requester.send_request(
                    auth_request(user_id=self.username).to_xml()
                )
            )

            assert auth_resp is not None and hasattr(auth_resp, "nonce")

            authhash = hashlib.sha1(self.password.encode()).hexdigest().lower()
            signed_password = (
                hashlib.md5(":".join([auth_resp.nonce, authhash]).encode())  # type: ignore
                .hexdigest()
                .lower()
            )  # We can safely ignore the type here as we know auth_resp is a valid response with a nonce

            if not (
                login_request_class := self._dispatch_table.get("LoginRequest14sp4")
            ):
                raise ValueError("LoginRequest14sp4 not found in dispatch table")

            request = login_request_class(
                user_id=self.username, signed_password=signed_password
            )

        login_resp = self._receive_response(
            self._requester.send_request(request.to_xml())
        )

        if isinstance(login_resp, BWKSErrorResponse):
            raise MError(f"Failed to authenticate: {login_resp.summary}")

        self.logger.info("Authenticated with server")
        self.authenticated = True
        return login_resp

    def _receive_response(self, response: RequestResult) -> CommandResult:
        """Receives response from requester and returns BWKSCommand"""

        if isinstance(response, MError):
            raise response

        # Extract Typename From Raw Response
        response_dict: XMLDictResult = Parser.to_dict_from_xml(response)

        # Check if response_dict is a dict before accessing
        if not isinstance(response_dict, dict):
            raise MError("Failed to parse response object - invalid format")

        command_data = response_dict.get("command")

        if isinstance(command_data, dict):
            type_name: Union[str, None] = command_data.get("attributes", {}).get(
                "{http://www.w3.org/2001/XMLSchema-instance}type"
            )
        else:
            return BWKSSucessResponse()

        # Validate Typename Extraction
        if not type_name or not isinstance(type_name, str):
            raise MError("Failed to parse response object")

        # Remove Namespace From Typename
        if ":" in type_name:
            type_name = type_name.split(":", 1)[1]

        # Cache Response Class
        response_class = self._dispatch_table.get(type_name)

        # Validate Response Class Instantiation
        if not response_class:
            raise MError(f"Failed To Find Raw Response Type: {type_name}")

        # Construct Response Class With Raw Response
        self.logger.debug(f"Response -> {response_class}")
        return response_class.from_xml(response)  # type: ignore

    def disconnect(self):
        """Disconnects from the server

        Call this method at the end of your program to disconnect from the server.
        """
        self.authenticated = False
        self.session_id = ""
        self._requester.disconnect()
