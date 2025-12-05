import pytest
import tempfile
import os
from unittest.mock import Mock

from mercury_ocip.client import Client
from mercury_ocip.bulk.auto_attendant import AutoAttendantBulkOperations
from mercury_ocip.commands.commands import GroupAutoAttendantConsolidatedAddInstanceRequest, ServiceInstanceAddProfile


class TestAutoAttendantBulkOperations:
    """Simple tests for auto attendant bulk operations"""

    @pytest.fixture
    def mock_client(self):
        """Mock client with dispatch table"""
        client = Mock(spec=Client)
        client._dispatch_table = {
            "GroupAutoAttendantConsolidatedAddInstanceRequest": GroupAutoAttendantConsolidatedAddInstanceRequest,
            "ServiceInstanceAddProfile": ServiceInstanceAddProfile,
        }
        return client

    def test_csv_flow_with_template_file(self, mock_client):
        """Test CSV processing using the actual template file"""
        # Create temp CSV with template format
        csv_content = """operation,serviceProviderId,groupId,serviceUserId,serviceInstanceProfile.name,serviceInstanceProfile.callingLineIdLastName,serviceInstanceProfile.callingLineIdFirstName,type,firstDigitTimeoutSeconds,enableVideo,extensionDialingScope,nameDialingEntries,isActive
auto.attendant.create,TestServiceProvider,SalesGroup,sales-aa@test.com,Sales Auto Attendant,Sales,AA,Basic,15,false,Group,LastName + FirstName,true"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_file = f.name

        try:
            auto_attendant_ops = AutoAttendantBulkOperations(mock_client)
            mock_response = Mock()
            mock_client.command.return_value = mock_response

            results = auto_attendant_ops.execute_from_csv(temp_file, dry_run=False)

            assert len(results) == 1
            assert results[0]["success"]
            assert results[0]["data"]["service_instance_profile"]["name"] == "Sales Auto Attendant"
        finally:
            os.unlink(temp_file)

    def test_direct_method_call_flow(self, mock_client):
        """Test direct method call with data array"""
        auto_attendant_ops = AutoAttendantBulkOperations(mock_client)
        mock_response = Mock()
        mock_client.command.return_value = mock_response

        data = [
            {
                "operation": "auto.attendant.create",
                "service_provider_id": "TestServiceProvider",
                "group_id": "TestGroup",
                "service_user_id": "test-aa@test.com",
                "service_instance_profile": {
                    "name": "Test Auto Attendant",
                    "calling_line_id_last_name": "Test",
                    "calling_line_id_first_name": "AA",
                },
                "type": "Basic",
                "first_digit_timeout_seconds": 15,
            }
        ]

        results = auto_attendant_ops.execute_from_data(data, dry_run=False)

        assert len(results) == 1
        assert results[0]["success"]
        assert results[0]["data"]["service_instance_profile"]["name"] == "Test Auto Attendant"

    def test_nested_object_processing(self, mock_client):
        """Test that serviceInstanceProfile.* notation is properly converted to nested object"""
        auto_attendant_ops = AutoAttendantBulkOperations(mock_client)

        row = {
            "operation": "auto.attendant.create",
            "serviceProviderId": "TestServiceProvider",
            "groupId": "TestGroup",
            "serviceUserId": "test-aa@test.com",
            "serviceInstanceProfile.name": "Test Auto Attendant",
            "serviceInstanceProfile.callingLineIdLastName": "Test",
            "serviceInstanceProfile.callingLineIdFirstName": "AA",
            "type": "Basic",
            "firstDigitTimeoutSeconds": "15",
        }

        result = auto_attendant_ops._process_row(row)

        assert "service_instance_profile" in result
        assert result["service_instance_profile"]["name"] == "Test Auto Attendant"
        assert result["service_instance_profile"]["calling_line_id_last_name"] == "Test"
        assert result["service_instance_profile"]["calling_line_id_first_name"] == "AA"

    def test_nested_array_processing(self, mock_client):
        """Test that serviceInstanceProfile.alias[0] notation is properly converted to nested array"""
        auto_attendant_ops = AutoAttendantBulkOperations(mock_client)

        row = {
            "operation": "auto.attendant.create",
            "serviceProviderId": "TestServiceProvider",
            "groupId": "TestGroup",
            "serviceUserId": "test-aa@test.com",
            "serviceInstanceProfile.name": "Test Auto Attendant",
            "serviceInstanceProfile.alias[0]": "test-alias1",
            "serviceInstanceProfile.alias[1]": "test-alias2",
            "type": "Basic",
        }

        result = auto_attendant_ops._process_row(row)

        assert "service_instance_profile" in result
        assert result["service_instance_profile"]["alias"] == ["test-alias1", "test-alias2"]

    def test_boolean_conversion(self, mock_client):
        """Test that boolean values are properly converted from strings"""
        auto_attendant_ops = AutoAttendantBulkOperations(mock_client)

        row = {
            "operation": "auto.attendant.create",
            "serviceProviderId": "TestServiceProvider",
            "groupId": "TestGroup",
            "serviceUserId": "test-aa@test.com",
            "serviceInstanceProfile.name": "Test Auto Attendant",
            "enableVideo": "true",
            "isActive": "false",
            "type": "Basic",
        }

        result = auto_attendant_ops._process_row(row)

        assert result["enable_video"] is True
        assert result["is_active"] is False

    def test_integer_conversion(self, mock_client):
        """Test that integer fields are properly converted from strings"""
        auto_attendant_ops = AutoAttendantBulkOperations(mock_client)

        row = {
            "operation": "auto.attendant.create",
            "serviceProviderId": "TestServiceProvider",
            "groupId": "TestGroup",
            "serviceUserId": "test-aa@test.com",
            "serviceInstanceProfile.name": "Test Auto Attendant",
            "firstDigitTimeoutSeconds": "20",
            "type": "Basic",
        }

        result = auto_attendant_ops._process_row(row)

        assert result["first_digit_timeout_seconds"] == 20

    def test_defaults_application(self, mock_client):
        """Test that defaults are properly applied when not provided"""
        auto_attendant_ops = AutoAttendantBulkOperations(mock_client)
        mock_response = Mock()
        mock_client.command.return_value = mock_response

        data = [
            {
                "operation": "auto.attendant.create",
                "service_provider_id": "TestServiceProvider",
                "group_id": "TestGroup",
                "service_user_id": "test-aa@test.com",
                "service_instance_profile": {
                    "name": "Test Auto Attendant",
                },
            }
        ]

        results = auto_attendant_ops.execute_from_data(data, dry_run=True)

        assert len(results) == 1
        assert results[0]["success"]
        # Check that defaults were applied
        result_data = results[0]["command"]
        assert result_data.type == "Basic"  # default
        assert result_data.first_digit_timeout_seconds == 10  # default
        assert result_data.enable_video is False  # default
        assert result_data.extension_dialing_scope == "Group"  # default
        assert result_data.name_dialing_entries == "LastName + FirstName"  # default
        assert result_data.is_active is True  # default

    def test_dry_run_mode(self, mock_client):
        """Test dry run doesn't make API calls"""
        auto_attendant_ops = AutoAttendantBulkOperations(mock_client)

        data = [
            {
                "operation": "auto.attendant.create",
                "service_provider_id": "TestServiceProvider",
                "group_id": "TestGroup",
                "service_user_id": "test-aa@test.com",
                "service_instance_profile": {
                    "name": "Test Auto Attendant",
                },
            }
        ]

        results = auto_attendant_ops.execute_from_data(data, dry_run=True)

        assert len(results) == 1
        assert results[0]["success"] 
        mock_client.command.assert_not_called()

    def test_case_conversion(self, mock_client):
        """Test that camelCase is converted to snake_case"""
        auto_attendant_ops = AutoAttendantBulkOperations(mock_client)

        row = {
            "operation": "auto.attendant.create",
            "serviceProviderId": "TestServiceProvider",
            "groupId": "TestGroup",
            "serviceUserId": "test-aa@test.com",
            "serviceInstanceProfile.name": "Test Auto Attendant",
            "enableVideo": "true",
            "firstDigitTimeoutSeconds": "15",
            "type": "Basic",
        }

        result = auto_attendant_ops._process_row(row)

        assert "service_provider_id" in result
        assert "group_id" in result
        assert "service_user_id" in result
        assert "enable_video" in result
        assert "first_digit_timeout_seconds" in result