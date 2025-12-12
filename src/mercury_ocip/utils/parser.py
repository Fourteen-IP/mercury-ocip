# Responsible for parsing data between types such as JSON, XML and Classes

# Design not fully fleshed out yet
import asyncio
from concurrent.futures import ThreadPoolExecutor
import xml.etree.ElementTree as ET

from mercury_ocip.libs.basic_types import XMLDictResult
from mercury_ocip.utils.defines import snake_to_camel, to_snake_case
from typing import get_type_hints, List, get_args, Union, Type, cast, Dict, TypeVar

OCIType = TypeVar(
    "OCIType"
)  # Type Annotation Linkage For OCIType Without Circular Import


class Parser:
    """
    Base Class For OCI Object Parsing & Type Translation

    method table:

    - to_xml_from_class: Translates class object to xml
    - to_xml_from_dict: Translates dictionary object to xml
    - to_dict_from_class: Translates class object to dictionary
    - to_dict_from_xml: Translates xml into dictionary
    - to_class_from_dict: Translates dictionary object to class
    - to_class_from_xml: Translates xml to class
    """

    @staticmethod
    def to_xml_from_class(obj: object) -> str:
        def serialize_value(parent: ET.Element, tag: str, value: Union[str, object]):
            """
            Converts any passed value into an XML Tree Element
            """
            from mercury_ocip.commands.base_command import OCIType as Baseclass

            # Sanitises Boolean Values
            if isinstance(value, bool):
                value = str(value).lower()

            # If The Value Being Passed Inherets From OCIType We Recursively Process The Element Into XML Elements
            if isinstance(value, Baseclass):
                child = ET.SubElement(parent, tag)
                data = Parser.to_dict_from_class(value)

                assert isinstance(data, dict)

                for k, v in data.items():
                    if isinstance(v, list):
                        for item in v:
                            if isinstance(item, bool):
                                item = str(item).lower()
                            ET.SubElement(child, snake_to_camel(k)).text = str(item)
                    elif isinstance(v, dict):
                        nested_child = ET.SubElement(child, snake_to_camel(k))
                        for sub_k, sub_v in v.items():
                            if isinstance(sub_v, bool):
                                sub_v = str(sub_v).lower()
                            ET.SubElement(
                                nested_child, snake_to_camel(sub_k)
                            ).text = str(sub_v)
                    else:
                        if isinstance(v, bool):
                            v = str(v).lower()
                        ET.SubElement(child, snake_to_camel(k)).text = str(v)
            else:
                ET.SubElement(parent, tag).text = str(value)

        root = ET.Element(
            "command",
            attrib={
                "xmlns": "",
                "{http://www.w3.org/2001/XMLSchema-instance}type": obj.__class__.__name__,
            },
        )

        aliases = obj.get_field_aliases()

        type_hints = get_type_hints(obj.__class__)
        for attr, hint in type_hints.items():
            value = getattr(obj, attr, None)
            if value is None:
                continue

            args = get_args(hint)
            if args:
                if isinstance(value, list):
                    for item in value:
                        serialize_value(root, aliases.get(attr), item)
                    continue

            serialize_value(root, aliases.get(attr), value)

        return ET.tostring(root, encoding="ISO-8859-1", xml_declaration=False).decode()

    @staticmethod
    def to_xml_from_dict(data: XMLDictResult, cls: Type[OCIType]) -> str:
        obj = Parser.to_class_from_dict(data, cls)
        return Parser.to_xml_from_class(obj)

    @staticmethod
    def to_dict_from_class(obj: object) -> XMLDictResult:
        result: XMLDictResult = {}
        type_hints = get_type_hints(obj.__class__)
        for attr, hint in type_hints.items():
            value = getattr(obj, attr, None)
            if value is None:
                continue

            from mercury_ocip.commands.base_command import OCIType as Baseclass

            origin = getattr(hint, "__origin__", None)
            if origin in (list, List):
                if isinstance(result, dict):
                    attr_value = result.setdefault(attr, [])
                    if isinstance(attr_value, list):
                        for item in value:
                            attr_value.append(
                                Parser.to_dict_from_class(item)
                                if isinstance(value, Baseclass)
                                else item
                            )
            elif isinstance(value, Baseclass):
                if isinstance(result, dict):
                    result[attr] = Parser.to_dict_from_class(value)
                else:
                    result = Parser.to_dict_from_class(value)
            else:
                if isinstance(result, dict):
                    result[attr] = value
                else:
                    result = value
        return result

    @staticmethod
    def to_dict_from_xml(xml: Union[str, ET.Element]) -> XMLDictResult:
        if isinstance(xml, str):
            xml = ET.fromstring(xml)

        result: XMLDictResult = {}

        if xml.attrib:
            if isinstance(result, dict):
                result["attributes"] = dict(xml.attrib)

        children = list(xml)

        if xml.tag.__contains__("Table"):
            from mercury_ocip.commands.base_command import (
                OCITable,
                OCITableRow,
            )  # Inline Table Import

            col_headings: list[str] = []
            rows: list[OCITableRow] = []

            for child in children:
                if child.tag == "colHeading":
                    col_headings.append(child.text or "")
                elif child.tag == "row":
                    col_values = [col.text or "" for col in child.findall("col")]
                    rows.append(OCITableRow(col=col_values))

            result = OCITable(col_heading=col_headings, row=rows)
        elif children:
            for child in children:
                child_dict = Parser.to_dict_from_xml(child)

                if child.tag in result:
                    if isinstance(result, dict):
                        existing = result[child.tag]
                    if isinstance(existing, list):
                        cast(List[XMLDictResult], existing).append(child_dict)
                    else:
                        items: List[XMLDictResult] = []
                        if isinstance(existing, dict):
                            items.append(existing)
                        else:
                            items.append(existing)
                        if isinstance(child_dict, dict):
                            items.append(child_dict)
                        else:
                            items.append(child_dict)

                        if isinstance(result, dict):
                            result[child.tag] = items
                else:
                    if isinstance(result, dict):
                        result[child.tag] = (
                            child_dict if isinstance(child_dict, dict) else child_dict
                        )
        else:
            text = xml.text.strip() if xml.text else ""
            result = text

        return result

    @staticmethod
    def to_class_from_dict(data: XMLDictResult, cls: Type[OCIType]) -> OCIType:
        type_hints = get_type_hints(cls)
        init_args = {}

        assert data is not None
        assert isinstance(data, dict)
        assert data.get("command") is not None
        assert isinstance(data.get("command"), dict)

        data_dict = cast(
            Dict[str, Union[str, XMLDictResult, List[XMLDictResult]]], data
        )
        command = cast(
            Dict[str, Union[str, XMLDictResult, List[XMLDictResult]]],
            data_dict.get("command"),
        )

        snake_case_command = {to_snake_case(k): v for k, v in command.items()}

        for key, hint in type_hints.items():
            if key not in snake_case_command:
                continue

            value = snake_case_command[key]
            args = get_args(hint)
            origin = getattr(hint, "__origin__", None)

            if origin in (list, List):
                subtype = args[0]
                init_args[key] = [
                    Parser.to_class_from_dict(v, subtype) if isinstance(v, dict) else v
                    for v in value
                ]
            elif isinstance(value, dict) and hint.__name__ == "OCIType":
                init_args[key] = Parser.to_class_from_dict(value, hint)
            else:
                init_args[key] = value

        return cls(**init_args)

    @staticmethod
    def to_class_from_xml(xml: Union[str, ET.Element], cls: Type[OCIType]) -> OCIType:
        return Parser.to_class_from_dict(Parser.to_dict_from_xml(xml), cls)


class AsyncParser:
    """
    Base Class For Async OCI Object Parsing & Type Translation

    It is doing the exact same thing as Parser, except adding each call onto the event loop.

    method table:

    - to_xml_from_class: Translates class object to xml
    - to_xml_from_dict: Translates dictionary object to xml
    - to_dict_from_class: Translates class object to dictionary
    - to_dict_from_xml: Translates xml into dictionary
    - to_class_from_dict: Translates dictionary object to class
    - to_class_from_xml: Translates xml to class
    """

    _executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="async_parser")

    @staticmethod
    def _get_loop():
        return asyncio.get_event_loop()

    @staticmethod
    async def to_xml_from_class(obj: OCIType) -> str:
        return await AsyncParser._get_loop().run_in_executor(
            AsyncParser._executor, Parser.to_xml_from_class, obj
        )

    @staticmethod
    async def to_xml_from_dict(data: XMLDictResult, cls: Type[OCIType]) -> str:
        return await AsyncParser._get_loop().run_in_executor(
            AsyncParser._executor, Parser.to_xml_from_dict, data, cls
        )

    @staticmethod
    async def to_dict_from_class(obj: OCIType) -> XMLDictResult:
        return await AsyncParser._get_loop().run_in_executor(
            AsyncParser._executor, Parser.to_dict_from_class, obj
        )

    @staticmethod
    async def to_dict_from_xml(xml: Union[str, ET.Element]) -> XMLDictResult:
        return await AsyncParser._get_loop().run_in_executor(
            AsyncParser._executor, Parser.to_dict_from_xml, xml
        )

    @staticmethod
    async def to_class_from_dict(data: XMLDictResult, cls: Type[OCIType]) -> OCIType:
        return await AsyncParser._get_loop().run_in_executor(
            AsyncParser._executor, Parser.to_class_from_dict, data, cls
        )

    @staticmethod
    async def to_class_from_xml(
        xml: Union[str, ET.Element], cls: Type[OCIType]
    ) -> OCIType:
        return await AsyncParser._get_loop().run_in_executor(
            AsyncParser._executor, Parser.to_class_from_xml, xml, cls
        )
