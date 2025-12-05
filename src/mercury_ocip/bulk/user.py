from mercury_ocip.bulk.base_operation import BaseBulkOperations
from mercury_ocip.client import BaseClient


class UserBulkOperations(BaseBulkOperations):
    """Bulk user operations

    This class is used to handle all bulk user operations.

    Inherits from BaseBulkOperations which contains client needed for the operations
    """

    def __init__(self, client: BaseClient) -> None:
        super().__init__(client)

        self.operation_mapping = {
            "user.create": {
                "command": "UserConsolidatedAddRequest22",
                "nested_types": {
                    "alternate_user_id": "AlternateUserIdEntry",
                    "service_pack": "ConsolidatedServicePackAssignment",
                    "user_service": "ConsolidatedServicePackAssignment",
                    "sip_authentication_data": "SIPAuthenticationUserNamePassword",
                    "address": "StreetAddress",
                    "shared_call_appearance_access_device_endpoint": "ConsolidatedSharedCallAppearanceAccessDeviceMultipleIdentityEndpointAdd22",
                    "access_device_endpoint": {
                        "ConsolidatedAccessDeviceMultipleIdentityEndpointAndContactAdd22": {
                            "access_device": "AccessDevice",
                            "access_device_credentials": "DeviceManagementUserNamePassword16",
                        }
                    },
                    "trunk_addressing": {
                        "TrunkAddressingMultipleContactAdd": {
                            "trunk_group_device_endpoint": "TrunkGroupDeviceMultipleContactEndpointAdd"
                        }
                    },
                },
                # "defaults": {},
                "integer_fields": [
                    "access_device_endpoint.port",
                    "access_device_endpoint.port_number",
                ],
            },
            "user.modify": {
                "command": "UserConsolidatedModifyRequest22",
                "nested_types": {
                    "service_pack_list": {
                        "ReplacementConsolidatedServicePackAssignmentList": {
                            "service_pack": "ConsolidatedServicePackAssignment"
                        }
                    }
                },
            },
        }
