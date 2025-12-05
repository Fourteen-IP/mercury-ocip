import pytest
from unittest.mock import Mock, patch
from dataclasses import dataclass

from mercury_ocip.client import Client
from mercury_ocip.agent import Agent


@dataclass
class MockGroupDetails:
    """Mock group details response"""
    group_name: str = "TestGroup"
    default_domain: str = "test.domain.com"


@dataclass
class MockLicenseResponse:
    """Mock license authorization response"""
    def to_dict(self):
        return {
            "group_services_authorization_table": [
                {"service_name": "Basic", "usage": "10"},
                {"service_name": "Standard", "usage": "5"},
                {"service_name": "Unused", "usage": "0"},  # Should be filtered out
            ],
            "service_packs_authorization_table": [
                {"service_pack_name": "Premium Pack", "usage": "25"},
            ],
            "user_services_authorization_table": [
                {"service_name": "Call Waiting", "usage": "75"},
                {"service_name": "Call Forwarding", "usage": "60"},
            ],
            "empty_table": [],  # Should be filtered out
        }


@dataclass
class MockDnResponse:
    """Mock DN assignment list response"""
    dn_table: list


class TestGroupAuditor:
    """Tests for group auditor automation"""

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

    def test_audit_group_successfully(self, agent, mock_client):
        """Test successful audit with all data populated"""
        # Mock group details response
        mock_group_details = MockGroupDetails()

        # Mock license response
        mock_license_response = MockLicenseResponse()

        # Mock DN response with individual numbers
        mock_dn_response = MockDnResponse(
            dn_table=[
                {"phone_numbers": "1000"},
                {"phone_numbers": "1001"},
                {"phone_numbers": "1002"},
            ]
        )

        # Mock client.command to return appropriate responses based on command type
        def mock_command(command):
            command_name = command.__class__.__name__
            if command_name == "GroupGetRequest22V5":
                return mock_group_details
            elif command_name == "GroupServiceGetAuthorizationListRequest":
                return mock_license_response
            elif command_name == "GroupDnGetAssignmentListRequest18":
                return mock_dn_response
            return None

        mock_client.command.side_effect = mock_command

        result = agent.automate.audit_group(
            service_provider_id="TestSP",
            group_id="TestGroup"
        )

        assert result.ok is True
        assert result.payload.group_details is not None
        assert result.payload.group_details.group_name == "TestGroup"
        assert result.payload.license_breakdown is not None
        assert result.payload.license_breakdown.group_services_authorization_table == {
            "Basic": "10",
            "Standard": "5"
        }
        assert result.payload.license_breakdown.service_packs_authorization_table == {
            "Premium Pack": "25"
        }
        assert result.payload.group_dns is not None
        assert result.payload.group_dns.total == 3
        assert result.payload.group_dns.numbers == {"1000", "1001", "1002"}

    def test_audit_group_with_phone_range(self, agent, mock_client):
        """Test audit handles phone number ranges correctly"""
        # Mock group details response
        mock_group_details = MockGroupDetails()

        # Mock license response (empty for simplicity)
        mock_license_response = MockLicenseResponse()
        mock_license_response.to_dict = lambda: {}

        # Mock DN response with a range
        mock_dn_response = MockDnResponse(
            dn_table=[
                {"phone_numbers": "1000 - 1002"},  # Range should be expanded
                {"phone_numbers": "2000"},  # Single number
            ]
        )

        def mock_command(command):
            command_name = command.__class__.__name__
            if command_name == "GroupGetRequest22V5":
                return mock_group_details
            elif command_name == "GroupServiceGetAuthorizationListRequest":
                return mock_license_response
            elif command_name == "GroupDnGetAssignmentListRequest18":
                return mock_dn_response
            return None

        mock_client.command.side_effect = mock_command

        result = agent.automate.audit_group(
            service_provider_id="TestSP",
            group_id="TestGroup"
        )

        assert result.ok is True
        assert result.payload.group_dns is not None
        # Range "1000 - 1002" should be expanded to 3 numbers plus "2000" = 4 total
        assert result.payload.group_dns.total == 4
        assert "1000" in result.payload.group_dns.numbers
        assert "1001" in result.payload.group_dns.numbers
        assert "1002" in result.payload.group_dns.numbers
        assert "2000" in result.payload.group_dns.numbers

    def test_audit_group_filters_zero_usage(self, agent, mock_client):
        """Test that services with zero usage are filtered out"""
        # Mock group details response
        mock_group_details = MockGroupDetails()

        # Mock license response with zero usage entries
        mock_license_response = MockLicenseResponse()
        mock_license_response.to_dict = lambda: {
            "group_services_authorization_table": [
                {"service_name": "Active Service", "usage": "10"},
                {"service_name": "Inactive Service", "usage": "0"},  # Should be filtered
            ],
            "service_packs_authorization_table": [],
            "user_services_authorization_table": [],
        }

        # Mock DN response
        mock_dn_response = MockDnResponse(dn_table=[])

        def mock_command(command):
            command_name = command.__class__.__name__
            if command_name == "GroupGetRequest22V5":
                return mock_group_details
            elif command_name == "GroupServiceGetAuthorizationListRequest":
                return mock_license_response
            elif command_name == "GroupDnGetAssignmentListRequest18":
                return mock_dn_response
            return None

        mock_client.command.side_effect = mock_command

        result = agent.automate.audit_group(
            service_provider_id="TestSP",
            group_id="TestGroup"
        )

        assert result.ok is True
        assert result.payload.license_breakdown is not None
        # Only "Active Service" should be present, "Inactive Service" with usage "0" filtered out
        assert "Active Service" in result.payload.license_breakdown.group_services_authorization_table
        assert "Inactive Service" not in result.payload.license_breakdown.group_services_authorization_table

