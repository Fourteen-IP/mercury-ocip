from mercury_ocip.bulk.base_operation import BaseBulkOperations
from mercury_ocip.client import BaseClient


class AutoAttendantBulkOperations(BaseBulkOperations):
    """Bulk auto attendant operations

    This class is used to handle all bulk auto attendant operations.

    Inherits from BaseBulkOperations which contains client needed for the operations
    """

    def __init__(self, client: BaseClient) -> None:
        super().__init__(client)

        self.operation_mapping = {
            "auto.attendant.create": {
                "command": "GroupAutoAttendantConsolidatedAddInstanceRequest",
                "nested_types": {
                    "service_instance_profile": "ServiceInstanceAddProfile",
                },
                "defaults": {
                    "service_instance_profile": {
                        "name": "Default Auto Attendant Name",
                        "calling_line_id_last_name": "Last Name",
                        "calling_line_id_first_name": "First Name",
                    },
                    "type": "Basic",
                    "first_digit_timeout_seconds": 10,
                    "enable_video": False,
                    "extension_dialing_scope": "Group",
                    "name_dialing_scope": "Group",
                    "name_dialing_entries": "LastName + FirstName",
                    "is_active": True,
                },
                "integer_fields": ["first_digit_timeout_seconds"],
            },
        }
