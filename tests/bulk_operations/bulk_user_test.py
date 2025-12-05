import pytest
import tempfile
import os
from unittest.mock import Mock

from mercury_ocip.client import Client
from mercury_ocip.bulk.user import UserBulkOperations
from mercury_ocip.commands.commands import UserConsolidatedAddRequest22, AlternateUserIdEntry, StreetAddress, AlternateUserIdEntry


class TestUserBulkOperations:
    """Simple tests for user bulk operations"""

    @pytest.fixture
    def mock_client(self):
        """Mock client with dispatch table"""
        client = Mock(spec=Client)
        client._dispatch_table = {
            "UserConsolidatedAddRequest22": UserConsolidatedAddRequest22,
            "AlternateUserIdEntry": AlternateUserIdEntry,
            "StreetAddress": StreetAddress,
        }
        return client

    def test_csv_flow_with_template_file(self, mock_client):
        """Test CSV processing using the actual template file"""
        # Create temp CSV with template format
        csv_content = """operation,serviceProviderId,groupId,userId,firstName,lastName,callingLineIdFirstName,callingLineIdLastName,extension,password,emailAddress,accessDeviceEndpoint.accessDevice.deviceName,accessDeviceEndpoint.accessDevice.deviceLevel,alias[0],alias[1],alternateUserId[0].alternateUserId,alternateUserId[1].alternateUserId
user.create,TestServiceProvider,SalesGroup,john.doe@test.com,John,Doe,John,Doe,1234,password123,john.doe@test.com,existing-device-01,Group,john.doe,jdoe,jdoe,altuser"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_file = f.name

        try:
            user_ops = UserBulkOperations(mock_client)
            mock_response = Mock()
            mock_client.command.return_value = mock_response

            results = user_ops.execute_from_csv(temp_file, dry_run=False)

            print(results)

            assert len(results) == 1
            assert results[0]["success"]
            assert results[0]["data"]["first_name"] == "John"
            assert results[0]["data"]["last_name"] == "Doe"
            assert results[0]["data"]["alias"] == ["john.doe", "jdoe"]
            assert results[0]["data"]["alternate_user_id"] == [AlternateUserIdEntry(alternate_user_id="jdoe"), AlternateUserIdEntry(alternate_user_id="altuser")]
        finally:
            os.unlink(temp_file)

    def test_direct_method_call_flow(self, mock_client):
        """Test direct method call with data array"""
        user_ops = UserBulkOperations(mock_client)
        mock_response = Mock()
        mock_client.command.return_value = mock_response

        data = [
            {
                "operation": "user.create",
                "service_provider_id": "TestServiceProvider",
                "group_id": "TestGroup",
                "user_id": "test-user@test.com",
                "first_name": "Test",
                "last_name": "User",
                "calling_line_id_first_name": "Test",
                "calling_line_id_last_name": "User",
                "extension": "1234",
                "password": "password123",
                "access_device_endpoint": {
                    "access_device": {
                        "device_name": "existing-device-01",
                        "device_level": "Group"
                    }
                },
                "alias": ["test.user", "tuser"],
            }
        ]

        results = user_ops.execute_from_data(data, dry_run=False)

        assert len(results) == 1
        assert results[0]["success"]
        assert results[0]["data"]["first_name"] == "Test"

    def test_array_notation_processing(self, mock_client):
        """Test that alias[0], alias[1] notation is properly converted to array"""
        user_ops = UserBulkOperations(mock_client)

        row = {
            "operation": "user.create",
            "serviceProviderId": "TestServiceProvider",
            "groupId": "TestGroup",
            "userId": "test-user@test.com",
            "firstName": "Test",
            "lastName": "User",
            "callingLineIdFirstName": "Test",
            "callingLineIdLastName": "User",
            "extension": "1234",
            "password": "password123",
            "alias[0]": "test.user",
            "alias[1]": "tuser",
        }

        result = user_ops._process_row(row)

        assert result["alias"] == ["test.user", "tuser"]
        assert "alias[0]" not in result
        assert "alias[1]" not in result

    def test_nested_object_processing(self, mock_client):
        """Test that address.* notation is properly converted to nested object"""
        user_ops = UserBulkOperations(mock_client)

        row = {
            "operation": "user.create",
            "serviceProviderId": "TestServiceProvider",
            "groupId": "TestGroup",
            "userId": "test-user@test.com",
            "firstName": "Test",
            "lastName": "User",
            "callingLineIdFirstName": "Test",
            "callingLineIdLastName": "User",
            "extension": "1234",
            "password": "password123",
            "address.addressLine1": "123 Main Street",
            "address.city": "Tokyo",
            "address.country": "Japan",
        }

        result = user_ops._process_row(row)

        assert "address" in result
        assert result["address"]["address_line1"] == "123 Main Street"
        assert result["address"]["city"] == "Tokyo"
        assert result["address"]["country"] == "Japan"

    def test_nested_array_processing(self, mock_client):
        """Test that alternateUserId[0].alternateUserId notation is properly converted to nested array"""
        user_ops = UserBulkOperations(mock_client)

        row = {
            "operation": "user.create",
            "serviceProviderId": "TestServiceProvider",
            "groupId": "TestGroup",
            "userId": "test-user@test.com",
            "firstName": "Test",
            "lastName": "User",
            "callingLineIdFirstName": "Test",
            "callingLineIdLastName": "User",
            "extension": "1234",
            "password": "password123",
            "alternateUserId[0].alternateUserId": "altuser1",
            "alternateUserId[1].alternateUserId": "altuser2",
        }

        result = user_ops._process_row(row)

        assert "alternate_user_id" in result
        assert result["alternate_user_id"] == [{"alternate_user_id": "altuser1"}, {"alternate_user_id": "altuser2"}]

    def test_boolean_conversion(self, mock_client):
        """Test that boolean values are properly converted from strings"""
        user_ops = UserBulkOperations(mock_client)

        row = {
            "operation": "user.create",
            "serviceProviderId": "TestServiceProvider",
            "groupId": "TestGroup",
            "userId": "test-user@test.com",
            "firstName": "Test",
            "lastName": "User",
            "callingLineIdFirstName": "Test",
            "callingLineIdLastName": "User",
            "extension": "1234",
            "password": "password123",
            "accessDeviceEndpoint.useCustomUserNamePassword": "true",
            "accessDeviceEndpoint.useHotline": "false",
        }

        result = user_ops._process_row(row)

        assert result["access_device_endpoint"]["use_custom_user_name_password"] is True
        assert result["access_device_endpoint"]["use_hotline"] is False

    def test_integer_conversion(self, mock_client):
        """Test that integer fields are properly converted from strings"""
        user_ops = UserBulkOperations(mock_client)

        row = {
            "operation": "user.create",
            "serviceProviderId": "TestServiceProvider",
            "groupId": "TestGroup",
            "userId": "test-user@test.com",
            "firstName": "Test",
            "lastName": "User",
            "callingLineIdFirstName": "Test",
            "callingLineIdLastName": "User",
            "extension": "1234",
            "password": "password123",
            "accessDeviceEndpoint.portNumber": "5060",
        }

        result = user_ops._process_row(row)

        assert result["access_device_endpoint"]["port_number"] == 5060

    def test_defaults_application(self, mock_client):
        """Test that defaults are properly applied when not provided"""
        user_ops = UserBulkOperations(mock_client)
        mock_response = Mock()
        mock_client.command.return_value = mock_response

        data = [
            {
                "operation": "user.create",
                "service_provider_id": "TestServiceProvider",
                "group_id": "TestGroup",
                "user_id": "test-user@test.com",
                "first_name": "Test",
                "last_name": "User",
                "calling_line_id_first_name": "Test",
                "calling_line_id_last_name": "User",
                "extension": "1234",
                "password": "password123",
            }
        ]

        results = user_ops.execute_from_data(data, dry_run=False)

        assert len(results) == 1
        assert results[0]["success"]
        # Check that no defaults are applied (users have no defaults configured)
        result_data = results[0]["data"]
        assert result_data["first_name"] == "Test"
        assert result_data["last_name"] == "User"

    def test_dry_run_mode(self, mock_client):
        """Test dry run doesn't make API calls"""
        user_ops = UserBulkOperations(mock_client)

        data = [
            {
                "operation": "user.create",
                "service_provider_id": "TestServiceProvider",
                "group_id": "TestGroup",
                "user_id": "test-user@test.com",
                "first_name": "Test",
                "last_name": "User",
                "calling_line_id_first_name": "Test",
                "calling_line_id_last_name": "User",
                "extension": "1234",
                "password": "password123",
            }
        ]

        results = user_ops.execute_from_data(data, dry_run=True)

        assert len(results) == 1
        assert results[0]["success"] 
        mock_client.command.assert_not_called()

    def test_case_conversion(self, mock_client):
        """Test that camelCase is converted to snake_case"""
        user_ops = UserBulkOperations(mock_client)

        row = {
            "operation": "user.create",
            "serviceProviderId": "TestServiceProvider",
            "groupId": "TestGroup",
            "userId": "test-user@test.com",
            "firstName": "Test",
            "lastName": "User",
            "callingLineIdFirstName": "Test",
            "callingLineIdLastName": "User",
            "extension": "1234",
            "password": "password123",
            "accessDeviceEndpoint.useCustomUserNamePassword": "true",
            "accessDeviceEndpoint.portNumber": "5060",
        }

        result = user_ops._process_row(row)

        assert "service_provider_id" in result
        assert "group_id" in result
        assert "user_id" in result
        assert "first_name" in result
        assert "last_name" in result
        assert "calling_line_id_first_name" in result
        assert "calling_line_id_last_name" in result
        assert "access_device_endpoint" in result
        assert "use_custom_user_name_password" in result["access_device_endpoint"]
        assert "port_number" in result["access_device_endpoint"]
