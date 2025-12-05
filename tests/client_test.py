import pytest
import logging
from unittest.mock import Mock, patch

from mercury_ocip.client import Client
from mercury_ocip.requester import SyncTCPRequester
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


@pytest.fixture
def mock_requester():
    """Mock requester that behaves like the real thing"""
    mock_req = Mock(spec=SyncTCPRequester)

    def mock_send_request(command):
        # Determine response based on command type
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

    mock_req.send_request.side_effect = mock_send_request
    mock_req.disconnect = Mock()
    return mock_req


@pytest.fixture
def mock_create_requester(mock_requester):
    """Mock the create_requester factory function"""
    with patch(
        "mercury_ocip.client.create_requester", return_value=mock_requester
    ) as mock:
        yield mock


@pytest.fixture
def mock_parser():
    """Mock parser that behaves like the real thing"""
    with (
        patch("mercury_ocip.client.Parser.to_dict_from_xml") as mock_dict,
        patch("mercury_ocip.client.Parser.to_class_from_xml") as mock_class,
        patch("mercury_ocip.client.Parser.to_xml_from_class") as mock_cls_to_xml,
    ):

        def mock_to_dict_from_xml(xml_string):
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

        def mock_to_class_from_xml(xml_string, cls):
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

        def mock_to_xml_from_class(cls):
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
def mock_authenticate():
    """Mock the authenticate method to prevent actual authentication"""
    with patch("mercury_ocip.client.Client.authenticate") as mock:
        yield mock


@pytest.fixture
def mock_receive_response():
    """Mock the receive response method to prevent actual response

    Used to simulate auth failure
    """
    with patch("mercury_ocip.client.Client._receive_response") as mock_receive:
        def mock_receive_response(response):
            if "UserGetRegistrationListResponse" in response:
                return "UserGetRegistrationListResponse"
            # Return an instance of ErrorResponse with a summary attribute
            return_response = ErrorResponse(
                summary="Authentication failed",
                summary_english="Authentication failed",
                detail="Invalid credentials kahdljahsd",
                error_code=100,
            )

            return return_response

        mock_receive.side_effect = mock_receive_response
        yield mock_receive


class TestClient:
    def test_client_initialises_with_defaults(
        self, mock_dispatch_table, mock_create_requester, mock_parser, mock_authenticate
    ):
        """Test the client initialises with defaults"""
        client = Client(host="localhost", username="user", password="pass")

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

        # Verify requester was created correctly
        mock_create_requester.assert_called_once_with(
            conn_type="TCP",
            async_=False,
            host="localhost",
            port=2209,
            timeout=30,
            logger=client.logger,
            session_id=client.session_id,
            tls=True,
        )
        assert client.async_mode is False

    def test_authentication_success_with_tls(
        self, mock_create_requester, mock_dispatch_table, mock_parser
    ):
        """Test the client authenticates successfully with TLS"""
        client = Client(host="localhost", username="user", password="pass")

        assert client.authenticated is True
        assert client.session_id is not None

        mock_requester = mock_create_requester.return_value
        mock_requester.send_request.assert_called_once()

        call_args = mock_requester.send_request.call_args[0][0]
        assert "LoginRequest22V5" in str(call_args)

    def test_authentication_success_without_tls(
        self, mock_create_requester, mock_dispatch_table, mock_parser
    ):
        """Test the client authenticates successfully without TLS"""
        client = Client(host="localhost", username="user", password="pass", tls=False)

        assert client.authenticated is True
        assert client.session_id is not None

        mock_requester = mock_create_requester.return_value

        call_args = mock_requester.send_request.call_args[0][0]
        assert "LoginRequest14sp4" in str(call_args)

    @pytest.mark.skip(reason="pytest/attrs compatibility issue with frozen objects")
    def test_authentication_failure(
        self,
        mock_create_requester,
        mock_dispatch_table,
        mock_parser,
        mock_receive_response,
    ):
        """Test the client authentication fails"""
        from mercury_ocip.exceptions import MError

        with pytest.raises(MError):
            client = Client(host="localhost", username="user", password="wrong_pass")

    def test_command_flow(
        self,
        mock_create_requester,
        mock_dispatch_table,
        mock_parser,
        mock_authenticate,
        mock_receive_response,
    ):
        """Test the complete command method flow"""

        # Create client (this will authenticate automatically)
        client = Client(host="localhost", username="user", password="pass")
        client.authenticated = True
        command = UserGetRegistrationListRequest(user_id="example_user")
        response = client.command(command)

        assert response == "UserGetRegistrationListResponse"

    def test_raw_command_flow(
        self,
        mock_create_requester,
        mock_dispatch_table,
        mock_parser,
        mock_authenticate,
        mock_receive_response,
    ):
        """Test the raw command method flow"""

        # Create client (this will authenticate automatically)
        client = Client(host="localhost", username="user", password="pass")
        client.authenticated = True

        response = client.raw_command(
            "UserGetRegistrationListRequest", user_id="example_user"
        )

        assert response == "UserGetRegistrationListResponse"

    def test_raw_command_with_non_existent_command(
        self,
        mock_create_requester,
        mock_dispatch_table,
        mock_parser,
        mock_authenticate,
        mock_receive_response,
    ):
        """Test the raw command method flow with a non-existent command"""

        # Create client (this will authenticate automatically)
        client = Client(host="localhost", username="user", password="pass")
        client.authenticated = True

        with pytest.raises(ValueError):
            client.raw_command("ThisCommandDoesntExist", userId="example_user")

    def test_disconnect_method(
        self,
        mock_create_requester,
        mock_dispatch_table,
        mock_parser,
        mock_authenticate,
        mock_receive_response,
    ):
        """Test the disconnect method"""

        # Create client (this will authenticate automatically)
        client = Client(host="localhost", username="user", password="pass")
        client.authenticated = True

        client.disconnect()

        assert client.authenticated is False
        assert client.session_id is ""
