import asyncio
from concurrent.futures import ThreadPoolExecutor
import xmltodict
from typing import (
    get_type_hints,
    List,
    get_args,
    Union,
    Type,
    cast,
    Dict,
    TypeVar,
    Any,
    Protocol,
    runtime_checkable,
)

from mercury_ocip.utils.defines import snake_to_camel, to_snake_case

OCIType = TypeVar("OCIType")
T = TypeVar("T")


@runtime_checkable
class HasFieldAliases(Protocol):
    """Protocol for objects that have field aliases."""

    def get_field_aliases(self) -> Dict[str, str]: ...


class Parser:
    """
    Base Class For OCI Object Parsing & Type Translation using xmltodict

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
        """Convert a class instance to XML string."""
        aliases: Dict[str, str] = {}
        if isinstance(obj, HasFieldAliases):
            aliases = obj.get_field_aliases()

        # ensure default empty namespace on <command> and declare the xsi namespace using prefix "C"
        root_content: Dict[str, Any] = {
            "@xmlns": "",
            "@xmlns:C": "http://www.w3.org/2001/XMLSchema-instance",
            "@C:type": obj.__class__.__name__,
        }

        type_hints = get_type_hints(obj.__class__)
        for attr, hint in type_hints.items():
            value = getattr(obj, attr, None)
            if value is None:
                continue

            key = aliases.get(attr, snake_to_camel(attr))

            def convert_keys(d: Any) -> Any:
                """Recursively convert dictionary keys to camelCase."""
                if isinstance(d, dict):
                    new_d: Dict[str, Any] = {}
                    for k, v in d.items():
                        new_k = snake_to_camel(k)
                        new_d[new_k] = convert_keys(v)
                    return new_d
                elif isinstance(d, list):
                    result_list = []
                    for i in d:
                        # If list item is an object, convert it to dict first
                        if hasattr(i, "__dict__"):
                            result_list.append(
                                convert_keys(Parser.to_dict_from_class(i))
                            )
                        else:
                            result_list.append(convert_keys(i))
                    return result_list
                elif isinstance(d, bool):
                    return str(d).lower()
                else:
                    return d

            if isinstance(value, list):
                if not value:  # empty list
                    continue

                processed_list: List[Any] = []
                for item in value:
                    if hasattr(item, "__dict__"):
                        # Convert to dict first
                        item_dict = Parser.to_dict_from_class(item)
                        # Then convert keys to camelCase
                        item_dict_camel = convert_keys(item_dict)
                        processed_list.append(item_dict_camel)
                    else:
                        processed_list.append(
                            str(item).lower() if isinstance(item, bool) else item
                        )

                import json

                print(
                    f"DEBUG {key}: {json.dumps(processed_list, indent=2, default=str)}"
                )

                # Assign the processed list
                root_content[key] = processed_list
            elif hasattr(value, "__dict__"):
                root_content[key] = convert_keys(Parser.to_dict_from_class(value))
            else:
                root_content[key] = (
                    str(value).lower() if isinstance(value, bool) else value
                )

        output = xmltodict.unparse(
            {"command": root_content}, full_document=False, short_empty_elements=True
        )

        if not isinstance(output, str):
            raise ValueError("XML output is not a string")

        return output

    @staticmethod
    def to_xml_from_dict(data: Dict[str, Any], cls: Type[OCIType]) -> str:
        """Convert a dictionary to XML via class instance."""
        obj = Parser.to_class_from_dict(data, cls)
        return Parser.to_xml_from_class(obj)

    @staticmethod
    def to_dict_from_class(obj: object) -> Dict[str, Any]:
        """Convert a class instance to a dictionary."""
        result: Dict[str, Any] = {}
        type_hints = get_type_hints(obj.__class__)

        for attr, hint in type_hints.items():
            value = getattr(obj, attr, None)
            if value is None:
                continue

            origin = getattr(hint, "__origin__", None)
            if origin in (list, List):
                if isinstance(value, list):
                    res_list: List[Any] = []
                    for item in value:
                        if hasattr(item, "__dict__"):
                            res_list.append(Parser.to_dict_from_class(item))
                        else:
                            res_list.append(item)
                    result[attr] = res_list
            elif hasattr(value, "__dict__"):
                result[attr] = Parser.to_dict_from_class(value)
            else:
                result[attr] = value

        return result

    @staticmethod
    def to_dict_from_xml(xml: str) -> Dict[str, Any]:
        """Parse XML string to dictionary."""
        if not isinstance(xml, str):
            return {}

        parsed = xmltodict.parse(xml)
        if not parsed or not isinstance(parsed, dict):
            return {}

        root_key = next(iter(parsed.keys()))
        root_val = parsed[root_key]

        return cast(Dict[str, Any], Parser._process_dict_item(root_key, root_val))

    @staticmethod
    def _process_dict_item(key: str, value: Any) -> Any:
        """Process individual dictionary items during XML parsing."""
        # Handle OCITable special case
        if (
            "Table" in key
            and isinstance(value, dict)
            and "colHeading" in value
            and "row" in value
        ):
            from mercury_ocip.commands.base_command import OCITable, OCITableRow

            col_headings = value["colHeading"]
            if not isinstance(col_headings, list):
                col_headings = [col_headings]

            rows_data = value["row"]
            if not isinstance(rows_data, list):
                rows_data = [rows_data]

            rows: List[OCITableRow] = []
            for r in rows_data:
                cols = r.get("col", [])
                if not isinstance(cols, list):
                    cols = [cols]
                rows.append(OCITableRow(col=cols))

            return OCITable(col_heading=col_headings, row=rows)

        # Handle dictionaries
        if isinstance(value, dict):
            if "#text" in value:
                return value["#text"]

            new_val: Dict[str, Any] = {}
            attributes: Dict[str, Any] = {}

            for k, v in value.items():
                if k.startswith("@"):
                    # Handle attributes
                    attr_name = k[1:]
                    if ":" in attr_name:
                        prefix, local = attr_name.split(":", 1)
                        attributes[attr_name] = v
                        attributes[local] = v
                        if prefix in ("xsi", "C"):
                            attributes[
                                f"{{http://www.w3.org/2001/XMLSchema-instance}}{local}"
                            ] = v
                    else:
                        attributes[attr_name] = v
                else:
                    if isinstance(v, list):
                        new_val[k] = [Parser._process_dict_item(k, i) for i in v]
                    else:
                        new_val[k] = Parser._process_dict_item(k, v)

            if attributes:
                new_val["attributes"] = attributes

            return new_val

        # Handle None
        if value is None:
            return ""

        return value

    @staticmethod
    def to_class_from_dict(data: Dict[str, Any], cls: Type[OCIType]) -> OCIType:
        """Convert a dictionary to a class instance."""
        type_hints = get_type_hints(cls)

        if not isinstance(data, dict):
            raise TypeError(
                f"Expected dict for {cls.__name__}, got {type(data).__name__}"
            )

        source = data
        if "command" in data:
            command_data = data["command"]
            if not isinstance(command_data, dict):
                raise TypeError(
                    f"Expected dict for command, got {type(command_data).__name__}"
                )
            source = command_data

        snake_case_source: Dict[str, Any] = {
            to_snake_case(k): v for k, v in source.items()
        }

        init_args: Dict[str, Any] = {}

        for key, hint in type_hints.items():
            if key not in snake_case_source:
                continue

            val = snake_case_source[key]
            origin = getattr(hint, "__origin__", None)
            args = get_args(hint)

            # Handle Optional types (which are Union[T, None])
            if origin is Union:
                non_none_args = [arg for arg in args if arg is not type(None)]
                if non_none_args:
                    hint = non_none_args[0]
                    origin = getattr(hint, "__origin__", None)
                    args = get_args(hint)

            # Handle List types
            if origin in (list, List):
                if not args:
                    init_args[key] = val if isinstance(val, list) else [val]
                    continue

                subtype = args[0]
                if isinstance(val, list):
                    init_args[key] = [
                        Parser.to_class_from_dict(v, subtype)
                        if isinstance(v, dict)
                        and hasattr(subtype, "__mro__")
                        and subtype is not Any
                        else v
                        for v in val
                    ]
                else:
                    init_args[key] = [
                        Parser.to_class_from_dict(val, subtype)
                        if isinstance(val, dict)
                        and hasattr(subtype, "__mro__")
                        and subtype is not Any
                        else val
                    ]
            # Handle nested class types (but not Any)
            elif hint is not Any and isinstance(val, dict) and hasattr(hint, "__mro__"):
                init_args[key] = Parser.to_class_from_dict(val, hint)
            # Handle primitive types and Any
            else:
                init_args[key] = val

        return cls(**init_args)

    @staticmethod
    def to_class_from_xml(xml: str, cls: Type[OCIType]) -> OCIType:
        """Parse XML string and convert to class instance."""
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
    async def to_xml_from_dict(data: Dict[str, Any], cls: Type[OCIType]) -> str:
        return await AsyncParser._get_loop().run_in_executor(
            AsyncParser._executor, Parser.to_xml_from_dict, data, cls
        )

    @staticmethod
    async def to_dict_from_class(obj: OCIType) -> Dict[str, Any]:
        return await AsyncParser._get_loop().run_in_executor(
            AsyncParser._executor, Parser.to_dict_from_class, obj
        )

    @staticmethod
    async def to_dict_from_xml(xml: str) -> Dict[str, Any]:
        return await AsyncParser._get_loop().run_in_executor(
            AsyncParser._executor, Parser.to_dict_from_xml, xml
        )

    @staticmethod
    async def to_class_from_dict(data: Dict[str, Any], cls: Type[OCIType]) -> OCIType:
        return await AsyncParser._get_loop().run_in_executor(
            AsyncParser._executor, Parser.to_class_from_dict, data, cls
        )

    @staticmethod
    async def to_class_from_xml(xml: str, cls: Type[OCIType]) -> OCIType:
        return await AsyncParser._get_loop().run_in_executor(
            AsyncParser._executor, Parser.to_class_from_xml, xml, cls
        )
