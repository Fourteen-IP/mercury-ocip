from mercury_ocip.bulk.base_operation import BaseBulkOperations
from mercury_ocip.client import BaseClient


class CallCenterBulkOperations(BaseBulkOperations):
    """Bulk call center operations

    This class is used to handle all bulk call center operations.

    Inherits from BaseBulkOperations which contains client needed for the operations
    """

    def __init__(self, client: BaseClient) -> None:
        super().__init__(client)

        self.operation_mapping = {
            "call.center.create": {
                "command": "GroupCallCenterAddInstanceRequest22",
                "nested_types": {
                    "service_instance_profile": "ServiceInstanceAddProfileCallCenter",
                },
                "defaults": {
                    "service_instance_profile": {
                        "name": "Default Call Center Name",
                        "calling_line_id_last_name": "Default CLID Last Name",
                        "calling_line_id_first_name": "Default CLID First Name",
                    },
                    # Defaults fot a basic cc
                    "type": "Basic",
                    "policy": "Circular",
                    "enable_video": False,
                    "queue_length": 3,
                    "allow_caller_to_dial_escape_digit": False,
                    "escape_digit": "3",
                    "reset_call_statistics_upon_entry_in_queue": True,
                    "allow_agent_logoff": True,
                    "allow_call_waiting_for_agents": True,
                    "external_preferred_audio_codec": "None",
                    "internal_preferred_audio_codec": "None",
                    "play_ringing_when_offering_call": True,
                    # Standard CC
                    # "enable_reporting": False,
                    # "wrap_up_seconds": 30,
                    # "override_agent_wrap_up_time": False,
                    # "allow_calls_to_agents_in_wrap_up": True,
                    # "enable_automatic_state_change_for_agents": False,
                    # "agent_state_after_call": "Available",
                    # "agent_unavailable_code": "3",
                    # Premium CC
                    # "routing_type": "Priority Based",
                    # "force_delivery_of_calls": False,
                    # "force_delivery_wait_time_seconds": 9,
                },
                "integer_fields": [
                    "wrap_up_seconds",
                    "force_delivery_wait_time_seconds",
                    "queue_length",
                ],
            },
            "call.center.update.agent.list": {
                "command": "GroupCallCenterModifyAgentListRequest",
                "nested_types": {
                    "agent_user_id_list": "ReplacementUserIdList",
                },
                # "integer_fields": [],
                # "defaults": {},
            },
        }
