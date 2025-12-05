import ast
import re
import sys
from difflib import ndiff
from pathlib import Path

from mercury_ocip.utils.docs.correct_typo import correct_typo

"""
A script to fix common typos in the schema definitions.

Some schemas have incorrect response types in their doc strings, since this is used to generate the docs, we need to fix them here.

This uses "correct_typo", a series of helper functions to run some heueristics. It will:

- Strip Versioning
- Check that the Response actually exists
- If its not real, it will first check any missing words or moved words and re-arrange them in correct order.
- Typo check all words - e.g Get instead of Getl
- Find the highest version of the command
- Return the response

This script will then iterate through all dataclasses and run these checks. Updating the final commands.py file.

"""

commands_file = Path("src/mercury_ocip/commands/commands.py")
module_import_path = "mercury_ocip.commands.commands"

if not commands_file.exists():
    print(f"ERROR: commands.py not found at {commands_file}")
    sys.exit(2)

source: str = commands_file.read_text()
tree = ast.parse(source)
outliers = []
corrections = []

defined_class_names: set[str] = {
    node.name for node in tree.body if isinstance(node, ast.ClassDef)
}

for node in tree.body:
    if not isinstance(node, ast.ClassDef):
        continue

    class_name: str = node.name
    class_inheritance = node.bases[0].id if node.bases else ""  # type: ignore

    if class_inheritance not in ("OCIDataResponse", "OCIRequest"):
        continue

    docstring: str | None = ast.get_docstring(node)

    if responses := re.findall(
        r"\b([A-Za-z]+(?:[A-Z][a-z]+)*Response(?:\d+V?\d*)?)\b", docstring or ""
    ):
        for response in responses:
            if (
                response
                not in (
                    "SuccessResponse",
                    "ErrorResponse",
                )
                and response not in defined_class_names
            ):  # If the response from the docstring isnt found in the actual class defintions (Typo)
                corrected_response = correct_typo(
                    class_name, response, defined_class_names
                )

                if (
                    corrected_response is None
                ):  # Check if the correction failed, if so, add it to the outliers and move onto the next.
                    outliers.append(response)
                    continue

                if docstring is None:
                    print(f"Skipping {class_name}: No docstring found")
                    continue

                diff = "\n".join(ndiff([response], [corrected_response]))
                print(f"Fixing {class_name}:")
                print(f"  Difference:\n{diff}\n")

                corrections.append(corrected_response)

                docstring = docstring.replace(response, corrected_response)  # type: ignore

                new_doc_expr = ast.Expr(value=ast.Constant(value=docstring))

                if (
                    node.body  # type: ignore
                    and isinstance(node.body[0], ast.Expr)  # type: ignore
                    and isinstance(
                        getattr(node.body[0], "value", None),
                        (ast.Constant, ast.Str),
                    )
                ):
                    node.body[0] = new_doc_expr  # type: ignore
                else:
                    node.body.insert(0, new_doc_expr)  # type: ignore

ast.fix_missing_locations(tree)
new_source = ast.unparse(tree)
commands_file.write_text(new_source)
print(f"Updated {commands_file}, Number of classes corrected: {len(corrections)}")

if outliers:
    print(
        f"Some classes could not be resolved automatically, please fix manually: {[outlier for outlier in outliers]}"
    )
