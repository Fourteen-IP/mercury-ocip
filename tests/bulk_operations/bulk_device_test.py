import pytest
import tempfile
import os
from unittest.mock import Mock

from mercury_ocip.client import Client
from mercury_ocip.bulk.device import DeviceBulkOperations
from mercury_ocip.commands.commands import GroupAccessDeviceAddRequest22V2, DeviceManagementUserNamePassword16


class TestDeviceBulkOperations:
    """Simple tests for device bulk operations"""

    @pytest.fixture
    def mock_client(self):
        """Mock client with dispatch table"""
        client = Mock(spec=Client)
        client._dispatch_table = {
            "GroupAccessDeviceAddRequest22V2": GroupAccessDeviceAddRequest22V2,
            "DeviceManagementUserNamePassword16": DeviceManagementUserNamePassword16,
        }
        return client

    def test_csv_flow_with_template_file(self, mock_client):
        """Test CSV processing using the actual template format"""
        # Create temp CSV with template format
        csv_content = """operation,serviceProviderId,groupId,deviceType,deviceName,transportProtocol,netAddress,port,macAddress,serialNumber,description,physicalLocation,useCustomUserNamePassword,accessDeviceCredentials.userName,accessDeviceCredentials.password
device.group.create,TestServiceProvider,SalesGroup,Polycom VVX 450,sales-phone-01,UDP,192.168.1.100,5060,00:11:22:33:44:55,SN123456789,Sales floor phone 1,Building A Floor 2,true,salesphone01,SecurePass123"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_file = f.name

        try:
            device_ops = DeviceBulkOperations(mock_client)
            mock_response = Mock()
            mock_client.command.return_value = mock_response

            results = device_ops.execute_from_csv(temp_file, dry_run=False)

            assert len(results) == 1
            assert results[0]["success"]
            assert results[0]["data"]["device_name"] == "sales-phone-01"
            assert results[0]["data"]["device_type"] == "Polycom VVX 450"
        finally:
            os.unlink(temp_file)

    def test_direct_method_call_flow(self, mock_client):
        """Test direct method call with data array"""
        device_ops = DeviceBulkOperations(mock_client)
        mock_response = Mock()
        mock_client.command.return_value = mock_response

        data = [
            {
                "operation": "device.group.create",
                "service_provider_id": "TestServiceProvider",
                "group_id": "TestGroup",
                "device_type": "Polycom VVX 450",
                "device_name": "test-phone-01",
                "transport_protocol": "UDP",
                "net_address": "192.168.1.100",
                "port": 5060,
                "mac_address": "00:11:22:33:44:55",
                "serial_number": "SN123456789",
                "description": "Test phone",
                "physical_location": "Test location",
                "use_custom_user_name_password": True,
                "access_device_credentials": {
                    "user_name": "testphone01",
                    "password": "TestPass123"
                }
            }
        ]

        results = device_ops.execute_from_data(data, dry_run=False)

        assert len(results) == 1
        assert results[0]["success"]
        assert results[0]["data"]["device_name"] == "test-phone-01"
        assert results[0]["data"]["device_type"] == "Polycom VVX 450"

    def test_nested_object_processing(self, mock_client):
        """Test that accessDeviceCredentials.* notation is properly converted to nested object"""
        device_ops = DeviceBulkOperations(mock_client)

        row = {
            "operation": "device.group.create",
            "serviceProviderId": "TestServiceProvider",
            "groupId": "TestGroup",
            "deviceType": "Polycom VVX 450",
            "deviceName": "test-phone-01",
            "accessDeviceCredentials.userName": "testuser",
            "accessDeviceCredentials.password": "testpass",
        }

        result = device_ops._process_row(row)

        assert "access_device_credentials" in result
        assert result["access_device_credentials"]["user_name"] == "testuser"
        assert result["access_device_credentials"]["password"] == "testpass"

    def test_boolean_conversion(self, mock_client):
        """Test that boolean values are properly converted from strings"""
        device_ops = DeviceBulkOperations(mock_client)

        row = {
            "operation": "device.group.create",
            "serviceProviderId": "TestServiceProvider",
            "groupId": "TestGroup",
            "deviceType": "Polycom VVX 450",
            "deviceName": "test-phone-01",
            "useCustomUserNamePassword": "true",
        }

        result = device_ops._process_row(row)

        assert result["use_custom_user_name_password"] is True

    def test_boolean_conversion_false(self, mock_client):
        """Test that boolean false values are properly converted"""
        device_ops = DeviceBulkOperations(mock_client)

        row = {
            "operation": "device.group.create",
            "serviceProviderId": "TestServiceProvider",
            "groupId": "TestGroup",
            "deviceType": "Polycom VVX 450",
            "deviceName": "test-phone-01",
            "useCustomUserNamePassword": "false",
        }

        result = device_ops._process_row(row)

        assert result["use_custom_user_name_password"] is False

    def test_no_defaults_application(self, mock_client):
        """Test that devices work without defaults (minimal config)"""
        device_ops = DeviceBulkOperations(mock_client)
        mock_response = Mock()
        mock_client.command.return_value = mock_response

        data = [
            {
                "operation": "device.group.create",
                "service_provider_id": "TestServiceProvider",
                "group_id": "TestGroup",
                "device_type": "Polycom VVX 450",
                "device_name": "test-phone-01",
            }
        ]

        results = device_ops.execute_from_data(data, dry_run=False)

        assert len(results) == 1
        assert results[0]["success"]
        # Verify no unexpected defaults were added
        result_data = results[0]["data"]
        assert "transport_protocol" not in result_data
        assert "net_address" not in result_data
        assert "port" not in result_data

    def test_dry_run_mode(self, mock_client):
        """Test dry run doesn't make API calls"""
        device_ops = DeviceBulkOperations(mock_client)

        data = [
            {
                "operation": "device.group.create",
                "service_provider_id": "TestServiceProvider",
                "group_id": "TestGroup",
                "device_type": "Polycom VVX 450",
                "device_name": "test-phone-01",
            }
        ]

        results = device_ops.execute_from_data(data, dry_run=True)

        assert len(results) == 1
        assert results[0]["success"]
        mock_client.command.assert_not_called()

    def test_case_conversion(self, mock_client):
        """Test that camelCase is converted to snake_case"""
        device_ops = DeviceBulkOperations(mock_client)

        row = {
            "operation": "device.group.create",
            "serviceProviderId": "TestServiceProvider",
            "groupId": "TestGroup",
            "deviceType": "Polycom VVX 450",
            "deviceName": "test-phone-01",
            "transportProtocol": "UDP",
            "netAddress": "192.168.1.100",
            "macAddress": "00:11:22:33:44:55",
            "serialNumber": "SN123456789",
            "physicalLocation": "Test Location",
            "useCustomUserNamePassword": "true",
        }

        result = device_ops._process_row(row)

        assert "service_provider_id" in result
        assert "group_id" in result
        assert "device_type" in result
        assert "device_name" in result
        assert "transport_protocol" in result
        assert "net_address" in result
        assert "mac_address" in result
        assert "serial_number" in result
        assert "physical_location" in result
        assert "use_custom_user_name_password" in result

    def test_optional_fields_filtering(self, mock_client):
        """Test that empty/None values are filtered out"""
        device_ops = DeviceBulkOperations(mock_client)

        row = {
            "operation": "device.group.create",
            "serviceProviderId": "TestServiceProvider",
            "groupId": "TestGroup",
            "deviceType": "Polycom VVX 450",
            "deviceName": "test-phone-01",
            "transportProtocol": "",
            "netAddress": "None",
            "port": "",
        }

        result = device_ops._process_row(row)

        assert "transport_protocol" not in result
        assert "net_address" not in result
        assert "port" not in result
        assert result["device_name"] == "test-phone-01"

    def test_full_device_configuration(self, mock_client):
        """Test device creation with all fields populated"""
        device_ops = DeviceBulkOperations(mock_client)
        mock_response = Mock()
        mock_client.command.return_value = mock_response

        data = [
            {
                "operation": "device.group.create",
                "service_provider_id": "TestServiceProvider",
                "group_id": "SalesGroup",
                "device_type": "Polycom VVX 450",
                "device_name": "sales-phone-01",
                "transport_protocol": "TLS",
                "net_address": "phone.domain.com",
                "port": 5061,
                "outbound_proxy_server_net_address": "proxy.domain.com",
                "stun_server_net_address": "stun.domain.com",
                "mac_address": "00:11:22:33:44:55",
                "serial_number": "SN123456789",
                "description": "Sales floor phone 1",
                "physical_location": "Building A, Floor 2, Desk 15",
                "use_custom_user_name_password": True,
                "access_device_credentials": {
                    "user_name": "salesphone01",
                    "password": "SecurePass123"
                }
            }
        ]

        results = device_ops.execute_from_data(data, dry_run=False)

        assert len(results) == 1
        assert results[0]["success"]
        result_data = results[0]["data"]
        assert result_data["device_name"] == "sales-phone-01"
        assert result_data["transport_protocol"] == "TLS"
        assert result_data["net_address"] == "phone.domain.com"
        assert result_data["port"] == 5061
        assert result_data["mac_address"] == "00:11:22:33:44:55"
        assert result_data["access_device_credentials"]["user_name"] == "salesphone01"

    def test_device_without_credentials(self, mock_client):
        """Test device creation without custom credentials"""
        device_ops = DeviceBulkOperations(mock_client)
        mock_response = Mock()
        mock_client.command.return_value = mock_response

        data = [
            {
                "operation": "device.group.create",
                "service_provider_id": "TestServiceProvider",
                "group_id": "TestGroup",
                "device_type": "Cisco 8851",
                "device_name": "test-phone-02",
                "use_custom_user_name_password": False,
            }
        ]

        results = device_ops.execute_from_data(data, dry_run=False)

        assert len(results) == 1
        assert results[0]["success"]
        assert results[0]["data"]["use_custom_user_name_password"] is False
        assert "access_device_credentials" not in results[0]["data"]

    def test_multiple_devices_from_csv(self, mock_client):
        """Test creating multiple devices from CSV"""
        csv_content = """operation,serviceProviderId,groupId,deviceType,deviceName,transportProtocol,macAddress
device.group.create,TestServiceProvider,SalesGroup,Polycom VVX 450,sales-phone-01,UDP,00:11:22:33:44:55
device.group.create,TestServiceProvider,SalesGroup,Polycom VVX 450,sales-phone-02,TCP,AA:BB:CC:DD:EE:FF
device.group.create,TestServiceProvider,SupportGroup,Cisco 8851,support-phone-01,TLS,11:22:33:44:55:66"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_file = f.name

        try:
            device_ops = DeviceBulkOperations(mock_client)
            mock_response = Mock()
            mock_client.command.return_value = mock_response

            results = device_ops.execute_from_csv(temp_file, dry_run=False)

            assert len(results) == 3
            assert all(result["success"] for result in results)
            assert results[0]["data"]["device_name"] == "sales-phone-01"
            assert results[1]["data"]["device_name"] == "sales-phone-02"
            assert results[2]["data"]["device_name"] == "support-phone-01"
            assert results[0]["data"]["transport_protocol"] == "UDP"
            assert results[1]["data"]["transport_protocol"] == "TCP"
            assert results[2]["data"]["transport_protocol"] == "TLS"
        finally:
            os.unlink(temp_file)

