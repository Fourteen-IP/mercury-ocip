from mercury_ocip.bulk.base_operation import BaseBulkOperations
from mercury_ocip.client import BaseClient


class AdminBulkOperations(BaseBulkOperations):
    """Admin operations at all levels.

    This class is used to handle all bulk group admin operations.

    Inherits from BaseBulkOperations which contains client needed for the operations
    """

    def __init__(self, client: BaseClient) -> None:
        super().__init__(client)

        self.operation_mapping = {
            "service.provider.admin.create": {
                "command": "ServiceProviderAdminAddRequest14",
                # "nested_types": {},
                # "defaults": {},
                # "integer_fields": {},
            },
            "service.provider.admin.delete": {
                "command": "ServiceProviderAdminDeleteRequest",
            },
            "service.provider.admin.modify.policy": {
                "command": "ServiceProviderAdminModifyPolicyRequest14",
                "defaults": {
                    "profile_access": "Read-Only",
                    "group_access": "None",
                    "user_access": "Read-Only Profile",
                    "admin_access": "Read-Only",
                    "department_access": "Full",
                    "access_device_access": "Full",
                    "phone_number_extension_access": "Assign To Services and Users",
                    "calling_line_id_number_access": "Full",
                    "service_access": "No Authorization",
                    "service_pack_access": "None",
                    "session_admission_control_access": "Read-Only",
                    "web_branding_access": "Full",
                    "office_zone_access": "Full",
                    "communication_barring_access": "Read-Only",
                    "network_policy_access": "None",
                    "number_activation_access": "Full",
                    "dialable_caller_id_access": "Full",
                    "verify_translation_and_routing_access": "None",
                },
            },
            "group.admin.create": {
                "command": "GroupAdminAddRequest",
                # "nested_types": {},
                # "defaults": {},
                # "integer_fields": {},
            },
            "group.admin.delete": {
                "command": "GroupAdminDeleteRequest",
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
