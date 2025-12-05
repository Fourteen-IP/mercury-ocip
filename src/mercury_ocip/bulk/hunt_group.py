from mercury_ocip.bulk.base_operation import BaseBulkOperations
from mercury_ocip.client import BaseClient


class HuntGroupBulkOperations(BaseBulkOperations):
    """Bulk hunt group operations

    This class is used to handle all bulk hunt group operations.

    Inherits from BaseBulkOperations which contains client needed for the operations
    """

    def __init__(self, client: BaseClient) -> None:
        super().__init__(client)

        self.operation_mapping = {
            "hunt.group.create": {
                "command": "GroupHuntGroupAddInstanceRequest20",
                "nested_types": {
                    "service_instance_profile": "ServiceInstanceAddProfile",
                },
                "defaults": {
                    "service_instance_profile": {
                        "name": "Test Group Name",
                        "calling_line_id_last_name": "Last Name",
                        "calling_line_id_first_name": "First Name",
                        "alias": [],
                    },
                    "policy": "Regular",
                    "hunt_after_no_answer": True,
                    "no_answer_number_of_rings": 5,
                    "forward_after_timeout": False,
                    "forward_timeout_seconds": 10,
                    "allow_call_waiting_for_agents": True,
                    "use_system_hunt_group_clid_setting": True,
                    "include_hunt_group_name_in_clid": True,
                    "enable_not_reachable_forwarding": False,
                    "make_busy_when_not_reachable": False,
                    "allow_members_to_control_group_busy": False,
                    "enable_group_busy": False,
                    "apply_group_busy_when_terminating_to_agent": False,
                    "agent_user_id": [],
                },
                "integer_fields": [
                    "no_answer_number_of_rings",
                    "forward_timeout_seconds",
                ],
            },
        }
