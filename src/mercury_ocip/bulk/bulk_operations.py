from typing import List, Dict, Any

from mercury_ocip.bulk.call_pickup import CallPickupBulkOperations
from mercury_ocip.bulk.call_center import CallCenterBulkOperations
from mercury_ocip.bulk.hunt_group import HuntGroupBulkOperations
from mercury_ocip.bulk.auto_attendant import AutoAttendantBulkOperations
from mercury_ocip.bulk.device import DeviceBulkOperations
from mercury_ocip.bulk.user import UserBulkOperations
from mercury_ocip.bulk.administrator import AdminBulkOperations


class BulkOperations:
    """Main bulk operations handler

    Gateway class for all bulk operations for better ux.

    Inherits from BaseBulkOperations which contains client needed for the operations

    Args:
        client (BaseClient): Client object to be used in the scripts.
    """

    def __init__(self, client):
        self.client = client
        self.logger = client.logger
        self.call_center = CallCenterBulkOperations(client)
        self.call_pickup = CallPickupBulkOperations(client)
        self.hunt_group = HuntGroupBulkOperations(client)
        self.auto_attendant = AutoAttendantBulkOperations(client)
        self.devices = DeviceBulkOperations(client)
        self.users = UserBulkOperations(client)
        self.administrator = AdminBulkOperations(client)
        self.logger.debug("BulkOperations initialized")

    # Call Pickup
    def create_call_pickup_from_csv(
        self, csv_path: str, dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        return self.call_pickup.execute_from_csv(csv_path, dry_run)

    def create_call_pickup_from_data(
        self, call_pickup_data: List[Dict[str, Any]], dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        return self.call_pickup.execute_from_data(call_pickup_data, dry_run)

    # Hunt Group
    def create_hunt_group_from_csv(
        self, csv_path: str, dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        return self.hunt_group.execute_from_csv(csv_path, dry_run)

    def create_hunt_group_from_data(
        self, hunt_group_data: List[Dict[str, Any]], dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        return self.hunt_group.execute_from_data(hunt_group_data, dry_run)

    # Call Center
    def create_call_center_from_csv(
        self, csv_path: str, dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        return self.call_center.execute_from_csv(csv_path, dry_run)

    def create_call_center_from_data(
        self, call_center_data: List[Dict[str, Any]], dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        return self.call_center.execute_from_data(call_center_data, dry_run)

    # Auto Attendant
    def create_auto_attendant_from_csv(
        self, csv_path: str, dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        return self.auto_attendant.execute_from_csv(csv_path, dry_run)

    def create_auto_attendant_from_data(
        self, auto_attendant_data: List[Dict[str, Any]], dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        return self.auto_attendant.execute_from_data(auto_attendant_data, dry_run)

    # Device
    def create_device_from_csv(
        self, csv_path: str, dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        return self.devices.execute_from_csv(csv_path, dry_run)

    def create_device_from_data(
        self, device_data: List[Dict[str, Any]], dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        return self.devices.execute_from_data(device_data, dry_run)

    # User
    def create_user_from_csv(
        self, csv_path: str, dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        return self.users.execute_from_csv(csv_path, dry_run)

    def create_users_from_data(
        self, user_data: List[Dict[str, Any]], dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        return self.users.execute_from_data(user_data, dry_run)

    def modify_user_from_csv(
        self, csv_path: str, dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        return self.users.execute_from_csv(csv_path, dry_run)

    def modify_user_from_data(
        self, user_data: List[Dict[str, Any]], dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        return self.users.execute_from_data(user_data, dry_run)

    # Group Admin
    def create_group_admin_from_csv(
        self, csv_path: str, dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        return self.administrator.execute_from_csv(csv_path, dry_run)

    def create_group_admin_from_data(
        self, group_admin_data: List[Dict[str, Any]], dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        return self.administrator.execute_from_data(group_admin_data, dry_run)

    # Group Admin Modify Policy
    def modify_group_admin_policy_from_csv(
        self, csv_path: str, dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        return self.administrator.execute_from_csv(csv_path, dry_run)

    def modify_group_admin_policy_from_data(
        self, group_admin_policy_data: List[Dict[str, Any]], dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        return self.administrator.execute_from_data(group_admin_policy_data, dry_run)

    # Service Provider Admin
    def create_service_provider_admin_from_csv(
        self, csv_path: str, dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        return self.administrator.execute_from_csv(csv_path, dry_run)

    def create_service_provider_from_data(
        self, group_admin_data: List[Dict[str, Any]], dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        return self.administrator.execute_from_data(group_admin_data, dry_run)

    # Delete Service Provider Admin
    def delete_service_provider_admin_from_csv(
        self, csv_path: str, dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        return self.administrator.execute_from_csv(csv_path, dry_run)

    def delete_service_provider_admin_from_data(
        self, group_admin_data: List[Dict[str, Any]], dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        return self.administrator.execute_from_data(group_admin_data, dry_run)

    # Service Provider Admin Modify Policy
    def modify_service_provider_admin_policy_from_csv(
        self, csv_path: str, dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        return self.administrator.execute_from_csv(csv_path, dry_run)

    def modify_service_provider_admin_policy_from_data(
        self, group_admin_policy_data: List[Dict[str, Any]], dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        return self.administrator.execute_from_data(group_admin_policy_data, dry_run)
