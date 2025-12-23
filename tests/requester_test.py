import pytest
from unittest.mock import Mock, patch, AsyncMock
import sys
import os
from lxml import etree
import socket

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mercury_ocip.requester import (
    SyncTCPRequester,
    SyncSOAPRequester,
    AsyncSOAPRequester,
    AsyncTCPRequester,
)
from mercury_ocip.exceptions import (
    MErrorSocketInitialisation,
    MErrorSocketTimeout,
    MErrorClientInitialisation,
    MErrorSendRequestFailed,
)
from mercury_ocip.commands import base_command as BroadworksCommand


@pytest.fixture
def mock_logger():
    return Mock()


@pytest.fixture
def mock_command():
    cmd = Mock()
    cmd.encode.return_value = b"""
<BroadsoftDocument xmlns:xsi="http://www.w3.org/2001/XMLSchema-requester">
  <command xmlns="" xsi:type="LoginRequest22V5"></command>
</BroadsoftDocument>
"""
    return cmd


def test_build_oci_xml_creates_correct_structure(mock_logger):
    requester = SyncSOAPRequester.__new__(SyncSOAPRequester)
    requester.client = None
    requester.logger = mock_logger
    requester.session_id = "123214235235235"

    mock_command = Mock()
    mock_command.encode.return_value = """
    <command xmlns="" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="AuthenticationRequest">
    <userId>vinny</userId>
    </command>"""

    result = requester.build_oci_xml(mock_command)
    root = etree.fromstring(result)

    assert root.tag == "{C}BroadsoftDocument"

    session_el = root.find("sessionId")
    assert session_el is not None
    assert session_el.text == "123214235235235"

    command_el = root.find("command")
    assert command_el is not None
    assert (
        command_el.attrib.get("{http://www.w3.org/2001/XMLSchema-instance}type")
        == "AuthenticationRequest"
    )

    user_id_el = command_el.find("userId")
    assert user_id_el is not None
    assert user_id_el.text == "vinny"


class TestSyncTCPRequester:
    @patch("socket.create_connection")
    @patch("ssl.create_default_context")
    def test_init_and_connect_ssl_success(
        self, mock_ssl_context, mock_create_connection, mock_logger
    ):
        mock_socket = Mock()
        mock_create_connection.return_value = mock_socket

        mock_ssl = Mock()
        mock_ssl.wrap_socket.return_value = "wrapped_socket"
        mock_ssl_context.return_value = mock_ssl

        requester = SyncTCPRequester(
            logger=mock_logger, host="localhost", port=2209, tls=True
        )
        result = requester.connect()

        assert requester.sock == "wrapped_socket"
        mock_create_connection.assert_called_once_with(("localhost", 2209), timeout=30)
        mock_ssl.wrap_socket.assert_called_once_with(
            mock_socket, server_hostname="localhost"
        )
        mock_logger.info.assert_called()
        assert result is None

    @patch("socket.create_connection")
    @patch("ssl.create_default_context")
    def test_connect_ssl_failure(
        self, mock_ssl_context, mock_create_connection, mock_logger
    ):
        mock_create_connection.side_effect = Exception("Failed to connect")

        requester = SyncTCPRequester(
            logger=mock_logger, host="localhost", port=2209, tls=True
        )
        result = requester.connect()

        assert requester.sock is None
        assert isinstance(result, MErrorSocketInitialisation)
        mock_logger.error.assert_called()

    def test_sync_tcp_send_request_success(self, mock_logger):
        requester = SyncTCPRequester.__new__(SyncTCPRequester)
        requester.logger = mock_logger
        requester.host = "localhost"
        requester.port = 2209
        requester.timeout = 30
        requester.session_id = ""
        fake_sock = Mock()
        fake_sock.sendall = Mock()
        fake_sock.recv = Mock(side_effect=[b"<BroadsoftDocument>", b"<command/>", b"</BroadsoftDocument>"])
        requester.sock = fake_sock

        mock_command = Mock()
        with patch.object(requester, "build_oci_xml", return_value=b"<mock-xml>"):
            result = requester.send_request(mock_command)

        assert isinstance(result, str)
        assert "</BroadsoftDocument>" in result
        fake_sock.sendall.assert_called_once()

    def test_sync_tcp_send_request_recv_timeout_returns_MError(self, mock_logger):
        mock_logger = Mock()
        requester = SyncTCPRequester.__new__(SyncTCPRequester)
        requester.logger = mock_logger
        requester.host = "localhost"
        requester.port = 2209
        requester.timeout = 30
        requester.session_id = ""
        fake_sock = Mock()
        fake_sock.sendall = Mock()
        fake_sock.recv = Mock(side_effect=socket.timeout("timed out"))
        requester.sock = fake_sock

        mock_command = Mock()
        with patch.object(requester, "build_oci_xml", return_value=b"<mock-xml>"):
            result = requester.send_request(mock_command)

        assert isinstance(result, MErrorSocketTimeout)


class TestSyncSOAPRequester:
    @patch("mercury_ocip.requester.requests.sessions.Session")
    @patch("mercury_ocip.requester.Settings")
    @patch("mercury_ocip.requester.Transport")
    @patch("mercury_ocip.requester.Client")
    def test_connect_success(
        self, mock_client_class, mock_transport, mock_settings, mock_session
    ):
        mock_logger = Mock()
        requester = SyncSOAPRequester(logger=mock_logger, host="localhost", port=2209)

        assert requester.client is not None
        assert requester.zclient is not None
        mock_logger.info.assert_called_once_with(
            "Initiated client on SyncSOAPRequester: localhost:2209"
        )

    @patch(
        "mercury_ocip.requester.requests.sessions.Session",
        side_effect=Exception("Session error"),
    )
    def test_connect_fail(self, mock_session):
        mock_logger = Mock()
        requester = SyncSOAPRequester.__new__(SyncSOAPRequester)
        requester.logger = mock_logger
        requester.host = "localhost"
        requester.port = 2209
        requester.timeout = 10
        requester.client = None

        result = requester.connect()

        assert isinstance(result, MErrorClientInitialisation)
        mock_logger.error.assert_called_once()
        mock_logger.info.assert_not_called()

    def test_disconnect_closes_session(self):
        mock_logger = Mock()
        mock_client = Mock()

        requester = SyncSOAPRequester.__new__(SyncSOAPRequester)
        requester.logger = mock_logger
        requester.client = mock_client

        requester.disconnect()

        mock_client.close.assert_called_once()
        assert requester.client is None

    def test_disconnect_handles_exception(self):
        mock_logger = Mock()
        bad_client = Mock()
        bad_client.close.side_effect = Exception("close failed")

        requester = SyncSOAPRequester.__new__(SyncSOAPRequester)
        requester.logger = mock_logger
        requester.client = bad_client

        requester.disconnect()

        mock_logger.warning.assert_called_once()
        assert requester.client is None

    @patch.object(SyncSOAPRequester, "build_oci_xml")
    def test_send_request_success(self, mock_build_xml):
        mock_logger = Mock()
        requester = SyncSOAPRequester.__new__(SyncSOAPRequester)
        requester.logger = mock_logger
        requester.zclient = Mock()
        requester.zclient.service.processOCIMessage = Mock(
            return_value="<xml>response</xml>"
        )

        mock_command = Mock(spec=BroadworksCommand)

        result = requester.send_request(mock_command)

        assert result == "<xml>response</xml>"
        mock_build_xml.assert_called_once_with(mock_command)

    @patch.object(
        SyncSOAPRequester, "build_oci_xml", side_effect=Exception("build failed")
    )
    def test_send_request_fail(self, mock_build_xml):
        mock_logger = Mock()
        requester = SyncSOAPRequester.__new__(SyncSOAPRequester)
        requester.logger = mock_logger
        requester.zclient = Mock()

        mock_command = Mock(spec=BroadworksCommand)

        result = requester.send_request(mock_command)

        assert isinstance(result, MErrorSendRequestFailed)
        mock_logger.error.assert_called_once()


class TestAsyncTCPRequester:
    @pytest.mark.asyncio
    async def test_send_request_success(self):
        mock_logger = Mock()

        async def fake_command():
            return "mocked_command"

        mock_command = fake_command()

        requester = AsyncTCPRequester.__new__(AsyncTCPRequester)
        requester.logger = mock_logger
        requester.host = "localhost"
        requester.port = 2209
        requester.timeout = 10
        requester.session_id = None

        requester.reader = AsyncMock()
        requester.writer = AsyncMock()
        requester.writer.drain = AsyncMock()
        requester.reader.read = AsyncMock(
            side_effect=[b"<data></BroadsoftDocument>", b""]
        )

        with patch.object(requester, "build_oci_xml", return_value=b"<mocked-xml>"):
            result = await requester.send_request(mock_command)

            assert isinstance(result, str)
            assert "data" in result
            requester.writer.write.assert_called_once()
            requester.writer.drain.assert_called_once()


class TestAsyncSOAPRequester:
    @pytest.mark.asyncio
    async def test_send_request_success(self):
        mock_logger = Mock()

        async def fake_command():
            return "mocked_command"

        mock_command = fake_command()

        requester = AsyncSOAPRequester.__new__(AsyncSOAPRequester)
        requester.logger = mock_logger
        requester.host = "localhost"
        requester.port = 2209
        requester.timeout = 10
        requester.session_id = None

        requester.async_client = Mock()
        requester.wsdl_client = Mock()
        requester.zeep_client = Mock()
        requester.zeep_client.service.processOCIMessage = AsyncMock(
            return_value="soap response"
        )

        with patch.object(requester, "build_oci_xml", return_value=b"<mocked-xml>"):
            result = await requester.send_request(mock_command)

            assert result == "soap response"
            requester.zeep_client.service.processOCIMessage.assert_called_once()
