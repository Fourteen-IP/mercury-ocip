import sys
import os
from unittest.mock import MagicMock, patch
import pytest
from mercury_ocip.cli.globals import MERCURY_CLI
from mercury_ocip.cli.core import cli, dispatch
from mercury_ocip.cli.commands.misc.plugins import load_plugins
from mercury_ocip.plugins.base_plugin import BasePlugin
from mercury_ocip.commands.commands import SystemSoftwareVersionGetResponse

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
    """Ensure plugin-related commands don't leak between tests.

    Keeps the default 'list' command and removes any plugin groups added by load_plugins.
    """
    def _cleanup():
        plugin_group = cli.root.children.get("plugin")
        if plugin_group:
            for key in list(plugin_group.children.keys()):
                if key != "list":
                    plugin_group.children.pop(key, None)

    _cleanup()
    yield
    _cleanup()

def test_bulk_create(mock_cli_components):
    """Test bulk create command invocation."""
    test_file = "items.csv"
    command = f"bulk create user {test_file}"

    # Mock file existence so argument validation passes
    with patch("os.path.exists", return_value=True):
        dispatch(command)

    mock_cli_components.agent.bulk.create_user_from_csv.assert_called_once_with(test_file)

def test_bulk_create_quoted_path_with_spaces(mock_cli_components):
    """Paths containing spaces work when quoted."""
    with patch("os.path.exists", return_value=True):
        dispatch('bulk create user "my items.csv"')

    mock_cli_components.agent.bulk.create_user_from_csv.assert_called_once_with("my items.csv")

def test_completer_actions():
    """Test that commands are correctly registered in the tree."""
    assert "exit" in cli.root.children
    assert "sysver" in cli.root.children
    assert "bulk" in cli.root.children
    assert "automations" in cli.root.children

    exit_command = cli.root.children["exit"]
    assert exit_command.meta == "Exits the CLI"

def test_help_command(capsys):
    """Test the help command displays available commands."""
    assert "help" in cli.root.children
    help_command = cli.root.children["help"]
    assert help_command.meta == "Gives a list of all commands"

    dispatch("help")

    captured = capsys.readouterr()
    assert "Mercury CLI - Available Commands" in captured.out
    assert "help <command>" in captured.out

def test_help_for_specific_command(capsys):
    """Help with a command path shows that command's params."""
    dispatch("help automations group_audit")

    captured = capsys.readouterr()
    assert "group_audit" in captured.out
    assert "service_provider_id" in captured.out
    assert "group_id" in captured.out



def test_sysver_command(capsys, mock_cli_components):
    """Test the sysver command which interacts with the client."""
    # Setup mock return value
    mock_version = MagicMock(spec=SystemSoftwareVersionGetResponse)
    mock_version.version = "1.0.0"
    mock_cli_components.client.raw_command.return_value = mock_version

    dispatch("sysver")

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

    assert "plugin" in cli.root.children

    plugin_group = cli.root.children["plugin"]

    assert plugin_group.meta == "Used to view and manage plugins"

    assert "mock_plugin" in plugin_group.children
    assert plugin_group.children["mock_plugin"].meta == "Mock plugin description"

def test_plugin_not_found_listing_with_none_installed(mock_cli_components):
    mock_cli_components.agent._discoverable_plugins = []

    load_plugins()

    assert "plugin" in cli.root.children

    plugin_group = cli.root.children["plugin"]

    assert plugin_group.meta == "Used to view and manage plugins"

    assert len(plugin_group.children) == 1 # Only 'list' command should be present
