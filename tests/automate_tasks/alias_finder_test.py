import pytest
from unittest.mock import Mock, patch
from dataclasses import dataclass

from mercury_ocip.client import Client
from mercury_ocip.agent import Agent


@dataclass
class MockEntity:
    """Mock entity with alias field"""
    alias: str | list[str]
    name: str
    service_instance_profile: dict | None = None


class TestAliasFinder:
    """Tests for alias finder automation"""

    @pytest.fixture
    def mock_client(self):
        """Mock client for testing"""
        client = Mock(spec=Client)
        return client

    @pytest.fixture
    def agent(self, mock_client):
        """Agent instance with mocked client"""
        # Reset singleton to allow fresh instance in tests
        Agent._Agent__instance = None
        with patch.object(Agent, 'load_plugins'):
            return Agent.get_instance(mock_client)

    def test_find_alias_successfully(self, agent, mock_client):
        """Test finding an alias that exists on a user"""
        # Mock entity with alias
        mock_user = MockEntity(
            alias="john.doe@test.com",
            name="John Doe"
        )

        # Mock shared_ops methods to return entities
        with patch.object(agent.automate._alias_finder.shared_ops, 'fetch_call_center_details', return_value=[]):
            with patch.object(agent.automate._alias_finder.shared_ops, 'fetch_hunt_group_details', return_value=[]):
                with patch.object(agent.automate._alias_finder.shared_ops, 'fetch_auto_attendant_details', return_value=[]):
                    with patch.object(agent.automate._alias_finder.shared_ops, 'fetch_user_details', return_value=[mock_user]):
                        result = agent.automate.find_alias(
                            service_provider_id="TestSP",
                            group_id="TestGroup",
                            alias="john.doe"
                        )

        assert result.ok is True
        assert result.payload.found is True
        assert result.payload.entity == mock_user
        assert result.message == "Alias found."

    def test_find_alias_not_found(self, agent, mock_client):
        """Test searching for an alias that doesn't exist"""
        # Mock all entity types returning empty lists
        with patch.object(agent.automate._alias_finder.shared_ops, 'fetch_call_center_details', return_value=[]):
            with patch.object(agent.automate._alias_finder.shared_ops, 'fetch_hunt_group_details', return_value=[]):
                with patch.object(agent.automate._alias_finder.shared_ops, 'fetch_auto_attendant_details', return_value=[]):
                    with patch.object(agent.automate._alias_finder.shared_ops, 'fetch_user_details', return_value=[]):
                        result = agent.automate.find_alias(
                            service_provider_id="TestSP",
                            group_id="TestGroup",
                            alias="nonexistent"
                        )

        assert result.ok is False
        assert result.payload.found is False
        assert result.payload.entity is None
        assert result.message == "Alias not found."

    def test_find_alias_ignores_domain(self, agent, mock_client):
        """Test that alias matching ignores the domain part"""
        # Mock hunt group with full domain alias
        mock_hunt_group = MockEntity(
            alias="sales.main@company.com",
            name="Main Sales Hunt Group"
        )

        # Mock shared_ops methods
        with patch.object(agent.automate._alias_finder.shared_ops, 'fetch_call_center_details', return_value=[]):
            with patch.object(agent.automate._alias_finder.shared_ops, 'fetch_hunt_group_details', return_value=[mock_hunt_group]):
                with patch.object(agent.automate._alias_finder.shared_ops, 'fetch_auto_attendant_details', return_value=[]):
                    with patch.object(agent.automate._alias_finder.shared_ops, 'fetch_user_details', return_value=[]):
                        # Search using alias without domain
                        result = agent.automate.find_alias(
                            service_provider_id="TestSP",
                            group_id="TestGroup",
                            alias="sales.main"
                        )

        assert result.ok is True
        assert result.payload.found is True
        assert result.payload.entity == mock_hunt_group
        assert result.message == "Alias found."

