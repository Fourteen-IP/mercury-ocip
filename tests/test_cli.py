import sys
import os
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from mercury_ocip.cli.globals import MERCURY_CLI
from mercury_ocip.cli.main import authenticate, show_splash


def test_singleton_instance():
    """Ensure MERCURY_CLI.get() behaves as a singleton."""
    instance1 = MERCURY_CLI.get()
    instance2 = MERCURY_CLI.get()

    assert instance1 is not None
    assert instance1 is instance2, "MERCURY_CLI.get() did not return the same instance"


def test_globals():
    """Ensure global accessors exist as used in main.py."""

    assert hasattr(MERCURY_CLI, "completer")
    assert hasattr(MERCURY_CLI, "session")
    assert hasattr(MERCURY_CLI, "client")

    # The instance should have these methods
    instance = MERCURY_CLI.get()
    assert hasattr(instance, "client_auth")
    assert hasattr(instance, "session_create")


def test_show_splash(capsys):
    """Test that show_splash prints to stdout."""
    show_splash()
    captured = capsys.readouterr()

    assert "Welcome to mercury_cli" in captured.out


@patch("mercury_ocip.cli.main.Prompt.ask")
@patch("mercury_ocip.cli.globals.MERCURY_CLI.get")
def test_authenticate_flow(mock_cli_get, mock_prompt):
    """Test the authenticate function flow with valid inputs."""
    # Setup mocks
    mock_instance = MagicMock()
    mock_cli_get.return_value = mock_instance

    # Mock user input: username, password, host, tls (y)
    mock_prompt.side_effect = ["testuser", "secret", "https://test.host/webservice/services/ProvisioningService"]

    authenticate()

    # Verify prompt calls (should be 3 inputs)
    assert mock_prompt.call_count == 3

    # Verify client_auth was called on the singleton instance with correct args
    mock_instance.client_auth.assert_called_once_with(
        username="testuser", password="secret", host="https://test.host/webservice/services/ProvisioningService", tls=True
    )