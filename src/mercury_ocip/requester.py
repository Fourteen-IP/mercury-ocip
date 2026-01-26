import socket
import requests
import ssl
import logging
from abc import ABC, abstractmethod
from typing import Optional, Union

from mercury_ocip.exceptions import (
    MErrorSocketInitialisation,
    MErrorSendRequestFailed,
    MErrorSocketTimeout,
    MErrorClientInitialisation,
    MError,
)
from mercury_ocip.libs.types import (
    RequestResult,
    ConnectResult,
    DisconnectResult,
)

from lxml import etree, builder
from zeep import Client, Settings, Transport


class BaseRequester(ABC):
    """Base class for all requesters.

    Args:
        logger (logging.Logger): The logger of the requester.
        host (str): The host of the server.
        port (int): The port of the server.
        timeout (int): The timeout of the requester.
        session_id (str): The session id of the requester.
    """

    def __init__(
        self,
        logger: logging.Logger,
        host: str,
        port: int,
        timeout: int,
        session_id: str,
    ) -> None:
        self.logger = logger
        self.host = host
        self.port = port
        self.timeout = timeout
        self.session_id = session_id

    @abstractmethod
    def send_request(self, command: str) -> RequestResult:
        """Sends a request to the server.

        Args:
            command (BroadworksCommand): The command to send to the server.
        """
        pass

    @abstractmethod
    def connect(
        self,
    ) -> ConnectResult:
        """Connects to the server.

        Returns:
            None if successful, or a tuple of (ExceptionType, Exception) if an error occurs.
            For async implementations, returns an awaitable of the same.
        """
        pass

    @abstractmethod
    def disconnect(self) -> DisconnectResult:
        """Disconnects from the server."""
        pass

    def build_oci_xml(self, command: str) -> bytes:
        """Builds an OCI XML request from the given BroadworksCommand.

        Constructs an XML document with a session ID and the encoded command,
        wrapped in a BroadsoftDocument element with the OCI protocol.

        Args:
            command (BroadworksCommand): The command to be encoded into the XML.

        Returns:
            bytes: The serialized XML document as bytes, encoded with ISO-8859-1.
        """

        ElementMaker = builder.ElementMaker(
            namespace="C",
            nsmap={None: "C", "xsi": "http://www.w3.org/2001/XMLSchema-instance"},
        )

        session_id = etree.Element("sessionId")
        session_id.text = self.session_id
        session_id.set("xmlns", "")

        command_element = etree.fromstring(command.encode("ISO-8859-1"))

        broadsoft_doc = ElementMaker.BroadsoftDocument(
            session_id, command_element, protocol="OCI"
        )

        return etree.tostring(
            broadsoft_doc, xml_declaration=True, encoding="ISO-8859-1"
        )

    def __del__(self) -> None:
        self.disconnect()


class SyncTCPRequester(BaseRequester):
    """A synchronous TCP requester for BroadWorks OCI-P.

    This class manages a synchronous connection to a BroadWorks Application
    Server. It will open a TCP Socket connection, using 2209 for an SSL wrapped
    socket for encrypted traffic.

    Args:
        logger (logging.Logger): An instance of `logging.Logger` for logging messages.
        host (str): The hostname or IP address of the BroadWorks server.
        port (int): The port for the OCI-P interface, defaults to 2209.
        timeout (int): The timeout for HTTP requests in seconds, defaults to 10.
        session_id (str): The session ID for an established OCI-P session.
    """

    def __init__(
        self,
        logger: logging.Logger,
        host: str,
        port: int = 2209,
        timeout: int = 30,
        session_id: str = "",
        tls: bool = True,
    ) -> None:
        self.sock: Optional[Union[socket.socket, ssl.SSLSocket]] = None
        self.tls = tls
        super().__init__(
            logger=logger,
            host=host,
            port=port,
            timeout=timeout,
            session_id=session_id,
        )
        self.connect()

    def connect(self) -> ConnectResult:
        """
        Opens a TCP Socket connection to the Server

        Returns:
            THErrorSocketInitialisation if the Socket fails to open
        """
        if self.sock is None:
            try:
                if self.tls:
                    raw_sock: socket.socket = socket.create_connection(
                        (self.host, self.port), timeout=self.timeout
                    )
                    context: ssl.SSLContext = ssl.create_default_context()
                    self.sock = context.wrap_socket(raw_sock, server_hostname=self.host)
                else:
                    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.sock.settimeout(self.timeout)
                    self.sock.connect((self.host, self.port))
            except Exception as e:
                self.logger.error(
                    f"Failed to initiate socket on {self.__class__.__name__}: {e}"
                )
                return MErrorSocketInitialisation(str(e))
            finally:
                self.logger.info(
                    f"Initiated socket on {self.__class__.__name__}: {self.host}:{self.port}"
                )

    def disconnect(self) -> None:
        """Disconnects from the server."""
        if self.sock:
            try:
                self.sock.close()
            except Exception as e:
                self.logger.warning(
                    f"Exception: {e} was raised when attemping to close {self.__class__.__name__}, but was ignored."
                )
                pass  # Pass as this is expected behaviour, but better to put a warning.
            finally:
                self.sock = None

    def send_request(self, command: str) -> RequestResult:
        """Sends a request to the server.

        Args:
            command (str): The command to send to the server.

        Returns:
            Any: The response from the server.
        """
        try:
            if self.sock is None and isinstance(connection := self.connect(), MError):
                return connection

            assert self.sock is not None

            command_bytes: bytes = self.build_oci_xml(command)

            self.logger.debug(f"Sending command to {self.host}:{self.port}: {command}")

            self.sock.sendall(command_bytes + b"\n")

            content = b""
            while True:
                try:
                    chunk: bytes = self.sock.recv(4096)

                    if not chunk:
                        self.logger.warning(
                            "Socket connection closed unexpectedly before receiving full message."
                        )
                        break
                    content += chunk

                    if b"</BroadsoftDocument>" in content:
                        break
                # Handle blocking IO errors and interruptions gracefully
                except BlockingIOError:
                    continue
                except InterruptedError:
                    continue
            return content.rstrip(b"\n").decode("ISO-8859-1")
        except socket.timeout as e:
            self.logger.error(f"Socket timed out: {self.__class__.__name__}: {e}")
            return MErrorSocketTimeout(str(e))


class SyncSOAPRequester(BaseRequester):
    """A synchronous SOAP requester for BroadWorks OCI-P.

    This class manages a synchronous connection to a BroadWorks Application
    Server, handling the wrapping of OCI commands into SOAP envelopes and
    returning the response.

    Args:
        logger (logging.Logger): An instance of `logging.Logger` for logging messages.
        host (str): The hostname or IP address of the BroadWorks server.
        port (int): The port for the OCI-P interface, defaults to 2209.
        timeout (int): The timeout for HTTP requests in seconds, defaults to 10.
        session_id (str): The session ID for an established OCI-P session.
    """

    def __init__(
        self,
        logger: logging.Logger,
        host: str,
        port: int = 2209,
        timeout: int = 10,
        session_id: str = "",
    ) -> None:
        self.client: Optional[requests.Session] = None
        self.zclient: Optional[Client] = None
        super().__init__(
            logger=logger,
            host=host,
            port=port,
            timeout=timeout,
            session_id=session_id,
        )
        self.connect()

    def connect(self) -> ConnectResult:
        """
        Opens a HTTP Client connection to the Server.

        Returns:
            THErrorClientInitialisation if the client fails to open.
        """
        if self.client is None:
            try:
                self.client = requests.sessions.Session()
                settings: Settings = Settings(strict=False, xml_huge_tree=True)  # type: ignore
                transport: Transport = Transport(
                    session=self.client, timeout=self.timeout
                )
                self.zclient = Client(
                    wsdl=f"{self.host}?wsdl", transport=transport, settings=settings
                )
                self.logger.info(
                    f"Initiated socket on {self.__class__.__name__}: {self.host}:{self.port}"
                )
            except Exception as e:
                self.logger.error(
                    f"Failed to initiate client on {self.__class__.__name__}: {e}"
                )
                return MErrorClientInitialisation(str(e))

    def disconnect(self) -> None:
        """Disconnects from the server."""
        if self.client:
            try:
                self.client.close()
            except Exception as e:
                self.logger.warning(
                    f"Exception: {e} was raised when attempting to close {self.__class__.__name__}, but was ignored."
                )
                pass
            finally:
                self.client = None

    def send_request(self, command: str) -> RequestResult:
        """Sends a request to the server.

        Args:
            command (str): The command to send to the server.

        Returns:
            Any: The response from the server.
        """
        try:
            if self.zclient is None and isinstance(
                connection := self.connect(), MError
            ):
                return connection

            assert self.zclient is not None

            self.logger.debug(
                f"Sending command over {self.__class__.__name__}: {command}"
            )

            response: str = self.zclient.service.processOCIMessage(
                self.build_oci_xml(command)
            )

            return response
        except Exception as e:
            self.logger.error(
                f"Failed to send command over {self.__class__.__name__}: {e}"
            )
            return MErrorSendRequestFailed(str(e))


def create_requester(
    logger: logging.Logger,
    session_id: str,
    host: str,
    port: int,
    conn_type: str = "SOAP",
    timeout: int = 10,
    tls: bool = True,
) -> BaseRequester:
    """Factory function to create a requester.

    Args:
        logger (logging.Logger): The logger to use.
        session_id (str): The session ID to use.
        host (str): The host to connect to.
        port (int): The port to connect to.
        conn_type (str): The connection type to use.
        async_ (bool): Whether to use an asynchronous requester.
        timeout (int): The timeout to use.

    Returns:
        BaseRequester: The created requester.
    """
    if conn_type == "SOAP":
        return SyncSOAPRequester(
            host=host,
            port=port,
            timeout=timeout,
            logger=logger,
            session_id=session_id,
        )
    elif conn_type == "TCP":
        return SyncTCPRequester(
            host=host,
            port=port,
            timeout=timeout,
            logger=logger,
            session_id=session_id,
            tls=tls,
        )
    else:
        raise ValueError(f"Unknown connection type: {conn_type}")
