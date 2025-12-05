"""
test async client
"""

import pytest
import logging
from unittest.mock import Mock, patch
import asyncio

from mercury_ocip.client import AsyncClient
from mercury_ocip.requester import AsyncTCPRequester
from mercury_ocip.utils.parser import Parser, AsyncParser
from mercury_ocip.commands.commands import (
    UserGetRegistrationListRequest,
    LoginRequest22V5,
    LoginRequest14sp4,
    AuthenticationRequest,
)
from mercury_ocip.commands.commands import (
    AuthenticationResponse,
    LoginResponse22V5,
    LoginResponse14sp4,
)
from mercury_ocip.commands.base_command import (
    ErrorResponse,
)


# Async Client Tests
@pytest.fixture
def mock_async_requester():
    """Mock async requester that behaves like the real thing"""
    mock_req = Mock(spec=AsyncTCPRequester)

    async def mock_send_request(command):
        # Await the coroutine to get the actual XML string
        if asyncio.iscoroutine(command):
            command = await command

        # Same logic as sync version but async
        if "LoginRequest22V5" in command:
            return "LoginResponse22V5"
        elif "AuthenticationRequest" in command:
            return "AuthenticationResponse"
        elif "LoginRequest14sp4" in command:
            return "LoginResponse14sp4"
        elif "ErrorResponse" in command:
            return "ErrorResponse"
        elif "UserGetRegistrationListRequest" in command:
            return "UserGetRegistrationListResponse"
        else:
            return "SuccessResponse"

    mock_req.send_request = Mock(side_effect=mock_send_request)
    mock_req.disconnect = Mock()
    return mock_req


@pytest.fixture
def mock_create_async_requester(mock_async_requester):
    """Mock the create_requester factory function for async"""
    with patch(
        "mercury_ocip.client.create_requester", return_value=mock_async_requester
    ) as mock:
        yield mock


@pytest.fixture
def mock_async_parser():
    """Mock async parser that behaves like the real thing"""
    with (
        patch("mercury_ocip.client.AsyncParser.to_dict_from_xml") as mock_dict,
        patch("mercury_ocip.client.AsyncParser.to_class_from_xml") as mock_class,
        patch("mercury_ocip.client.AsyncParser.to_xml_from_class") as mock_cls_to_xml,
    ):

        async def mock_to_dict_from_xml(xml_string):
            if "LoginResponse22V5" in xml_string:
                return {
                    "command": {
                        "attributes": {
                            "{http://www.w3.org/2001/XMLSchema-instance}type": "LoginResponse22V5"
                        }
                    }
                }
            if "LoginResponse14sp4" in xml_string:
                return {
                    "command": {
                        "attributes": {
                            "{http://www.w3.org/2001/XMLSchema-instance}type": "LoginResponse14sp4"
                        }
                    }
                }
            if "AuthenticationResponse" in xml_string:
                return {
                    "command": {
                        "attributes": {
                            "{http://www.w3.org/2001/XMLSchema-instance}type": "AuthenticationResponse"
                        }
                    }
                }

        async def mock_to_class_from_xml(xml_string, cls):
            if "LoginResponse22V5" in xml_string:
                return LoginResponse22V5
            if "LoginResponse14sp4" in xml_string:
                return LoginResponse14sp4
            if "AuthenticationResponse" in xml_string:
                return AuthenticationResponse(
                    nonce="12345678910",
                    user_id="user",
                    password_algorithm="MD5",
                )
            return ErrorResponse

        async def mock_to_xml_from_class(cls):
            if isinstance(cls, LoginRequest22V5):
                return "LoginRequest22V5"
            if isinstance(cls, LoginRequest14sp4):
                return "LoginRequest14sp4"
            if isinstance(cls, AuthenticationRequest):
                return "AuthenticationRequest"
            if isinstance(cls, UserGetRegistrationListRequest):
                return "UserGetRegistrationListRequest"
            return "SuccessResponse"

        mock_dict.side_effect = mock_to_dict_from_xml
        mock_class.side_effect = mock_to_class_from_xml
        mock_cls_to_xml.side_effect = mock_to_xml_from_class
        yield mock_dict, mock_class, mock_cls_to_xml


@pytest.fixture
def mock_async_authenticate():
    """Mock the async authenticate method to prevent actual authentication"""
    with patch("mercury_ocip.client.AsyncClient.authenticate") as mock:
        yield mock


@pytest.fixture
def mock_async_receive_response():
    """Mock the async receive response method"""
    with patch("mercury_ocip.client.AsyncClient._receive_response") as mock_receive:

        async def mock_receive_response(response):
            if "UserGetRegistrationListResponse" in response:
                return "UserGetRegistrationListResponse"

            # Return an instance of ErrorResponse with a summary attribute
            return_response = ErrorResponse(
                summary="Authentication failed",
                summaryEnglish="Authentication failed",
                detail="Invalid credentials kahdljahsd",
                errorCode=100,
            )

            return return_response

        mock_receive.side_effect = mock_receive_response
        yield mock_receive


class TestAsyncClient:
    def test_async_client_initialises_with_defaults(
        self,
        mock_dispatch_table,
        mock_create_async_requester,
        mock_async_parser,
        mock_async_authenticate,
    ):
        """Test the async client initialises with defaults"""

        client = AsyncClient(host="localhost", username="user", password="pass")

        assert client.host == "localhost"
        assert client.username == "user"
        assert client.password == "pass"
        assert client.port == 2209
        assert client.conn_type == "TCP"
        assert client.user_agent == "Broadworks SDK"
        assert client.timeout == 30
        assert isinstance(client.logger, logging.Logger)
        assert client.authenticated is False
        assert client.session_id is not None
        assert client.tls is True
        assert client.async_mode is True

    @pytest.mark.asyncio
    async def test_authentication_success_with_tls(
        self, mock_create_async_requester, mock_dispatch_table, mock_async_parser
    ):
        """Test the client authenticates successfully with TLS"""
        client = AsyncClient(host="localhost", username="user", password="pass")
        await client.authenticate()

        assert client.authenticated is True
        assert client.session_id is not None

        mock_requester = mock_create_async_requester.return_value
        mock_requester.send_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_authentication_success_without_tls(
        self,
        mock_create_async_requester,
        mock_dispatch_table,
        mock_async_parser,
    ):
        """Test the client authenticates successfully without TLS"""
        client = AsyncClient(
            host="localhost", username="user", password="pass", tls=False
        )
        await client.authenticate()
        assert client.authenticated is True
        assert client.session_id is not None

    @pytest.mark.asyncio
    async def test_async_command_flow(
        self,
        mock_create_async_requester,
        mock_dispatch_table,
        mock_async_parser,
        mock_async_authenticate,
        mock_async_receive_response,
    ):
        """Test the complete async command method flow"""

        client = AsyncClient(host="localhost", username="user", password="pass")
        client.authenticated = True

        command = UserGetRegistrationListRequest(user_id="example_user")
        response = await client.command(command)

        assert response == "UserGetRegistrationListResponse"

    @pytest.mark.asyncio
    async def test_async_raw_command_flow(
        self,
        mock_create_async_requester,
        mock_dispatch_table,
        mock_async_parser,
        mock_async_authenticate,
        mock_async_receive_response,
    ):
        """Test the complete async command method flow"""

        client = AsyncClient(host="localhost", username="user", password="pass")
        client.authenticated = True

        response = await client.raw_command(
            "UserGetRegistrationListRequest", user_id="example_user"
        )

        assert response == "UserGetRegistrationListResponse"
