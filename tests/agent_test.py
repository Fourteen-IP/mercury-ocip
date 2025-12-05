import pytest
from unittest.mock import Mock, MagicMock, patch
from importlib.metadata import EntryPoint
import inspect

from mercury_ocip.agent import Agent
from mercury_ocip.client import BaseClient
from mercury_ocip.plugins.base_plugin import BasePlugin


# Mock Plugin Classes for Testing
class MockValidPlugin(BasePlugin):
    """A valid plugin for testing"""
    name = "MockValid"
    
    def __init__(self, client: BaseClient):
        super().__init__(client)
    
    def get_commands(self):
        """Return a dictionary of command names to command classes."""
        pass


class MockInvalidPlugin:
    """Invalid plugin - doesn't inherit from BasePlugin"""
    def __init__(self, client: BaseClient):
        self.client = client


class MockFailingPlugin(BasePlugin):
    """Plugin that fails during initialization"""
    name = "MockFailing"
    
    def __init__(self, client: BaseClient):
        raise ValueError("Intentional initialization failure")


@pytest.fixture
def mock_client():
    """Fixture for a mock BaseClient"""
    return Mock(spec=BaseClient)


@pytest.fixture
def reset_agent_singleton():
    """Reset the Agent singleton between tests"""
    Agent._Agent__instance = None
    yield
    Agent._Agent__instance = None

@pytest.fixture
def reset_installed_plugins():
    """Reset the installed plugins list between tests"""
    Agent._installed_plugins = []
    yield
    Agent._installed_plugins = []

class TestPluginLoading:
    """Test plugin discovery and loading"""
    
    @patch('importlib.metadata.entry_points')
    def test_loads_valid_plugin(self, mock_entry_points, mock_client, reset_agent_singleton, reset_installed_plugins):
        """Test that a valid plugin is loaded correctly"""

        mock_ep = Mock(spec=EntryPoint)
        mock_ep.name = "test_plugin"
        mock_ep.group = "mercury_ocip.plugins"
        mock_ep.load.return_value = MockValidPlugin
        
        mock_eps = Mock()
        mock_eps.select.return_value = [mock_ep]
        mock_entry_points.return_value = mock_eps
        
        agent = Agent.get_instance(mock_client)
        
        assert hasattr(agent, 'mock_valid')
        assert isinstance(agent.mock_valid, MockValidPlugin)
        assert mock_ep in agent._installed_plugins
    
    @patch('importlib.metadata.entry_points')
    def test_skips_invalid_plugin(self, mock_entry_points, mock_client, reset_agent_singleton, reset_installed_plugins):
        """Test that an invalid plugin is skipped"""
        mock_ep = Mock(spec=EntryPoint)
        mock_ep.name = "invalid_plugin"
        mock_ep.group = "mercury_ocip.plugins"
        mock_ep.load.return_value = MockInvalidPlugin
        
        mock_eps = Mock()
        mock_eps.select.return_value = [mock_ep]
        mock_entry_points.return_value = mock_eps
        
        agent = Agent.get_instance(mock_client)
        
        assert not hasattr(agent, 'mock_invalid')
        assert not hasattr(agent, 'invalid_plugin')
        assert mock_ep not in agent._installed_plugins
    
    @patch('importlib.metadata.entry_points')
    def test_skips_base_plugin_class(self, mock_entry_points, mock_client, reset_agent_singleton, reset_installed_plugins):
        """Test that BasePlugin itself is not loaded as a plugin"""
        mock_ep = Mock(spec=EntryPoint)
        mock_ep.name = "base_plugin"
        mock_ep.group = "mercury_ocip.plugins"
        mock_ep.load.return_value = BasePlugin
        
        mock_eps = Mock()
        mock_eps.select.return_value = [mock_ep]
        mock_entry_points.return_value = mock_eps
        
        agent = Agent.get_instance(mock_client)
        
        assert not hasattr(agent, 'base_plugin')
        assert mock_ep not in agent._installed_plugins

    @patch('importlib.metadata.entry_points')
    def test_ignores_plugin_without_entrypoint_group(self, mock_entry_points, 
                                              mock_client, reset_agent_singleton, reset_installed_plugins):
        """Test that plugins without the correct entry point group are ignored"""
        mock_ep = Mock(spec=EntryPoint)
        mock_ep.name = "plugin_test"
        mock_ep.group = "venus_ocip.plugins"
        mock_ep.load.return_value = MockValidPlugin

        mock_eps = Mock()

        mock_eps.select.return_value = []
        mock_entry_points.return_value = mock_eps
        
        agent = Agent.get_instance(mock_client)
        
        assert not hasattr(agent, 'plugin_test')
        assert not hasattr(agent, 'mock_valid')
        assert len(agent._installed_plugins) == 0
    
    @patch('importlib.metadata.entry_points')
    @patch('builtins.print')
    def test_handles_plugin_load_failure(self, mock_print, mock_entry_points, 
                                        mock_client, reset_agent_singleton, reset_installed_plugins):
        """Test that plugin load failure is handled gracefully"""
        mock_ep = Mock(spec=EntryPoint)
        mock_ep.name = "failing_plugin"
        mock_ep.group = "mercury_ocip.plugins"
        mock_ep.load.return_value = MockFailingPlugin
        
        mock_eps = Mock()
        mock_eps.select.return_value = [mock_ep]
        mock_entry_points.return_value = mock_eps
        
        agent = Agent.get_instance(mock_client)
        
        assert not hasattr(agent, 'mock_failing')
        mock_print.assert_called_once()
        assert "Failed to load plugin failing_plugin" in mock_print.call_args[0][0]
    
    @patch('importlib.metadata.entry_points')
    def test_plugin_name_conversion_to_snake_case(self, mock_entry_points, 
                                                   mock_client, reset_agent_singleton, reset_installed_plugins):
        """Test that plugin names are converted to snake_case"""
        mock_ep = Mock(spec=EntryPoint)
        mock_ep.name = "test_plugin"
        mock_ep.group = "mercury_ocip.plugins"
        mock_ep.load.return_value = MockValidPlugin
        
        mock_eps = Mock()
        mock_eps.select.return_value = [mock_ep]
        mock_entry_points.return_value = mock_eps
        
        agent = Agent.get_instance(mock_client)
        
        # Verify plugin name was converted (MockValid -> mock_valid)
        assert hasattr(agent, 'mock_valid')
        assert not hasattr(agent, 'MockValid')
    
    @patch('importlib.metadata.entry_points')
    def test_loads_multiple_plugins(self, mock_entry_points, mock_client, reset_agent_singleton, reset_installed_plugins):
        """Test that multiple plugins are loaded correctly"""
        class AnotherValidPlugin(BasePlugin):
            name = "AnotherValid"
            def __init__(self, client: BaseClient):
                super().__init__(client)

            def get_commands(self):
                """Return a dictionary of command names to command classes."""
                pass
        
        mock_ep1 = Mock(spec=EntryPoint)
        mock_ep1.name = "plugin1"
        mock_ep1.group = "mercury_ocip.plugins"
        mock_ep1.load.return_value = MockValidPlugin
        
        mock_ep2 = Mock(spec=EntryPoint)
        mock_ep2.name = "plugin2"
        mock_ep2.group = "mercury_ocip.plugins"
        mock_ep2.load.return_value = AnotherValidPlugin
        
        mock_eps = Mock()
        mock_eps.select.return_value = [mock_ep1, mock_ep2]
        mock_entry_points.return_value = mock_eps
        
        agent = Agent.get_instance(mock_client)
        
        assert hasattr(agent, 'mock_valid')
        assert hasattr(agent, 'another_valid')
        assert len(agent._installed_plugins) == 2

    @patch('importlib.metadata.entry_points')
    def test_plugin_functions_loaded_correctly(self, mock_entry_points, 
                                     mock_client, reset_agent_singleton, reset_installed_plugins):
        """Test that plugin functions are accessible after loading"""
        class AnotherValidPlugin(BasePlugin):
            name = "AnotherValid"
            def __init__(self, client: BaseClient):
                super().__init__(client)

            def get_commands(self):
                """Return a dictionary of command names to command classes."""
                pass

            def plugin_function(self):
                return "Function Executed"
        
        mock_ep = Mock(spec=EntryPoint)
        mock_ep.name = "another_valid"
        mock_ep.group = "mercury_ocip.plugins"
        mock_ep.load.return_value = AnotherValidPlugin

        mock_eps = Mock()
        mock_eps.select.return_value = [mock_ep]
        mock_entry_points.return_value = mock_eps

        agent = Agent.get_instance(mock_client)

        assert hasattr(agent, 'another_valid')
        assert hasattr(agent.another_valid, 'plugin_function')
        assert agent.another_valid.plugin_function() == "Function Executed"


class TestListPlugins:
    """Test plugin listing functionality"""
    
    @patch('importlib.metadata.entry_points')
    def test_list_plugins_returns_loaded_plugins(self, mock_entry_points, 
                                                 mock_client, reset_agent_singleton, reset_installed_plugins):
        mock_ep = Mock(spec=EntryPoint)
        mock_ep.name = "test_plugin"
        mock_ep.group = "mercury_ocip.plugins"
        mock_ep.load.return_value = MockValidPlugin
        
        mock_eps = Mock()
        mock_eps.select.return_value = [mock_ep]
        mock_entry_points.return_value = mock_eps
        
        agent = Agent.get_instance(mock_client)
        plugins = agent.list_plugins()
        
        assert len(plugins) == 1
        assert mock_ep in plugins
    
    @patch('importlib.metadata.entry_points')
    def test_list_plugins_empty_when_no_plugins(self, mock_entry_points, 
                                                mock_client, reset_agent_singleton, reset_installed_plugins):
        mock_eps = Mock()
        mock_eps.select.return_value = []
        mock_entry_points.return_value = mock_eps
        
        agent = Agent.get_instance(mock_client)
        plugins = agent.list_plugins()
        
        assert len(plugins) == 0
        assert plugins == []