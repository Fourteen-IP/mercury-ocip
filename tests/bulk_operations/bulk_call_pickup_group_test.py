import pytest
import tempfile
import os
from unittest.mock import Mock

from mercury_ocip.client import Client
from mercury_ocip.bulk.call_pickup import CallPickupBulkOperations
from mercury_ocip.commands.commands import GroupCallPickupAddInstanceRequest


class TestCallPickupBulkOperations:
    """Simple tests for call pickup bulk operations"""

    @pytest.fixture
    def mock_client(self):
        """Mock client with dispatch table"""
        client = Mock(spec=Client)
        client._dispatch_table = {
            "GroupCallPickupAddInstanceRequest": GroupCallPickupAddInstanceRequest,
        }
        return client

    def test_csv_flow_with_template_file(self, mock_client):
        """Test CSV processing using the actual template file"""
        # Create temp CSV with template format
        csv_content = """operation,serviceProviderId,groupId,name,userId[0],userId[1],userId[2]
pickup.group.create,TestServiceProvider,SalesGroup,Sales Pickup Group,john.doe@test.com,jane.smith@test.com,bob.wilson@test.com"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_file = f.name

        try:
            call_pickup_ops = CallPickupBulkOperations(mock_client)
            mock_response = Mock()
            mock_client.command.return_value = mock_response

            results = call_pickup_ops.execute_from_csv(temp_file, dry_run=False)

            assert len(results) == 1
            assert results[0]["success"]
            assert results[0]["data"]["name"] == "Sales Pickup Group"
            assert results[0]["data"]["user_id"] == ["john.doe@test.com", "jane.smith@test.com", "bob.wilson@test.com"]
        finally:
            os.unlink(temp_file)

    def test_direct_method_call_flow(self, mock_client):
        """Test direct method call with data array"""
        call_pickup_ops = CallPickupBulkOperations(mock_client)
        mock_response = Mock()
        mock_client.command.return_value = mock_response

        data = [
            {
                "operation": "pickup.group.create",
                "service_provider_id": "TestServiceProvider",
                "group_id": "TestGroup",
                "name": "Test Pickup Group",
                "user_id": ["user1@test.com", "user2@test.com"],
            }
        ]

        results = call_pickup_ops.execute_from_data(data, dry_run=False)

        assert len(results) == 1
        assert results[0]["success"]
        assert results[0]["data"]["name"] == "Test Pickup Group"

    def test_array_notation_processing(self, mock_client):
        """Test that userId[0], userId[1] notation is properly converted to array"""
        call_pickup_ops = CallPickupBulkOperations(mock_client)

        row = {
            "operation": "pickup.group.create",
            "serviceProviderId": "TestServiceProvider",
            "groupId": "TestGroup",
            "name": "Test Pickup Group",
            "userId[0]": "user1@test.com",
            "userId[1]": "user2@test.com",
        }

        result = call_pickup_ops._process_row(row)

        assert result["user_id"] == ["user1@test.com", "user2@test.com"]
        assert "userId[0]" not in result
        assert "userId[1]" not in result

    def test_dry_run_mode(self, mock_client):
        """Test dry run doesn't make API calls"""
        call_pickup_ops = CallPickupBulkOperations(mock_client)

        data = [
            {
                "operation": "pickup.group.create",
                "service_provider_id": "TestServiceProvider",
                "group_id": "TestGroup",
                "name": "Test Pickup Group",
                "user_id": ["user1@test.com"],
            }
        ]

        results = call_pickup_ops.execute_from_data(data, dry_run=True)

        assert len(results) == 1
        assert results[0]["success"] 
        mock_client.command.assert_not_called()
