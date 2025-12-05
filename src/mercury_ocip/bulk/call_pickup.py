from mercury_ocip.bulk.base_operation import BaseBulkOperations
from mercury_ocip.client import BaseClient


class CallPickupBulkOperations(BaseBulkOperations):
    """Bulk call pickup operations

    This class is used to handle all bulk call pickup operations.

    Inherits from BaseBulkOperations which contains client needed for the operations
    """

    def __init__(self, client: BaseClient) -> None:
        super().__init__(client)

        self.operation_mapping = {
            "pickup.group.create": {
                "command": "GroupCallPickupAddInstanceRequest",
                # "nested_types": {},
                # "defaults": {},
                # "integer_fields": {}
            }
        }
