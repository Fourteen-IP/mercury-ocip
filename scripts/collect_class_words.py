import ast
import re
import sys
from pathlib import Path

#
# Used to extract unique names from Broadworks commands. Used as a big list in correct_typo.py
#

scripts_path = Path(__file__).resolve().parent
if str(scripts_path) not in sys.path:
    sys.path.append(str(scripts_path))

commands_file = Path("src/mercury_ocip/commands/commands.py")

if not commands_file.exists():
    print(f"ERROR: commands.py not found at {commands_file}")
    sys.exit(2)

source = commands_file.read_text()
tree = ast.parse(source)

word_re = re.compile(r"[A-Z]+(?=[A-Z][a-z])|[A-Z][a-z]+|[A-Z]+[0-9]*|[0-9]+")

unique_words: set[str] = set()

for node in tree.body:
    if isinstance(node, ast.ClassDef):
        class_name = node.name
        parts = word_re.findall(class_name)
        for p in parts:
            unique_words.add(p)

if not unique_words:
    print("No class names found.")
else:
    print("Unique words from class names:")
    for w in sorted(unique_words, key=lambda s: s.lower()):
        print(w)
