import pytest
import tempfile
import os
from unittest.mock import Mock

from mercury_ocip.client import Client
from mercury_ocip.bulk.administrator import AdminBulkOperations
from mercury_ocip.commands.commands import GroupAdminAddRequest, GroupAdminModifyPolicyRequest


class TestAdminBulkOperations:
    """Simple tests for group admin bulk operations"""

    @pytest.fixture
    def mock_client(self):
        """Mock client with dispatch table"""
        client = Mock(spec=Client)
        client._dispatch_table = {
            "GroupAdminAddRequest": GroupAdminAddRequest,
            "GroupAdminModifyPolicyRequest": GroupAdminModifyPolicyRequest,
        }
        return client

    def test_csv_flow_with_template_file_create(self, mock_client):
        """Test CSV processing using the actual template file for create"""
        # Create temp CSV with template format
        csv_content = """operation,serviceProviderId,groupId,userId,firstName,lastName,password,language
group.admin.create,TestServiceProvider,SalesGroup,admin@test.com,John,Doe,password123,English"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_file = f.name

        try:
            group_admin_ops = AdminBulkOperations(mock_client)
            mock_response = Mock()
            mock_client.command.return_value = mock_response

            results = group_admin_ops.execute_from_csv(temp_file, dry_run=False)

            assert len(results) == 1
            assert results[0]["success"]
            assert results[0]["data"]["first_name"] == "John"
            assert results[0]["data"]["last_name"] == "Doe"
        finally:
            os.unlink(temp_file)

    def test_csv_flow_with_template_file_modify_policy(self, mock_client):
        """Test CSV processing using the actual template file for modify policy"""
        # Create temp CSV with template format
        csv_content = """operation,userId,profileAccess,userAccess,adminAccess,departmentAccess,accessDeviceAccess,enhancedServiceInstanceAccess,featureAccessCodeAccess,phoneNumberExtensionAccess,callingLineIdNumberAccess,serviceAccess,trunkGroupAccess,sessionAdmissionControlAccess,officeZoneAccess,dialableCallerIDAccess,numberActivationAccess
group.admin.modify.policy,admin@test.com,Full,Full,Full,Full,Read-Only,Full,Read-Only,Read-Only,Full,Read-Only,Full,Read-Only,Read-Only,Read-Only,None"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_file = f.name

        try:
            group_admin_ops = AdminBulkOperations(mock_client)
            mock_response = Mock()
            mock_client.command.return_value = mock_response

            results = group_admin_ops.execute_from_csv(temp_file, dry_run=False)

            assert len(results) == 1
            assert results[0]["success"]
            assert results[0]["data"]["user_id"] == "admin@test.com"
            assert results[0]["data"]["profile_access"] == "Full"
        finally:
            os.unlink(temp_file)

    def test_direct_method_call_flow_create(self, mock_client):
        """Test direct method call with data array for create"""
        group_admin_ops = AdminBulkOperations(mock_client)
        mock_response = Mock()
        mock_client.command.return_value = mock_response

        data = [
            {
                "operation": "group.admin.create",
                "service_provider_id": "TestServiceProvider",
                "group_id": "TestGroup",
                "user_id": "admin@test.com",
                "first_name": "Test",
                "last_name": "Admin",
                "password": "password123",
                "language": "English",
            }
        ]

        results = group_admin_ops.execute_from_data(data, dry_run=False)

        assert len(results) == 1
        assert results[0]["success"]
        assert results[0]["data"]["first_name"] == "Test"

    def test_direct_method_call_flow_modify_policy(self, mock_client):
        """Test direct method call with data array for modify policy"""
        group_admin_ops = AdminBulkOperations(mock_client)
        mock_response = Mock()
        mock_client.command.return_value = mock_response

        data = [
            {
                "operation": "group.admin.modify.policy",
                "user_id": "admin@test.com",
                "profile_access": "Full",
                "user_access": "Full",
                "admin_access": "Full",
            }
        ]

        results = group_admin_ops.execute_from_data(data, dry_run=False)

        assert len(results) == 1
        assert results[0]["success"]
        assert results[0]["data"]["user_id"] == "admin@test.com"

    def test_case_conversion(self, mock_client):
        """Test that camelCase is converted to snake_case"""
        group_admin_ops = AdminBulkOperations(mock_client)

        row = {
            "operation": "group.admin.create",
            "serviceProviderId": "TestServiceProvider",
            "groupId": "TestGroup",
            "userId": "admin@test.com",
            "firstName": "Test",
            "lastName": "Admin",
            "password": "password123",
        }

        result = group_admin_ops._process_row(row)

        assert "service_provider_id" in result
        assert "group_id" in result
        assert "user_id" in result
        assert "first_name" in result
        assert "last_name" in result

    def test_case_conversion_modify_policy(self, mock_client):
        """Test that camelCase is converted to snake_case for modify policy"""
        group_admin_ops = AdminBulkOperations(mock_client)

        row = {
            "operation": "group.admin.modify.policy",
            "userId": "admin@test.com",
            "profileAccess": "Full",
            "userAccess": "Full",
            "adminAccess": "Full",
        }

        result = group_admin_ops._process_row(row)

        assert "user_id" in result
        assert "profile_access" in result
        assert "user_access" in result
        assert "admin_access" in result

    def test_defaults_application(self, mock_client):
        """Test that defaults are properly applied when not provided"""
        group_admin_ops = AdminBulkOperations(mock_client)
        mock_response = Mock()
        mock_client.command.return_value = mock_response

        data = [
            {
                "operation": "group.admin.modify.policy",
                "user_id": "admin@test.com",
            }
        ]

        results = group_admin_ops.execute_from_data(data, dry_run=False)

        assert len(results) == 1
        assert results[0]["success"]
        # Check that defaults are applied
        result_data = results[0]["command"]
        assert result_data.profile_access == "Read-Only"
        assert result_data.user_access == "Full"
        assert result_data.admin_access == "Read-Only"
        assert result_data.department_access == "Full"

    def test_dry_run_mode(self, mock_client):
        """Test dry run doesn't make API calls"""
        group_admin_ops = AdminBulkOperations(mock_client)

        data = [
            {
                "operation": "group.admin.create",
                "service_provider_id": "TestServiceProvider",
                "group_id": "TestGroup",
                "user_id": "admin@test.com",
                "first_name": "Test",
                "last_name": "Admin",
            }
        ]

        results = group_admin_ops.execute_from_data(data, dry_run=True)

        assert len(results) == 1
        assert results[0]["success"]
        mock_client.command.assert_not_called()

    def test_dry_run_mode_modify_policy(self, mock_client):
        """Test dry run doesn't make API calls for modify policy"""
        group_admin_ops = AdminBulkOperations(mock_client)

        data = [
            {
                "operation": "group.admin.modify.policy",
                "user_id": "admin@test.com",
            }
        ]

        results = group_admin_ops.execute_from_data(data, dry_run=True)

        assert len(results) == 1
        assert results[0]["success"]
        mock_client.command.assert_not_called()

