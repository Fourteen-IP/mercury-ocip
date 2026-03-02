from mercury_ocip.commands.base_command import Nillable, OCIType
from mercury_ocip.utils.parser import Parser
from mercury_ocip.commands.commands import (
   UserConsolidatedModifyRequest22, 
   ReplacementConsolidatedServicePackAssignmentList,
   ConsolidatedServicePackAssignment,
   GroupAutoAttendantAddInstanceRequest20,
   AnnouncementFileLevelKey,
   AutoAttendantKeyConfigurationEntry20,
   AutoAttendantKeyConfiguration20,
   AutoAttendantAddMenu20,
   ServiceInstanceAddProfile,
   GroupGetListInSystemResponse,
   AlternateNumberEntry21,
   OutgoingCallingPlanOriginatingDepartmentPermissionsModify,
   GroupDepartmentKey,
)
from mercury_ocip.commands.base_command import OCITable, OCITableRow

def test_parser_to_xml_from_class():
    command = UserConsolidatedModifyRequest22(user_id="testuser")
    xml_output = Parser.to_xml_from_class(command)
    assert "<userId>testuser</userId>" in xml_output

def test_parser_to_xml_from_class_nested_types_fixed():
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

    xml_output = Parser.to_xml_from_class(command)

    # Ensure the key pieces are present rather than asserting an exact string
    assert "<userId>Test</userId>" in xml_output
    assert "<servicePackList" in xml_output
    assert xml_output.count("<servicePack>") == 2
    assert "<servicePackName>ServicePack</servicePackName>" in xml_output
    assert "<servicePackName>ServicePack2</servicePackName>" in xml_output

def test_parser_to_xml_from_dict():
    dict_input = {
        "user_id": "Test",
        "service_pack_list": {
            "service_pack": [
                {"service_pack_name": "ServicePack", "authorized_quantity": 1},
                {"service_pack_name": "ServicePack2", "authorized_quantity": 1},
            ]
        }
    }
    xml_output = Parser.to_xml_from_dict(dict_input, UserConsolidatedModifyRequest22)
    assert "<userId>Test</userId>" in xml_output
    assert xml_output.count("<servicePack>") == 2
    assert "<servicePackName>ServicePack</servicePackName>" in xml_output

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

    print(dict_output)
    
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
    type="Standard",
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
    assert '<command xmlns="" xsi:type="GroupAutoAttendantAddInstanceRequest20"><serviceProviderId>TestingNested</serviceProviderId><groupId>TestGroup</groupId><serviceUserId>AutoAttendant1</serviceUserId><serviceInstanceProfile><name>NestedProfile</name><callingLineIdLastName>Last</callingLineIdLastName><callingLineIdFirstName>First</callingLineIdFirstName></serviceInstanceProfile><type>Standard</type><firstDigitTimeoutSeconds>1</firstDigitTimeoutSeconds><enableVideo>false</enableVideo><extensionDialingScope>Group</extensionDialingScope><nameDialingScope>Group</nameDialingScope><businessHoursMenu><announcementSelection>Default</announcementSelection><enableFirstMenuLevelExtensionDialing>false</enableFirstMenuLevelExtensionDialing><keyConfiguration><key>0</key><entry><action>TransferToExtension</action><audioFile><name>File1</name><mediaFileType>wav</mediaFileType><level>Group</level></audioFile></entry></keyConfiguration><keyConfiguration><key>1</key><entry><action>TransferToExtension</action><audioFile><name>File2</name><mediaFileType>wav</mediaFileType><level>Group</level></audioFile></entry></keyConfiguration></businessHoursMenu></command>' in xml_output

def test_parser_oci_table_to_dict_on_own():
    
    table = OCITable(
        col_heading=["Column1", "Column2"],
        row=[
            OCITableRow(["Column1_Row1", "Column2_Row1"]),
            OCITableRow(["Column1_Row2", "Column2_Row2"]),
        ]
    )

    dict_output = table.to_dict()

    assert dict_output[0]["column1"] == "Column1_Row1"
    assert dict_output[0]["column2"] == "Column2_Row1"
    assert dict_output[1]["column1"] == "Column1_Row2"
    assert dict_output[1]["column2"] == "Column2_Row2"

def test_parser_to_dict_from_class_with_oci_table():
    table = OCITable(
        col_heading=["Column1", "Column2"],
        row=[
            OCITableRow(["Column1_Row1", "Column2_Row1"]),
            OCITableRow(["Column1_Row2", "Column2_Row2"]),
        ]
    )

    command = GroupGetListInSystemResponse(
        group_table=table
    )

    dict_output = command.to_dict()

    assert dict_output["group_table"][0]["column1"] == "Column1_Row1"
    assert dict_output["group_table"][0]["column2"] == "Column2_Row1"
    assert dict_output["group_table"][1]["column1"] == "Column1_Row2"
    assert dict_output["group_table"][1]["column2"] == "Column2_Row2"
    
def test_to_dict_from_xml_parses_table_and_returns_ocitable():
    xml_input = """
    <command>
      <groupTable>
        <colHeading>Column1</colHeading>
        <colHeading>Column2</colHeading>
        <row><col>Column1_Row1</col><col>Column2_Row1</col></row>
        <row><col>Column1_Row2</col><col>Column2_Row2</col></row>
      </groupTable>
    </command>
    """
    result = Parser.to_dict_from_xml(xml_input)
    assert isinstance(result, dict)
    assert "groupTable" in result
    assert isinstance(result["groupTable"], OCITable)
    rows = result["groupTable"].to_dict()
    assert rows[0]["column1"] == "Column1_Row1"
    assert rows[1]["column2"] == "Column2_Row2"

def test_to_dict_from_xml_preserves_attributes_and_nil():
    xml_input = """
    <command xmlns:C="http://www.w3.org/2001/XMLSchema-instance">
      <phoneNumber C:nil="true"/>
      <other attr="value">text</other>
    </command>
    """
    result = Parser.to_dict_from_xml(xml_input)
    assert "phoneNumber" in result
    assert isinstance(result["phoneNumber"], dict)
    assert "attributes" in result["phoneNumber"]
    assert result["phoneNumber"]["attributes"].get("C:nil") == "true" or result["phoneNumber"]["attributes"].get("nil") == "true"
    assert result["other"] == "text"

def test_nillable_type_creates_null_field():
    ob = AlternateNumberEntry21(phone_number="").to_xml()
    assert ob == '<command xmlns="" xsi:type="AlternateNumberEntry21"><phoneNumber C:nil="true"/></command>'

def test_type_key_appended_to_inherited_objects():
    xml = OutgoingCallingPlanOriginatingDepartmentPermissionsModify(
            department_key=GroupDepartmentKey(
                service_provider_id="MyServiceProvider",
                group_id="MyGroup",
                name="MyDepartment",
            )
    ).to_xml()

    assert xml == '<command xmlns="" xsi:type="OutgoingCallingPlanOriginatingDepartmentPermissionsModify"><departmentKey xsi:type="GroupDepartmentKey"><serviceProviderId>MyServiceProvider</serviceProviderId><groupId>MyGroup</groupId><name>MyDepartment</name></departmentKey></command>'

    