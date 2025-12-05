from mercury_ocip.bulk.base_operation import BaseBulkOperations
from mercury_ocip.client import BaseClient


class GroupAdminBulkOperations(BaseBulkOperations):
    """Group Admin operations

    This class is used to handle all bulk group admin operations.

    Inherits from BaseBulkOperations which contains client needed for the operations
    """

    def __init__(self, client: BaseClient) -> None:
        super().__init__(client)

        self.operation_mapping = {
            "group.admin.create": {
                "command": "GroupAdminAddRequest",
                # "nested_types": {},
                # "defaults": {},
                # "integer_fields": {},
            },
            "group.admin.modify.policy": {
                "command": "GroupAdminModifyPolicyRequest",
                "defaults": {
                    "profile_access": "Read-Only",
                    "user_access": "Full",
                    "admin_access": "Read-Only",
                    "department_access": "Full",
                    "access_device_access": "Read-Only",
                    "enhanced_service_instance_access": "Modify-Only",
                    "feature_access_code_access": "Read-Only",
                    "phone_number_extension_access": "Read-Only",
                    "calling_line_id_number_access": "Full",
                    "service_access": "Read-Only",
                    "trunk_group_access": "Full",
                    "session_admission_control_access": "Read-Only",
                    "office_zone_access": "Read-Only",
                    "number_activation_access": "None",
                    "dialable_caller_id_access": "Read-Only",
                },
            },
        }
