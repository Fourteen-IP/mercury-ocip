from typing import Any
from typing import get_type_hints, Optional
from dataclasses import fields, is_dataclass
from mercury_ocip.utils.parser import Parser, AsyncParser
from mercury_ocip.utils.defines import to_snake_case


class OCIType:
    """
    Base Class For Broadworks Types

    method_table:

    - __init__: Handles dataclass default initialisation of raw objects
    - to_dict: Invokes Parser to_dict_from_class
    - to_xml: Invokes Parser to_xml_from_class
    - from_dict: Invokes Parser to_class_from_dict
    - from_xml: Invokes Parser to_class_from_xml
    """

    namespace = "C"

    def __init__(self, **kwargs):
        annotations = get_type_hints(self.__class__)
        for key, value in kwargs.items():
            if key not in annotations:
                raise ValueError(f"Unknown field: {key}")
            setattr(self, key, value)

        for key in annotations:
            if not hasattr(self, key):
                setattr(self, key, None)

    def get_field_aliases(self):
        # fields() requires a dataclass type/instance. Some generated BWKS types
        # may be dataclasses; if not, return an empty mapping to satisfy the
        # type-checker and runtime.
        cls = self.__class__
        if not is_dataclass(cls):
            return {}
        return {f.name: f.metadata.get("alias", f.name) for f in fields(cls)}

    def to_dict(self) -> dict[str, Any]:
        return Parser.to_dict_from_class(self)

    def to_xml(self) -> str:
        return Parser.to_xml_from_class(self)

    @classmethod
    def from_dict(cls: type["OCIType"], data: dict[str, Any]) -> "OCIType":
        return Parser.to_class_from_dict(data, cls)

    @classmethod
    def from_xml(cls, xml: str) -> "OCIType":
        return Parser.to_class_from_xml(xml, cls)

    async def to_dict_async(self) -> dict[str, Any]:
        return await AsyncParser.to_dict_from_class(self)

    async def to_xml_async(self) -> str:
        return await AsyncParser.to_xml_from_class(self)

    @classmethod
    async def from_dict_async(cls: type["OCIType"], data: dict[str, Any]) -> "OCIType":
        return await AsyncParser.to_class_from_dict(data, cls)

    @classmethod
    async def from_xml_async(cls: type["OCIType"], xml: str) -> "OCIType":
        return await AsyncParser.to_class_from_xml(xml, cls)


class OCICommand(OCIType):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class OCIRequest(OCICommand):
    pass


class OCIResponse(OCICommand):
    pass


class OCIDataResponse(OCIResponse):
    pass


class SuccessResponse(OCIResponse):
    pass


class OCITableRow:
    col: list[str]

    def __init__(self, col):
        self.col = col


# class OCITable:
#    col_heading: list[str]
#    row: list[OCITableRow]
#
#    def __init__(self, col_heading, row):
#        self.col_heading = col_heading
#        self.row = row
#
#        return self.entries()
#
#    def entries(self) -> list[dict]:
#        """Converts the entire table to a list of dictionaries."""
#        dict_list = []
#        for row in self.row:
#            row_dict = {
#                self.col_heading[i]: row.col[i]
#                for i in range(min(len(self.col_heading), len(row.col)))
#            }
#            dict_list.append(row_dict)
#        return dict_list


class OCITable:
    col_heading: list[str]
    row: list[OCITableRow]

    def __new__(cls, col_heading, row):
        # Build table and return directly, skipping instance creation
        normalised_headings = [to_snake_case(h) for h in col_heading]

        return [
            {
                normalised_headings[i]: r.col[i]
                for i in range(min(len(col_heading), len(r.col)))
            }
            for r in row
        ]


class ErrorResponse(OCIResponse):
    errorCode: Optional[int] = None
    summary: str
    summaryEnglish: str
    detail: Optional[str] = None
