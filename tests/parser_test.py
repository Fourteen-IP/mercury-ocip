import pytest
from unittest.mock import Mock
from mercury_ocip.utils.parser import Parser
import lxml

from mercury_ocip.commands.commands import AccessDevice as Example
from mercury_ocip.commands.commands import GroupCallCenterGetInstanceResponse22 as NestedExample
from mercury_ocip.commands.commands import ServiceInstanceReadProfile19sp1 as NestedType

@pytest.fixture
def mock_class_to_dict():
    cls = Example(
        device_level="10",
        device_name="mydevice"
    )

    dictionary = Parser.to_dict_from_class(cls)

    assert isinstance(dictionary, dict)
    assert dictionary.get("device_level") == "10"
    assert dictionary.get("device_name") == "mydevice"

@pytest.fixture
def mock_class_to_xml():
    cls = Example(
        device_level="10",
        device_name="mydevice"
    )

    xml = Parser.to_xml_from_class(cls)

    assert isinstance(xml, str)

@pytest.fixture
def mock_xml_to_dict():

    xml = """<command xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="" xsi:type="AccessDevice"><deviceLevel>10</deviceLevel><deviceName>my_device</deviceName></command>"""
    
    dictionary = Parser.to_dict_from_xml(xml)

    assert isinstance(dictionary, dict)
    assert dictionary.get("deviceLevel") == "10"
    assert dictionary.get("deviceName") == "mydevice"

@pytest.fixture
def mock_xml_to_class():

    xml = """<command xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="" xsi:type="AccessDevice"><deviceLevel>10</deviceLevel><deviceName>my_device</deviceName></command>"""
    
    cls = Parser.to_class_from_xml(xml)

    assert isinstance(cls, Example)
    assert cls.device_level == "10"
    assert cls.device_name == "mydevice"

@pytest.fixture
def mock_nested_xml_to_class():

    xml = """
    <command
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xmlns="" xsi:type="GroupCallCenterGetInstanceResponse22">
        <serviceInstanceProfile>
            <name>Service UK</name>
            <callingLineIdLastName>Service UK</callingLineIdLastName>
            <callingLineIdFirstName>Company</callingLineIdFirstName>
            <hiraganaLastName>Service UK</hiraganaLastName>
            <hiraganaFirstName>Call Center</hiraganaFirstName>
            <extension>0000</extension>
            <language>English</language>
            <timeZone>Europe/London</timeZone>
            <timeZoneDisplayName>(GMT) Greenwich Mean Time</timeZoneDisplayName>
            <alias>0@transport.company.com</alias>
            <alias>6000@transport.company.com</alias>
        </serviceInstanceProfile>
        <type>Basic</type>
        <policy>Simultaneous</policy>
        <enableVideo>false</enableVideo>
        <queueLength>10</queueLength>
        <allowCallerToDialEscapeDigit>false</allowCallerToDialEscapeDigit>
        <escapeDigit>0</escapeDigit>
        <resetCallStatisticsUponEntryInQueue>false</resetCallStatisticsUponEntryInQueue>
        <allowAgentLogoff>true</allowAgentLogoff>
        <allowCallWaitingForAgents>false</allowCallWaitingForAgents>
        <externalPreferredAudioCodec>None</externalPreferredAudioCodec>
        <internalPreferredAudioCodec>None</internalPreferredAudioCodec>
        <playRingingWhenOfferingCall>true</playRingingWhenOfferingCall>
    </command>
    """

    cls = Parser.to_class_from_xml(xml)

    assert isinstance(cls, NestedExample)
    assert isinstance(cls.service_instance_profile, NestedType)