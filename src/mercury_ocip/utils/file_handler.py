import csv
import os
import unicodedata
from typing import List, Dict, Any


class FileHandler:
    """
    File handler class
    """

    @staticmethod
    def _normalise(value: Any) -> Any:
        """Normalise a string value by removing accents and special whitespace."""
        if not isinstance(value, str):
            return value
        # NFKD decomposes characters: é → e + combining accent, \xa0 → space
        value = unicodedata.normalize("NFKD", value)
        # Drop combining marks (accents) so é → e, ñ → n, etc.
        value = "".join(c for c in value if unicodedata.category(c) != "Mn")
        # Collapse any remaining whitespace runs
        return " ".join(value.split())

    @staticmethod
    def read_csv_to_dict(file_path: str) -> List[Dict[str, Any]]:
        """Read a CSV file and return a list of dictionaries"""
        FileHandler._check_file_exists(file_path)
        with open(file_path, mode="r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            return [
                {k: FileHandler._normalise(v) for k, v in row.items()}
                for row in reader
                if any(row.values())
            ]

    def _check_file_exists(file_path: str) -> bool:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist")
        return True
