import pytest
from unittest.mock import Mock
from mercury_ocip.utils.parser import Parser
import lxml

from mercury_ocip.commands.commands import AccessDevice as Example

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


def mock_xml_to_dict():

    xml = """<command xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="" xsi:type="AccessDevice"><deviceLevel>10</deviceLevel><deviceName>my_device</deviceName></command>"""
    
    dictionary = Parser.to_dict_from_xml(xml)

    assert isinstance(dictionary, dict)
    assert dictionary.get("deviceLevel") == "10"
    assert dictionary.get("deviceName") == "mydevice"

# def mock_xml_to_class():

#     xml = """<command xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="" xsi:type="AccessDevice"><deviceLevel>10</deviceLevel><deviceName>my_device</deviceName></command>"""
    
#     cls = Parser.to_class_from_xml(xml)

#     assert isinstance(cls, Example)
#     assert cls.device_level == "10"
#     assert cls.device_name == "mydevice"
#     pass
