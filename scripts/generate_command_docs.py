import mkdocs_gen_files
import ast
import re
from pathlib import Path
from string import Template
from textwrap import dedent, indent


def highest_version_for(command: str, defined_names: set[str]) -> str | None:
    """
    Finds the highest version of a class name based on its base name.

    This function identifies the class in `names` that starts with `base` and has the highest
    version number. If an exact match exists, it is returned. Otherwise, the highest version
    is determined based on the naming convention.

    Args:
        command (str): The name of the command class (e.g., "UserGetRequest22V2").
        defined_names (set[str]: A set of class names to search.

    Returns:
        str: The highest version of the class name, or None if no versioned variant is found.
    """

    base_command, _, _, _ = parse_version(command)

    matching = []
    for name in defined_names:
        try:
            base, major, sp, v = parse_version(name)
            if base_command == base:
                matching.append((name, major, sp, v))
        except ValueError:
            continue

    if not matching:
        return None

    matching.sort(key=lambda x: (x[1], x[2], x[3]), reverse=True)

    return matching[0][0]


def parse_version(command: str) -> tuple[str, int, int, int]:
    """
    Parse a versioned command/class name into its components.

    The expected form is:
      <base><major>[sp<service_patch>][V<subsequent_patch>]
    where:
      - <base> is any prefix - UserGetRequest | SystemSoftwareVersionGetRequest
      - <major> is an optional integer - 18 in UserDeleteRequest18
      - sp<service_patch> is an optional service patch integer (e.g. "sp3")
      - V<subsequent_patch> (or v) is an optional subsequent patch integer (e.g. "V2")

    Args:
        command (str): The versioned name to parse (e.g. "UserGetRequest22", "Foo12sp3V2").

    Returns:
        tuple[str, int, int, int]: (base_name, major, service_patch, subsequent_patch)
            service_patch and subsequent_patch default to 0 when absent.

    Raises:
        ValueError: If `command` does not match the expected pattern.
    """
    pattern = r"^([A-Za-z]+)(?:(\d+)(?:sp(\d+))?(?:V(\d+))?)?$"

    match = re.match(pattern, command)
    if not match:
        raise ValueError(f"Invalid command format: {command}")

    base_name = match.group(1)
    major = int(match.group(2)) if match.group(2) else 0
    service_patch: int = int(match.group(3)) if match.group(3) else 0
    subsequent_patch: int = int(match.group(4)) if match.group(4) else 0

    return (base_name, major, service_patch, subsequent_patch)


commands_file = Path("src/mercury_ocip/commands/commands.py")
module_import_path = "mercury_ocip.commands.commands"

with open(commands_file, "r") as f:
    source = f.read()

tree = ast.parse(source)

request_template = Template(
    dedent("""
# ${class_name}

::: ${module_import_path}.${class_name}

# Responses
${response_section}

## Example Usage

```python
from mercury_ocip.client import Client
from mercury_ocip.commands import ${class_name}

client = Client()

command = ${constructor_block}

response = client.command(command)

print(response)
```

## Example 2 with Raw Command

```python
from mercury_ocip.client import Client

client = Client()

response = client.raw_command("${class_name}"${raw_args})

print(response)
```

""")
)

defined_class_names = {
    node.name for node in tree.body if isinstance(node, ast.ClassDef)
}

for node in tree.body:
    if isinstance(node, ast.ClassDef):
        class_name = node.name
        class_inheritance = node.bases[0].id if node.bases else ""  # type: ignore

        assert class_inheritance is not None

        fields = []
        for item in node.body:
            if isinstance(item, ast.AnnAssign):
                field_name = item.target.id  # type: ignore
                fields.append(field_name)

        if fields:
            args = ",\n".join(f"{field}=..." for field in fields) + ","
            constructor_block = f"{class_name}(\n{indent(args, ' ' * 4)}\n)"
            kwargs_block = ",\n".join(f"{field}=..." for field in fields) + ","
            raw_args = f",\n{indent(kwargs_block, ' ' * 4)}\n"
        else:
            constructor_block = f"{class_name}()"
            raw_args = ""

        match class_inheritance:
            case c if "OCIType" in c:
                subfolder = "types"
                content = f"::: {module_import_path}.{class_name}"

            case c if "OCIRequest" in c:
                subfolder = "requests"
                response_section = ""

                doc_string = ast.get_docstring(node)

                if responses := re.findall(
                    r"\b([A-Za-z]+(?:[A-Z][a-z]+)*Response(?:\d+V?\d*)?)\b",
                    doc_string,
                ):  # type: ignore
                    for response in responses:
                        resolved = (
                            response
                            if response in ("SuccessResponse", "ErrorResponse")
                            else highest_version_for(response, defined_class_names)
                        )
                        if resolved in ("SuccessResponse", "ErrorResponse"):
                            response_section += dedent(f"""
                            ::: mercury_ocip.commands.base_command.{resolved}
                            """)
                        else:
                            response_section += dedent(f"""
                            ::: {module_import_path}.{resolved}
                            """)
                else:
                    response_section += dedent("""
                    :: mercury_ocip.commands.base_command.ErrorResponse

                    :: mercury_ocip.commands.base_command.SuccessResponse
                            """)  # Fallback to generics - some docs dont specify a response at all!

                content = request_template.substitute(
                    class_name=class_name,
                    constructor_block=constructor_block,
                    raw_args=raw_args,
                    module_import_path=module_import_path,
                    response_section=response_section,
                )

            case c if "OCIDataResponse" in c:
                continue

            case _:
                subfolder = "others"
                content = f"::: {module_import_path}.{class_name}"

        doc_path = Path(f"commands/{subfolder}/{class_name}.md")

        with mkdocs_gen_files.open(doc_path, "w") as fd:
            fd.write(content)

        mkdocs_gen_files.set_edit_path(doc_path, commands_file)
