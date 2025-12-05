from mercury_ocip.bulk.base_operation import BaseBulkOperations
from mercury_ocip.client import BaseClient


class DeviceBulkOperations(BaseBulkOperations):
    """Bulk device operations

    This class is used to handle all bulk device operations.

    Inherits from BaseBulkOperations which contains client needed for the operations
    """

    def __init__(self, client: BaseClient) -> None:
        super().__init__(client)

        self.operation_mapping = {
            "device.group.create": {
                "command": "GroupAccessDeviceAddRequest22V2",
                "nested_types": {
                    "access_device_credentials": "DeviceManagementUserNamePassword16",
                },
                # "defaults": {},
                # "integer_fields": {},
            }
        }
