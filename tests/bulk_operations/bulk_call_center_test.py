import pytest
import tempfile
import os
from unittest.mock import Mock

from mercury_ocip.client import Client
from mercury_ocip.bulk.call_center import CallCenterBulkOperations
from mercury_ocip.commands.commands import GroupCallCenterAddInstanceRequest22, ServiceInstanceAddProfileCallCenter, GroupCallCenterModifyAgentListRequest, ReplacementUserIdList


class TestCallCenterBulkOperations:
    """Simple tests for call center bulk operations"""

    @pytest.fixture
    def mock_client(self):
        """Mock client with dispatch table"""
        client = Mock(spec=Client)
        client._dispatch_table = {
            "GroupCallCenterAddInstanceRequest22": GroupCallCenterAddInstanceRequest22,
            "ServiceInstanceAddProfileCallCenter": ServiceInstanceAddProfileCallCenter,
            "GroupCallCenterModifyAgentListRequest": GroupCallCenterModifyAgentListRequest,
            "ReplacementUserIdList": ReplacementUserIdList,
        }
        return client

    def test_csv_flow_with_template_file(self, mock_client):
        """Test CSV processing using the actual template file"""
        # Create temp CSV with template format
        csv_content = """operation,serviceProviderId,groupId,serviceUserId,serviceInstanceProfile.name,serviceInstanceProfile.callingLineIdLastName,serviceInstanceProfile.callingLineIdFirstName,type,policy,enableVideo,queueLength,wrapUpSeconds,serviceInstanceProfile.password
call.center.create,TestServiceProvider,SalesGroup,sales-center@test.com,Sales Call Center,Sales,Center,Standard,Circular,false,5,45,testpassword123"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_file = f.name

        try:
            call_center_ops = CallCenterBulkOperations(mock_client)
            mock_response = Mock()
            mock_client.command.return_value = mock_response

            results = call_center_ops.execute_from_csv(temp_file, dry_run=False)

            assert len(results) == 1
            assert results[0]["success"]
            assert results[0]["data"]["service_instance_profile"]["name"] == "Sales Call Center"
        finally:
            os.unlink(temp_file)

    def test_direct_method_call_flow(self, mock_client):
        """Test direct method call with data array"""
        call_center_ops = CallCenterBulkOperations(mock_client)
        mock_response = Mock()
        mock_client.command.return_value = mock_response

        data = [
            {
                "operation": "call.center.create",
                "service_provider_id": "TestServiceProvider",
                "group_id": "TestGroup",
                "service_user_id": "test-center@test.com",
                "service_instance_profile": {
                    "name": "Test Call Center",
                    "calling_line_id_last_name": "Test",
                    "calling_line_id_first_name": "Center",
                    "password": "testpassword123",
                },
                "type": "Standard",
                "policy": "Circular",
            }
        ]

        results = call_center_ops.execute_from_data(data, dry_run=False)

        assert len(results) == 1
        assert results[0]["success"]
        assert results[0]["data"]["service_instance_profile"]["name"] == "Test Call Center"

    def test_nested_object_processing(self, mock_client):
        """Test that serviceInstanceProfile.* notation is properly converted to nested object"""
        call_center_ops = CallCenterBulkOperations(mock_client)

        row = {
            "operation": "call.center.create",
            "serviceProviderId": "TestServiceProvider",
            "groupId": "TestGroup",
            "serviceUserId": "test-center@test.com",
            "serviceInstanceProfile.name": "Test Call Center",
            "serviceInstanceProfile.callingLineIdLastName": "Test",
            "serviceInstanceProfile.callingLineIdFirstName": "Center",
            "type": "Standard",
            "policy": "Circular",
        }

        result = call_center_ops._process_row(row)

        assert "service_instance_profile" in result
        assert result["service_instance_profile"]["name"] == "Test Call Center"
        assert result["service_instance_profile"]["calling_line_id_last_name"] == "Test"
        assert result["service_instance_profile"]["calling_line_id_first_name"] == "Center"

    def test_nested_array_processing(self, mock_client):
        """Test that serviceInstanceProfile.alias[0] notation is properly converted to nested array"""
        call_center_ops = CallCenterBulkOperations(mock_client)

        row = {
            "operation": "call.center.create",
            "serviceProviderId": "TestServiceProvider",
            "groupId": "TestGroup",
            "serviceUserId": "test-center@test.com",
            "serviceInstanceProfile.name": "Test Call Center",
            "serviceInstanceProfile.alias[0]": "test-alias1",
            "serviceInstanceProfile.alias[1]": "test-alias2",
            "type": "Standard",
            "policy": "Circular",
        }

        result = call_center_ops._process_row(row)

        assert "service_instance_profile" in result
        assert result["service_instance_profile"]["alias"] == ["test-alias1", "test-alias2"]

    def test_boolean_conversion(self, mock_client):
        """Test that boolean values are properly converted from strings"""
        call_center_ops = CallCenterBulkOperations(mock_client)

        row = {
            "operation": "call.center.create",
            "serviceProviderId": "TestServiceProvider",
            "groupId": "TestGroup",
            "serviceUserId": "test-center@test.com",
            "serviceInstanceProfile.name": "Test Call Center",
            "enableVideo": "true",
            "allowCallerToDialEscapeDigit": "false",
            "type": "Standard",
            "policy": "Circular",
        }

        result = call_center_ops._process_row(row)

        assert result["enable_video"] is True
        assert result["allow_caller_to_dial_escape_digit"] is False

    def test_integer_conversion(self, mock_client):
        """Test that integer fields are properly converted from strings"""
        call_center_ops = CallCenterBulkOperations(mock_client)

        row = {
            "operation": "call.center.create",
            "serviceProviderId": "TestServiceProvider",
            "groupId": "TestGroup",
            "serviceUserId": "test-center@test.com",
            "serviceInstanceProfile.name": "Test Call Center",
            "queueLength": "5",
            "wrapUpSeconds": "45",
            "type": "Standard",
            "policy": "Circular",
        }

        result = call_center_ops._process_row(row)

        assert result["queue_length"] == 5
        assert result["wrap_up_seconds"] == 45

    def test_defaults_application(self, mock_client):
        """Test that defaults are properly applied when not provided"""
        call_center_ops = CallCenterBulkOperations(mock_client)
        mock_response = Mock()
        mock_client.command.return_value = mock_response

        data = [
            {
                "operation": "call.center.create",
                "service_provider_id": "TestServiceProvider",
                "group_id": "TestGroup",
                "service_user_id": "test-center@test.com",
                "service_instance_profile": {
                    "name": "Test Call Center",
                    "calling_line_id_last_name": "Test",
                    "calling_line_id_first_name": "Center",
                    "password": "testpassword123",
                },
            }
        ]

        results = call_center_ops.execute_from_data(data, dry_run=False)

        assert len(results) == 1
        assert results[0]["success"]
        # Check that defaults were applied
        result_command = results[0]["command"]
        assert result_command.type == "Basic"  # default
        assert result_command.policy == "Circular"  # default
        assert result_command.enable_video is False  # default
        assert result_command.queue_length == 3  # default

    def test_dry_run_mode(self, mock_client):
        """Test dry run doesn't make API calls"""
        call_center_ops = CallCenterBulkOperations(mock_client)

        data = [
            {
                "operation": "call.center.create",
                "service_provider_id": "TestServiceProvider",
                "group_id": "TestGroup",
                "service_user_id": "test-center@test.com",
                "service_instance_profile": {
                    "name": "Test Call Center",
                    "calling_line_id_last_name": "Test",
                    "calling_line_id_first_name": "Center",
                    "password": "testpassword123",
                },
            }
        ]

        results = call_center_ops.execute_from_data(data, dry_run=True)

        assert len(results) == 1
        assert results[0]["success"] 
        mock_client.command.assert_not_called()

    def test_case_conversion(self, mock_client):
        """Test that camelCase is converted to snake_case"""
        call_center_ops = CallCenterBulkOperations(mock_client)

        row = {
            "operation": "call.center.create",
            "serviceProviderId": "TestServiceProvider",
            "groupId": "TestGroup",
            "serviceUserId": "test-center@test.com",
            "serviceInstanceProfile.name": "Test Call Center",
            "enableVideo": "true",
            "queueLength": "5",
            "type": "Standard",
            "policy": "Circular",
        }

        result = call_center_ops._process_row(row)

        assert "service_provider_id" in result
        assert "group_id" in result
        assert "service_user_id" in result
        assert "enable_video" in result
        assert "queue_length" in result

    # Tests for modify agent list operation
    def test_modify_agent_list_csv_flow(self, mock_client):
        """Test CSV processing for modify agent list operation"""
        # Create temp CSV with agent list modification format
        csv_content = """operation,serviceUserId,agentUserIdList.userId[0],agentUserIdList.userId[1],agentUserIdList.userId[2]
call.center.update.agent.list,sales-center@test.com,agent1@test.com,agent2@test.com,agent3@test.com"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_file = f.name

        try:
            call_center_ops = CallCenterBulkOperations(mock_client)
            mock_response = Mock()
            mock_client.command.return_value = mock_response

            results = call_center_ops.execute_from_csv(temp_file, dry_run=False)

            assert len(results) == 1
            assert results[0]["success"]
            assert results[0]["data"]["service_user_id"] == "sales-center@test.com"
            assert results[0]["data"]["agent_user_id_list"]["user_id"] == ["agent1@test.com", "agent2@test.com", "agent3@test.com"]
        finally:
            os.unlink(temp_file)

    def test_modify_agent_list_direct_method_call(self, mock_client):
        """Test direct method call for modify agent list operation"""
        call_center_ops = CallCenterBulkOperations(mock_client)
        mock_response = Mock()
        mock_client.command.return_value = mock_response

        data = [
            {
                "operation": "call.center.update.agent.list",
                "service_user_id": "sales-center@test.com",
                "agent_user_id_list": {
                    "user_id": ["agent1@test.com", "agent2@test.com", "agent3@test.com"]
                }
            }
        ]

        results = call_center_ops.execute_from_data(data, dry_run=False)

        assert len(results) == 1
        assert results[0]["success"]
        assert results[0]["data"]["service_user_id"] == "sales-center@test.com"
        assert results[0]["data"]["agent_user_id_list"]["user_id"] == ["agent1@test.com", "agent2@test.com", "agent3@test.com"]

    def test_modify_agent_list_nested_array_processing(self, mock_client):
        """Test that agentUserIdList.userId[0] notation is properly converted to nested array"""
        call_center_ops = CallCenterBulkOperations(mock_client)

        row = {
            "operation": "call.center.update.agent.list",
            "serviceUserId": "sales-center@test.com",
            "agentUserIdList.userId[0]": "agent1@test.com",
            "agentUserIdList.userId[1]": "agent2@test.com",
            "agentUserIdList.userId[2]": "agent3@test.com",
        }

        result = call_center_ops._process_row(row)

        assert "agent_user_id_list" in result
        assert result["agent_user_id_list"]["user_id"] == ["agent1@test.com", "agent2@test.com", "agent3@test.com"]

    def test_modify_agent_list_empty_list(self, mock_client):
        """Test that empty agent list removes all agents"""
        call_center_ops = CallCenterBulkOperations(mock_client)
        mock_response = Mock()
        mock_client.command.return_value = mock_response

        data = [
            {
                "operation": "call.center.update.agent.list",
                "service_user_id": "sales-center@test.com",
                "agent_user_id_list": {
                    "user_id": []
                }
            }
        ]

        results = call_center_ops.execute_from_data(data, dry_run=False)

        assert len(results) == 1
        assert results[0]["success"]
        assert results[0]["data"]["agent_user_id_list"]["user_id"] == []

    def test_modify_agent_list_no_defaults(self, mock_client):
        """Test that modify agent list operation has no defaults applied"""
        call_center_ops = CallCenterBulkOperations(mock_client)
        mock_response = Mock()
        mock_client.command.return_value = mock_response

        data = [
            {
                "operation": "call.center.update.agent.list",
                "service_user_id": "sales-center@test.com",
                "agent_user_id_list": {
                    "user_id": ["agent1@test.com"]
                }
            }
        ]

        results = call_center_ops.execute_from_data(data, dry_run=False)

        assert len(results) == 1
        assert results[0]["success"]
        # Verify no additional defaults were applied beyond what was provided
        result_data = results[0]["data"]
        assert result_data["service_user_id"] == "sales-center@test.com"
        assert result_data["agent_user_id_list"]["user_id"] == ["agent1@test.com"]
        # Should not have any create operation defaults
        assert "type" not in result_data
        assert "policy" not in result_data