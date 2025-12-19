## OCITable Command Reference

The OCITable in base commands is used to represent tabular data structures in OCI-P commands. Below is a reference for the OCITable command and its usage.

```python
from mercury.commands.base import OCITable, OCITableRow

# Example of creating an OCITable instance
table = OCITable(
    col_heading=["User ID", "Last Name", "First Name"],
    row=[
        OCITableRow(col=["user1", "Doe", "John"]),
        OCITableRow(col=["user2", "Smith", "Jane"]),
    ],
)

print(table.to_dict())
```

The OCITable requires the table rows to be instances of OCITableRow. Each OCITableRow contains a list of column values corresponding to the column headings defined in the OCITable.

The OCITable class has a to_dict() method that converts the table into a dictionary format, which is useful for serialization or further processing. It will still be serialised when a OCITable nested in a command has its to_dict()/to_xml() method called.

```python
from mercury.commands.base import OCITable, OCITableRow
from mercury.commands.commands import GroupGetListInSystemResponse

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


print(command.to_dict())
```

This will output:

```python
{
    "group_table": [
        {"column1": "Column1_Row1", "column2": "Column2_Row1"},
        {"column1": "Column1_Row2", "column2": "Column2_Row2"},
    ]
}
```

If you want the response type to be in the serilialized format, you can pass a parameter to the Parser object method:

```python

from mercury.commands.base import OCITable, OCITableRow
from mercury.commands.commands import GroupGetListInSystemResponse
from mercury.utils import Parser

table = OCITable(
    col_heading=["Column1", "Column2"],
    row=[
        OCITableRow(["Column1_Row1", "Column2_Row1"]),
        OCITableRow(["Column1_Row2", "Column2_Row2"]),
    ],
)

command = GroupGetListInSystemResponse(group_table=table)

print(Parser.to_dict_from_class(command, wrap_in_class_name=True))
```

This will output:

```python
{
    "GroupGetListInSystemResponse": {
        "group_table": [
            {"column1": "Column1_Row1", "column2": "Column2_Row1"},
            {"column1": "Column1_Row2", "column2": "Column2_Row2"},
        ]
    }
}
```