import csv
import os
from typing import List, Dict, Any


class FileHandler:
    """
    File handler class
    """

    @staticmethod
    def read_csv_to_dict(file_path: str) -> List[Dict[str, Any]]:
        """Read a CSV file and return a list of dictionaries"""
        FileHandler._check_file_exists(file_path)
        with open(file_path, mode="r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            return [dict(row) for row in reader if any(row.values())]

    def _check_file_exists(file_path: str) -> bool:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist")
        return True
