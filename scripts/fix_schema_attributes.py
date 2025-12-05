import ast
import sys
from pathlib import Path

commands_file = Path("src/mercury_ocip/commands/commands.py")
module_import_path = "mercury_ocip.commands.commands"

if not commands_file.exists():
    print(f"ERROR: commands.py not found at {commands_file}")
    sys.exit(2)

source: str = commands_file.read_text()
tree = ast.parse(source)

for node in tree.body:
    if isinstance(node, ast.ClassDef):
        class_name: str = node.name
        docstring: str | None = ast.get_docstring(node)

        if not docstring:
            print(f"Skipping {class_name}: No docstring found")
            continue

        lines = docstring.split("\n")

        try:
            header_index = next(
                i
                for i, line in enumerate(lines)
                if line.strip().startswith("Attributes:")
            )
        except StopIteration:
            print(f"Skipping {class_name}: No 'Attributes:' section found")
            continue

        preamble_lines = lines[:header_index]
        header_line = lines[header_index]

        base_indent = header_line[: len(header_line) - len(header_line.lstrip())]

        attribute_indent = base_indent + "    "

        attribute_lines = []
        for line in lines[header_index + 1 :]:
            stripped_line = line.strip()
            if stripped_line:
                attribute_lines.append(attribute_indent + stripped_line)

        final_lines = preamble_lines + [header_line.rstrip()] + attribute_lines
        final = "\n".join(final_lines)

        if final != docstring:
            print(f"Fixing {class_name} Attributes indentation")
        else:
            print(f"No changes needed for {class_name}")
            continue

        new_doc_expr = ast.Expr(value=ast.Constant(value=final))

        if (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(
                getattr(node.body[0], "value", None), (ast.Constant, ast.Str)
            )
        ):
            node.body[0] = new_doc_expr
        else:
            node.body.insert(0, new_doc_expr)

print("\nSaving changes to file...")
new_source_code = ast.unparse(tree)
commands_file.write_text(new_source_code)
