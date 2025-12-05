import pytest
import tempfile
import os
from unittest.mock import Mock

from mercury_ocip.client import Client
from mercury_ocip.bulk.hunt_group import HuntGroupBulkOperations
from mercury_ocip.commands.commands import GroupHuntGroupAddInstanceRequest20, ServiceInstanceAddProfile


class TestHuntGroupBulkOperations:
    """Simple tests for hunt group bulk operations"""

    @pytest.fixture
    def mock_client(self):
        """Mock client with dispatch table"""
        client = Mock(spec=Client)
        client._dispatch_table = {
            "GroupHuntGroupAddInstanceRequest20": GroupHuntGroupAddInstanceRequest20,
            "ServiceInstanceAddProfile": ServiceInstanceAddProfile,
        }
        return client

    def test_csv_flow_with_template_file(self, mock_client):
        """Test CSV processing using the actual template file"""
        # Create temp CSV with template format
        csv_content = """operation,serviceProviderId,groupId,serviceUserId,serviceInstanceProfile.name,serviceInstanceProfile.callingLineIdLastName,serviceInstanceProfile.callingLineIdFirstName,policy,huntAfterNoAnswer,noAnswerNumberOfRings,agentUserId[0],agentUserId[1],agentUserId[2]
hunt.group.create,TestServiceProvider,SalesGroup,sales-hunt@test.com,Sales Hunt Group,Sales,Team,Regular,true,5,john.doe@test.com,jane.smith@test.com,bob.wilson@test.com"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_file = f.name

        try:
            hunt_group_ops = HuntGroupBulkOperations(mock_client)
            mock_response = Mock()
            mock_client.command.return_value = mock_response

            results = hunt_group_ops.execute_from_csv(temp_file, dry_run=False)

            assert len(results) == 1
            assert results[0]["success"]
            assert results[0]["data"]["service_instance_profile"]["name"] == "Sales Hunt Group"
            assert results[0]["data"]["agent_user_id"] == ["john.doe@test.com", "jane.smith@test.com", "bob.wilson@test.com"]
        finally:
            os.unlink(temp_file)

    def test_direct_method_call_flow(self, mock_client):
        """Test direct method call with data array"""
        hunt_group_ops = HuntGroupBulkOperations(mock_client)
        mock_response = Mock()
        mock_client.command.return_value = mock_response

        data = [
            {
                "operation": "hunt.group.create",
                "service_provider_id": "TestServiceProvider",
                "group_id": "TestGroup",
                "service_user_id": "test-hunt@test.com",
                "service_instance_profile": {
                    "name": "Test Hunt Group",
                    "calling_line_id_last_name": "Test",
                    "calling_line_id_first_name": "Group",
                },
                "policy": "Regular",
                "agent_user_id": ["user1@test.com", "user2@test.com"],
            }
        ]

        results = hunt_group_ops.execute_from_data(data, dry_run=False)

        assert len(results) == 1
        assert results[0]["success"]
        assert results[0]["data"]["service_instance_profile"]["name"] == "Test Hunt Group"

    def test_array_notation_processing(self, mock_client):
        """Test that agentUserId[0], agentUserId[1] notation is properly converted to array"""
        hunt_group_ops = HuntGroupBulkOperations(mock_client)

        row = {
            "operation": "hunt.group.create",
            "serviceProviderId": "TestServiceProvider",
            "groupId": "TestGroup",
            "serviceUserId": "test-hunt@test.com",
            "serviceInstanceProfile.name": "Test Hunt Group",
            "agentUserId[0]": "user1@test.com",
            "agentUserId[1]": "user2@test.com",
        }

        result = hunt_group_ops._process_row(row)

        assert result["agent_user_id"] == ["user1@test.com", "user2@test.com"]
        assert "agentUserId[0]" not in result
        assert "agentUserId[1]" not in result

    def test_nested_object_processing(self, mock_client):
        """Test that serviceInstanceProfile.* notation is properly converted to nested object"""
        hunt_group_ops = HuntGroupBulkOperations(mock_client)

        row = {
            "operation": "hunt.group.create",
            "serviceProviderId": "TestServiceProvider",
            "groupId": "TestGroup",
            "serviceUserId": "test-hunt@test.com",
            "serviceInstanceProfile.name": "Test Hunt Group",
            "serviceInstanceProfile.callingLineIdLastName": "Test",
            "serviceInstanceProfile.callingLineIdFirstName": "Group",
            "policy": "Regular",
        }

        result = hunt_group_ops._process_row(row)

        assert "service_instance_profile" in result
        assert result["service_instance_profile"]["name"] == "Test Hunt Group"
        assert result["service_instance_profile"]["calling_line_id_last_name"] == "Test"
        assert result["service_instance_profile"]["calling_line_id_first_name"] == "Group"

    def test_nested_array_processing(self, mock_client):
        """Test that serviceInstanceProfile.alias[0] notation is properly converted to nested array"""
        hunt_group_ops = HuntGroupBulkOperations(mock_client)

        row = {
            "operation": "hunt.group.create",
            "serviceProviderId": "TestServiceProvider",
            "groupId": "TestGroup",
            "serviceUserId": "test-hunt@test.com",
            "serviceInstanceProfile.name": "Test Hunt Group",
            "serviceInstanceProfile.alias[0]": "test-alias1",
            "serviceInstanceProfile.alias[1]": "test-alias2",
            "policy": "Regular",
        }

        result = hunt_group_ops._process_row(row)

        assert "service_instance_profile" in result
        assert result["service_instance_profile"]["alias"] == ["test-alias1", "test-alias2"]

    def test_boolean_conversion(self, mock_client):
        """Test that boolean values are properly converted from strings"""
        hunt_group_ops = HuntGroupBulkOperations(mock_client)

        row = {
            "operation": "hunt.group.create",
            "serviceProviderId": "TestServiceProvider",
            "groupId": "TestGroup",
            "serviceUserId": "test-hunt@test.com",
            "serviceInstanceProfile.name": "Test Hunt Group",
            "huntAfterNoAnswer": "true",
            "forwardAfterTimeout": "false",
            "policy": "Regular",
        }

        result = hunt_group_ops._process_row(row)

        assert result["hunt_after_no_answer"] is True
        assert result["forward_after_timeout"] is False

    def test_integer_conversion(self, mock_client):
        """Test that integer fields are properly converted from strings"""
        hunt_group_ops = HuntGroupBulkOperations(mock_client)

        row = {
            "operation": "hunt.group.create",
            "serviceProviderId": "TestServiceProvider",
            "groupId": "TestGroup",
            "serviceUserId": "test-hunt@test.com",
            "serviceInstanceProfile.name": "Test Hunt Group",
            "noAnswerNumberOfRings": "3",
            "forwardTimeoutSeconds": "15",
            "policy": "Regular",
        }

        result = hunt_group_ops._process_row(row)

        assert result["no_answer_number_of_rings"] == 3
        assert result["forward_timeout_seconds"] == 15

    def test_defaults_application(self, mock_client):
        """Test that defaults are properly applied when not provided"""
        hunt_group_ops = HuntGroupBulkOperations(mock_client)
        mock_response = Mock()
        mock_client.command.return_value = mock_response

        data = [
            {
                "operation": "hunt.group.create",
                "service_provider_id": "TestServiceProvider",
                "group_id": "TestGroup",
                "service_user_id": "test-hunt@test.com",
                "service_instance_profile": {
                    "name": "Test Hunt Group",
                },
                "agent_user_id": ["user1@test.com"],
            }
        ]

        results = hunt_group_ops.execute_from_data(data, dry_run=False)

        assert len(results) == 1
        assert results[0]["success"]
        # Check that defaults were applied
        result_data = results[0]["command"]
        assert result_data.policy == "Regular"  # default
        assert result_data.hunt_after_no_answer is True  # default
        assert result_data.no_answer_number_of_rings == 5  # default

    def test_dry_run_mode(self, mock_client):
        """Test dry run doesn't make API calls"""
        hunt_group_ops = HuntGroupBulkOperations(mock_client)

        data = [
            {
                "operation": "hunt.group.create",
                "service_provider_id": "TestServiceProvider",
                "group_id": "TestGroup",
                "service_user_id": "test-hunt@test.com",
                "service_instance_profile": {
                    "name": "Test Hunt Group",
                },
                "agent_user_id": ["user1@test.com"],
            }
        ]

        results = hunt_group_ops.execute_from_data(data, dry_run=True)

        assert len(results) == 1
        assert results[0]["success"] 
        mock_client.command.assert_not_called()

    def test_case_conversion(self, mock_client):
        """Test that camelCase is converted to snake_case"""
        hunt_group_ops = HuntGroupBulkOperations(mock_client)

        row = {
            "operation": "hunt.group.create",
            "serviceProviderId": "TestServiceProvider",
            "groupId": "TestGroup",
            "serviceUserId": "test-hunt@test.com",
            "serviceInstanceProfile.name": "Test Hunt Group",
            "huntAfterNoAnswer": "true",
            "noAnswerNumberOfRings": "5",
            "policy": "Regular",
        }

        result = hunt_group_ops._process_row(row)

        assert "service_provider_id" in result
        assert "group_id" in result
        assert "service_user_id" in result
        assert "hunt_after_no_answer" in result
        assert "no_answer_number_of_rings" in result