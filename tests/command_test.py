from mercury_ocip.commands.base_command import OCIType, ErrorResponse, OCINil
from mercury_ocip.commands.commands import (
    ConsolidatedSharedCallAppearanceAccessDeviceMultipleIdentityEndpointAdd22,
    AccessDevice,
    UserModifyRequest22,
    AccessDeviceMultipleIdentityAndContactEndpointModify22,
    TrunkAddressingMultipleContactModify22,
)
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

    print(dict_data)

    rebuilt = TestType.from_dict(dict_data)
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

def test_as_data_mode_type_bug():

    """Tests for a specific bug in command generation where seperation of AS/XS commands would be prioritised.
    XS commands are optional by default, but due to a regex pattern mismatch,
    AS Datamode fields would be incorrectly assigned optional."""

    with pytest.raises(TypeError):
        ConsolidatedSharedCallAppearanceAccessDeviceMultipleIdentityEndpointAdd22(
            access_device=AccessDevice(
                device_level="Group",
                device_name="testDevice"
            ),
            private_identity="string",
            is_active=True,
            allow_origination=True,
            allow_termination=True,
        )


class TestNillableUnionEndpointField:
    """Tests for Optional[Nillable[Union[...]]] endpoint field in UserModifyRequest22.

    The endpoint field has the type:
        Optional[Nillable[Union[
            AccessDeviceMultipleIdentityAndContactEndpointModify22,
            TrunkAddressingMultipleContactModify22
        ]]]

    This means:
    - endpoint can be omitted (None) - not included in XML
    - endpoint can be set to nil (OCINil) - generates <endpoint C:nil="true"/>
    - endpoint can only be one of the two Union types
    """

    def test_endpoint_omitted_not_in_xml(self):
        """When endpoint is None (omitted), it should not appear in the XML output."""
        cmd = UserModifyRequest22(user_id="testuser@example.com")
        xml = cmd.to_xml()

        assert "endpoint" not in xml
        assert "<userId>testuser@example.com</userId>" in xml

    def test_endpoint_nil_generates_nil_element(self):
        """When endpoint is set to OCINil, it should generate <endpoint C:nil="true"/>."""
        cmd = UserModifyRequest22(user_id="testuser@example.com", endpoint=OCINil)
        xml = cmd.to_xml()

        assert '<endpoint C:nil="true"/>' in xml
        assert "<userId>testuser@example.com</userId>" in xml

    def test_endpoint_accepts_access_device_type(self):
        """Endpoint should accept AccessDeviceMultipleIdentityAndContactEndpointModify22."""
        endpoint = AccessDeviceMultipleIdentityAndContactEndpointModify22(
            access_device=AccessDevice(device_level="Group", device_name="TestDevice"),
            line_port="sip:test@example.com"
        )
        cmd = UserModifyRequest22(user_id="testuser@example.com", endpoint=endpoint)
        xml = cmd.to_xml()

        assert "<endpoint>" in xml
        assert "<deviceLevel>Group</deviceLevel>" in xml
        assert "<deviceName>TestDevice</deviceName>" in xml
        assert "<linePort>sip:test@example.com</linePort>" in xml

    def test_endpoint_accepts_trunk_addressing_type(self):
        """Endpoint should accept TrunkAddressingMultipleContactModify22."""
        endpoint = TrunkAddressingMultipleContactModify22(
            enterprise_trunk_name="TestTrunk"
        )
        cmd = UserModifyRequest22(user_id="testuser@example.com", endpoint=endpoint)
        xml = cmd.to_xml()

        assert "<endpoint>" in xml
        assert "<enterpriseTrunkName>TestTrunk</enterpriseTrunkName>" in xml