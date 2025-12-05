from mercury_ocip.commands.base_command import OCIType, ErrorResponse
from dataclasses import dataclass, field
from typing import Optional
import pytest

@dataclass(kw_only=True)
class TestType(OCIType):
    device_level: str = field(metadata={'alias': 'deviceLevel'})
    device_name: str = field(metadata={'alias': 'deviceName'})
    device_order: Optional[int] = field(default=None, metadata={'alias': 'deviceOrder'})


def test_init_accepts_valid_fields():
    obj = TestType(device_level="Level1", device_name="DeviceA", device_order=1)
    assert obj.device_level == "Level1"
    assert obj.device_name == "DeviceA"
    assert obj.device_order == 1


def test_init_sets_missing_fields_to_none():
    obj = TestType(device_level="Level2", device_name="DeviceB")
    assert hasattr(obj, "device_level")
    assert hasattr(obj, "device_order")


def test_init_raises_on_invalid_field():
    with pytest.raises(TypeError, match="invalid"):
        TestType(device_level="Level1", device_name="DeviceA", invalid=123)


def test_to_dict_and_from_dict():
    original = TestType(device_level="Level1", device_name="DeviceA", device_order=1)
    dict_data = original.to_dict()

    rebuilt = TestType.from_dict({"command": dict_data})
    assert rebuilt.device_level == "Level1"
    assert rebuilt.device_name == "DeviceA"
    assert rebuilt.device_order == 1


# def test_to_xml_and_from_xml():
#     original = Example(name="Jane", age=50)
#     xml = original.to_xml()

#     rebuilt = Example.from_xml(xml)
#     assert rebuilt.name == "Jane"
#     assert rebuilt.age == 50


def test_subclass_behavior():
    err = ErrorResponse(summary="fail", summaryEnglish="failure")
    assert isinstance(err, OCIType)
    assert err.summary == "fail"

def test_empty_field_fails():
    with pytest.raises(TypeError):
        TestType(device_name="DeviceA")

def test_instantiating_from_dict_as_kwargs():
    data = {
        "device_level": "Level3",
        "device_name": "DeviceC",
        "device_order": 3
    }
    obj = TestType(**data)
    assert obj.device_level == "Level3"
    assert obj.device_name == "DeviceC"
    assert obj.device_order == 3