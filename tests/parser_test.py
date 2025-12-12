from mercury_ocip.commands.commands import AnnouncementFileLevelKey
from mercury_ocip.commands.commands import AutoAttendantKeyConfigurationEntry20
from mercury_ocip.commands.commands import AutoAttendantKeyConfiguration20
from mercury_ocip.commands.commands import AutoAttendantAddMenu20
from mercury_ocip.commands.commands import ServiceInstanceAddProfile
from typing import Any
import pytest
from unittest.mock import Mock
from mercury_ocip.utils.parser import Parser
from dataclasses import dataclass, field
from mercury_ocip.commands.commands import UserConsolidatedModifyRequest22, ReplacementConsolidatedServicePackAssignmentList, ConsolidatedServicePackAssignment, GroupAutoAttendantAddInstanceRequest20

def test_parser_to_xml_from_class():
    command = UserConsolidatedModifyRequest22(user_id="testuser")
    xml_output = Parser.to_xml_from_class(command)
    assert "<userId>testuser</userId>" in xml_output

def test_parser_to_xml_from_class_nested_types():
    command = UserConsolidatedModifyRequest22(
        user_id="Test",
        service_pack_list=ReplacementConsolidatedServicePackAssignmentList(
            service_pack=[
                ConsolidatedServicePackAssignment(
                    service_pack_name="ServicePack", authorized_quantity=1
                ),
                ConsolidatedServicePackAssignment(
                    service_pack_name="ServicePack2", authorized_quantity=1
                ),
            ]
        )
    )
    
    command = command.to_xml()

    assert command == "<command xmlns=\"\" xmlns:C=\"http://www.w3.org/2001/XMLSchema-instance\" C:type=\"UserConsolidatedModifyRequest22\"><userId>Test</userId><servicePackList><servicePack><servicePackName>ServicePack</servicePackName><authorizedQuantity>1</authorizedQuantity></servicePack><servicePack><servicePackName>ServicePack2</servicePackName><authorizedQuantity>1</authorizedQuantity></servicePack></servicePackList></command>"

def test_parser_to_class_from_xml():
    xml_input = """
    <command xmlns="" xmlns:C="http://www.w3.org/2001/XMLSchema-instance" C:type="UserConsolidatedModifyRequest22">
        <userId>testuser</userId>
    </command>
    """
    command_instance = Parser.to_class_from_xml(xml_input, UserConsolidatedModifyRequest22)
    assert isinstance(command_instance, UserConsolidatedModifyRequest22)
    assert command_instance.user_id == "testuser"

def test_parser_to_class_from_xml_with_nested_types():
    xml_input = """
    <command xmlns="" xmlns:C="http://www.w3.org/2001/XMLSchema-instance" C:type="UserConsolidatedModifyRequest22">
        <userId>Test</userId>
        <servicePackList>
            <servicePack>
                <servicePackName>ServicePack</servicePackName>
                <authorizedQuantity>1</authorizedQuantity>
            </servicePack>
            <servicePack>
                <servicePackName>ServicePack2</servicePackName>
                <authorizedQuantity>1</authorizedQuantity>
            </servicePack>
        </servicePackList>
    </command>
    """
    command_instance = Parser.to_class_from_xml(xml_input, UserConsolidatedModifyRequest22)
    
    assert isinstance(command_instance, UserConsolidatedModifyRequest22)
    assert command_instance.user_id == "Test"
    assert isinstance(command_instance.service_pack_list, ReplacementConsolidatedServicePackAssignmentList)
    assert len(command_instance.service_pack_list.service_pack) == 2
    assert command_instance.service_pack_list.service_pack[0].service_pack_name == "ServicePack"
    assert command_instance.service_pack_list.service_pack[1].service_pack_name == "ServicePack2"

def test_parser_to_dict_from_class():
    command = UserConsolidatedModifyRequest22(user_id="testuser")
    dict_output = Parser.to_dict_from_class(command)
    assert dict_output["user_id"] == "testuser"

def test_parser_to_class_from_dict():
    dict_input = {"user_id": "testuser"}
    command_instance = Parser.to_class_from_dict(dict_input, UserConsolidatedModifyRequest22)
    assert isinstance(command_instance, UserConsolidatedModifyRequest22)
    assert command_instance.user_id == "testuser"

def test_parser_to_class_from_dict_with_nested_types():
    dict_input = {
        "user_id": "Test",
        "service_pack_list": {
            "service_pack": [
                {
                    "service_pack_name": "ServicePack",
                    "authorized_quantity": 1
                },
                {
                    "service_pack_name": "ServicePack2",
                    "authorized_quantity": 1
                }
            ]
        }
    }
    command_instance = Parser.to_class_from_dict(dict_input, UserConsolidatedModifyRequest22)
    
    assert isinstance(command_instance, UserConsolidatedModifyRequest22)
    assert command_instance.user_id == "Test"
    assert isinstance(command_instance.service_pack_list, ReplacementConsolidatedServicePackAssignmentList)
    assert len(command_instance.service_pack_list.service_pack) == 2
    assert command_instance.service_pack_list.service_pack[0].service_pack_name == "ServicePack"
    assert command_instance.service_pack_list.service_pack[1].service_pack_name == "ServicePack2"

def test_parser_to_dict_from_class_with_nested_types():
    command = UserConsolidatedModifyRequest22(
        user_id="Test",
        service_pack_list=ReplacementConsolidatedServicePackAssignmentList(
            service_pack=[
                ConsolidatedServicePackAssignment(
                    service_pack_name="ServicePack", authorized_quantity=1
                ),
                ConsolidatedServicePackAssignment(
                    service_pack_name="ServicePack2", authorized_quantity=1
                ),
            ]
        )
    )
    dict_output = Parser.to_dict_from_class(command)
    
    assert dict_output["user_id"] == "Test"
    assert isinstance(dict_output["service_pack_list"], dict)
    assert len(dict_output["service_pack_list"]["service_pack"]) == 2
    assert dict_output["service_pack_list"]["service_pack"][0]["service_pack_name"] == "ServicePack"
    assert dict_output["service_pack_list"]["service_pack"][1]["service_pack_name"] == "ServicePack2"

def test_parser_large_nested_class_to_xml():
    command = GroupAutoAttendantAddInstanceRequest20(
    service_user_id="AutoAttendant1",
    group_id="TestGroup",
    service_provider_id="TestingNested",
    service_instance_profile=ServiceInstanceAddProfile(
        name="NestedProfile",
        calling_line_id_first_name="First",
        calling_line_id_last_name="Last",
    ),
    first_digit_timeout_seconds=1,
    enable_video=False,
    extension_dialing_scope="Group",
    name_dialing_scope="Group",
    name_dialing_entries=[],
    business_hours_menu=AutoAttendantAddMenu20(
        announcement_selection="Default",
        key_configuration=[
            AutoAttendantKeyConfiguration20(
                key="0",
                entry=AutoAttendantKeyConfigurationEntry20(
                    action="TransferToExtension",
                    audio_file=AnnouncementFileLevelKey(
                        name="File1", media_file_type="wav", level="Group"
                    ),
                ),
            ),
            AutoAttendantKeyConfiguration20(
                key="1",
                entry=AutoAttendantKeyConfigurationEntry20(
                    action="TransferToExtension",
                    audio_file=AnnouncementFileLevelKey(
                        name="File2", media_file_type="wav", level="Group"
                    ),
                ),
            ),
        ],
        enable_first_menu_level_extension_dialing=False,
    ),
)

    xml_output = Parser.to_xml_from_class(command)
    assert "<command xmlns=\"\" xmlns:C=\"http://www.w3.org/2001/XMLSchema-instance\" C:type=\"GroupAutoAttendantAddInstanceRequest20\"><serviceProviderId>TestingNested</serviceProviderId><groupId>TestGroup</groupId><serviceUserId>AutoAttendant1</serviceUserId><serviceInstanceProfile><name>NestedProfile</name><callingLineIdLastName>Last</callingLineIdLastName><callingLineIdFirstName>First</callingLineIdFirstName></serviceInstanceProfile><firstDigitTimeoutSeconds>1</firstDigitTimeoutSeconds><enableVideo>false</enableVideo><extensionDialingScope>Group</extensionDialingScope><nameDialingScope>Group</nameDialingScope><businessHoursMenu><announcementSelection>Default</announcementSelection><enableFirstMenuLevelExtensionDialing>false</enableFirstMenuLevelExtensionDialing><keyConfiguration><key>0</key><entry><action>TransferToExtension</action><audioFile><name>File1</name><mediaFileType>wav</mediaFileType><level>Group</level></audioFile></entry></keyConfiguration><keyConfiguration><key>1</key><entry><action>TransferToExtension</action><audioFile><name>File2</name><mediaFileType>wav</mediaFileType><level>Group</level></audioFile></entry></keyConfiguration></businessHoursMenu></command>" in xml_output

def test_parser_oci_table():
    