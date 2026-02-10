import sys
import os
from unittest.mock import MagicMock, patch
import pytest
from mercury_ocip.cli.globals import MERCURY_CLI
from mercury_ocip.cli.commands.misc.plugins import load_plugins
from mercury_ocip.plugins.base_plugin import BasePlugin
from mercury_ocip.cli.utils.service_group_id_callable import (
        _get_group_id_completions,
        _get_service_provider_id_completions,
    )

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

@pytest.fixture
def mock_cli_components():
    """Fixture to mock CLI internals (client and agent) for command testing."""
    mock_client = MagicMock()
    mock_agent = MagicMock()
    mock_bulk = MagicMock()

    # Setup the chain: agent().bulk -> mock_bulk
    mock_agent.bulk = mock_bulk

    # Patch both simultaneously using a single context or backslash continuation
    with patch.object(MERCURY_CLI, 'client', return_value=mock_client), \
         patch.object(MERCURY_CLI, 'agent', return_value=mock_agent):
        
        # Return a simple object holding our mocks so tests can access them
        mocks = MagicMock()
        mocks.client = mock_client
        mocks.agent = mock_agent
        mocks.bulk = mock_bulk
        yield mocks

@pytest.fixture(autouse=True)
def clear_plugin_actions_between_tests():
    """Ensure plugin-related actions don't leak between tests.

    Keeps the default 'list' command and removes any plugin groups added by load_plugins.
    """
    completer = MERCURY_CLI.completer()
    plugin_action = completer.root.children.get("plugin")
    if plugin_action:
        for key in list(plugin_action.children.keys()):
            if key != "list":
                plugin_action.children.pop(key, None)

    yield

    # Cleanup after test as well
    plugin_action = completer.root.children.get("plugin")
    if plugin_action:
        for key in list(plugin_action.children.keys()):
            if key != "list":
                plugin_action.children.pop(key, None)

def test_bulk_create(mock_cli_components):
    """Test bulk create command invocation."""
    test_file = "items.csv"
    command = f"bulk create user {test_file}"
    
    # Mock file existence so argument validation passes
    with patch("os.path.exists", return_value=True):
        MERCURY_CLI.completer().run_action(command)
        
    mock_cli_components.agent.bulk.create_user_from_csv.assert_called_once_with(test_file)

def test_completer_actions():
    """Test that actions are correctly registered in the completer."""
    completer = MERCURY_CLI.completer()

    # Check if root commands exist
    assert "exit" in completer.root.children
    assert "sysver" in completer.root.children
    assert "bulk" in completer.root.children
    assert "automations" in completer.root.children

    exit_action = completer.root.children["exit"]
    assert exit_action.display_meta == "Exits the CLI"

def test_help_command(capsys):
    """Test the help command displays available commands."""
    completer = MERCURY_CLI.completer()

    assert "help" in completer.root.children
    help_action = completer.root.children["help"]
    assert help_action.display_meta == "Gives a list of all commands"

    mock_document = MagicMock()
    mock_document.text = "help"
    mock_buffer = MagicMock()
    mock_buffer.document = mock_document
    mock_session = MagicMock()
    mock_session.default_buffer = mock_buffer

    with patch.object(MERCURY_CLI, 'session', return_value=mock_session):
        completer.run_action("help")

    captured = capsys.readouterr()
    assert "Mercury CLI - Available Commands" in captured.out
    assert "help <command>" in captured.out



def test_sysver_command(capsys, mock_cli_components):
    """Test the sysver command which interacts with the client."""
    # Setup mock return value
    mock_version = MagicMock()
    mock_version.version = "1.0.0"
    mock_cli_components.client.raw_command.return_value = mock_version

    MERCURY_CLI.completer().run_action("sysver")

    captured = capsys.readouterr()
    assert "Current system version: 1.0.0" in captured.out
    mock_cli_components.client.raw_command.assert_called_with("SystemSoftwareVersionGetRequest")

def test_plugin_found_listing_with_installed(mock_cli_components):
    class MockPlugin(BasePlugin):
        def __init__(self, client):
            self.description = "Mock plugin description"

        def get_commands(self):
            return {}

    fake_entrypoint = MagicMock()
    fake_entrypoint.name = "MockPlugin"

    plugin_instance = MockPlugin(None)

    mock_cli_components.agent._discoverable_plugins = [
        (MockPlugin, plugin_instance, fake_entrypoint),
    ]

    load_plugins()

    completer = MERCURY_CLI.completer()

    assert "plugin" in completer.root.children

    plugin_action = completer.root.children["plugin"]

    assert plugin_action.display_meta == "Used to view and manage plugins"

    assert "mock_plugin" in plugin_action.children
    assert plugin_action.children["mock_plugin"].display_meta == "Mock plugin description"

def test_plugin_not_found_listing_with_none_installed(mock_cli_components):
    mock_cli_components.agent._discoverable_plugins = []

    load_plugins()
        
    completer = MERCURY_CLI.completer()
    
    assert "plugin" in completer.root.children
    
    plugin_action = completer.root.children["plugin"]

    assert plugin_action.display_meta == "Used to view and manage plugins"

    assert len(plugin_action.children) == 1 # Only 'list' command should be present
