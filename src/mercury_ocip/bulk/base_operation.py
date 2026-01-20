from abc import ABC
from typing import List, Dict, Any, cast
import re

from mercury_ocip.client import BaseClient
from mercury_ocip.commands.base_command import OCICommand, ErrorResponse, OCINil
from mercury_ocip.utils.file_handler import FileHandler
from mercury_ocip.utils.defines import (
    to_snake_case,
    is_boolean,
    str_to_bool,
    is_empty,
    normalise_phone_number,
)
from mercury_ocip.libs.types import OCIResponse


class BaseBulkOperations(ABC):
    """Base class for all bulk operations

    This class is used to create a base class for all bulk operations.
    It contains the shared logic for all bulk operations.

    Args:
        client (BaseClient): Client object to be used in the scripts.
    """

    operation_mapping: Dict[str, Dict[str, Any]]  # Unique to each entity class

    def __init__(self, client: BaseClient) -> None:
        self.client = client
        self.logger = client.logger

    def execute_from_csv(
        self, csv_path: str, dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        """Create users from CSV file

        This method is used with the packages upload sheets.

        Args:
            csv_path (str): Path to the CSV file
            dry_run (bool, optional): If True, the operation will not be executed. Defaults to False.

        Returns:
            List[Dict[str, Any]]: List of bwks entities created.
        """
        self.logger.info(
            f"Starting bulk operation from CSV: {csv_path}, dry_run={dry_run}"
        )
        data: list[dict[str, Any]] = FileHandler.read_csv_to_dict(csv_path)
        self.logger.debug(f"Loaded {len(data)} rows from CSV file")
        parsed_data: list[Dict[str, Any]] = self._parse_csv(data)
        return self.execute_from_data(parsed_data, dry_run)

    def execute_from_data(
        self, data: List[Dict[str, Any]], dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        """Create users from data

        This method is used directly in the package via IDE or CLI.

        Args:
            data (List[Dict[str, Any]]): List of users to create
            dry_run (bool, optional): If True, the operation will not be executed. Defaults to False.

        Returns:
            List[Dict[str, Any]]: List of bwks entities created.
        """
        operation_class = self.__class__.__name__
        self.logger.info(
            f"Starting bulk operation: {operation_class} with {len(data)} items, dry_run={dry_run}"
        )
        results: list[dict[str, Any]] = []
        success_count = 0
        failure_count = 0

        for i, row in enumerate(data):
            try:
                operation = row.pop("operation")
                # Create command from data
                command: OCICommand = self._create_command(row, operation)

                # Validate data by attempting to create command (pydantic will error if invalid)
                if not dry_run:
                    response = self._execute_command(command)
                else:
                    response = None

                return_data = {
                    "index": i,
                    "data": row,
                    "command": command,
                    "response": response,
                    "success": True,
                }

                # If response is an ErrorResponse and not package issue
                if isinstance(response, ErrorResponse):
                    return_data["response"] = response.summary  # type: ignore
                    return_data["detail"] = response.detail  # type: ignore
                    return_data["success"] = False
                    failure_count += 1
                    self.logger.warning(
                        f"Row {i}: {operation} failed - {response.summary}"
                    )
                else:
                    success_count += 1
                    self.logger.debug(f"Row {i}: {operation} succeeded")

                results.append(return_data)

            except Exception as e:
                failure_count += 1
                # Pydantic validation errors or other failures
                self.logger.error(f"Row {i}: Failed to execute operation - {str(e)}")
                results.append(
                    {
                        "index": i,
                        "data": row,
                        "command": None,
                        "response": None,
                        "success": False,
                        "error": str(e),
                    }
                )

        self.logger.info(
            f"Bulk operation {operation_class} completed: {success_count} successful, {failure_count} failed, Time Saved {success_count * 1.25}"
        )
        return results

    def _parse_csv(self, data: list[dict[str, Any]]) -> List[Dict[str, Any]]:
        """Shared CSV parsing logic.

        Takes in path to CSV file and parses the data to a list of dictionaries.

        Args:
            data (list[dict[str, Any]]): List of dictionaries representing bwks entities.

        Returns:
            List[Dict[str, Any]]: List of dict representing bwks entities.
        """
        processed_data: list[Dict[str, Any]] = []
        for row in data:
            processed_data.append(self._process_row(row))
        return processed_data

    def _process_row(self, row: dict[str, Any]) -> dict[str, Any]:
        """Process a single row of data.

        Uses a dynamic token-based parser to handle arbitrary nesting of
        objects and arrays at any depth.

        Args:
            row (dict[str, Any]): A single row of data.

        Returns:
            dict[str, Any]: A single row of data with nested structures built.
        """
        result: Dict[str, Any] = {}
        operation = row["operation"]

        for key, value in row.items():
            key = to_snake_case(key)

            # Skip None values and empty strings
            if value is None or (isinstance(value, str) and is_empty(value)):
                continue

            # Convert 'null' string to Python None (explicit nil marker)
            if isinstance(value, str) and value.strip().lower() == "null":
                value = OCINil()
            else:
                value = value.strip()

            # Type conversions
            if isinstance(value, str) and is_boolean(value):
                value = str_to_bool(value)
            elif isinstance(value, str) and key in self.operation_mapping.get(
                operation, {}
            ).get("integer_fields", []):
                value = int(value)
            elif isinstance(value, str) and value.startswith("+"):
                # BWKS needs numbers as str and in E.164 formatting
                value = normalise_phone_number(value)

            # Parse the key path and set the value dynamically
            # Skip 'operation' as it's metadata
            if key != "operation":
                segments = self._parse_key_path(key)
                self._set_nested_value(result, segments, value)
            else:
                result[key] = value

        # Clean up arrays - remove None padding where appropriate
        self._clean_arrays(result)

        return result

    def _clean_arrays(self, data: Any) -> None:
        """Recursively clean arrays by removing trailing None values.

        Args:
            data (Any): The data structure to clean (dict, list, or primitive)
        """
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list):
                    # Remove None values from lists (they were used for padding)
                    data[key] = [item for item in value if item is not None]
                    # Recursively clean nested structures
                    for item in data[key]:
                        self._clean_arrays(item)
                else:
                    # Recursively clean nested objects
                    self._clean_arrays(value)
        elif isinstance(data, list):
            for item in data:
                self._clean_arrays(item)

    def _parse_key_path(self, key: str) -> List[tuple[str, int | None]]:
        """Parse a CSV column key into a list of path segments.

        Each segment is a tuple of (field_name, array_index) where array_index
        is None for objects and an integer for array elements.

        Examples:
            'user_id' -> [('user_id', None)]
            'alias[0]' -> [('alias', 0)]
            'address.city' -> [('address', None), ('city', None)]
            'alias[0].value' -> [('alias', 0), ('value', None)]
            'contact.phones[0]' -> [('contact', None), ('phones', 0)]
            'service.data[1].name' -> [('service', None), ('data', 1), ('name', None)]

        Args:
            key (str): The CSV column key to parse

        Returns:
            List[tuple[str, int | None]]: List of (field_name, array_index) tuples
        """
        segments: List[tuple[str, int | None]] = []
        # Split by dots first, but we need to handle brackets within each part
        parts = key.split(".")

        for part in parts:
            # Check if this part has an array index
            if "[" in part and "]" in part:
                # Extract field name and index
                match = re.match(r"^(\w+)\[(\d+)\]$", part)
                if match:
                    field_name = match.group(1)
                    index = int(match.group(2))
                    segments.append((field_name, index))
                else:
                    # Malformed, treat as regular field
                    segments.append((part, None))
            else:
                # Regular field name
                segments.append((part, None))

        return segments

    def _set_nested_value(
        self, result: Dict[str, Any], segments: List[tuple[str, int | None]], value: Any
    ) -> None:
        """Set a value in a nested structure based on parsed path segments.

        Dynamically builds the nested structure (dicts and lists) as needed.

        Args:
            result (Dict[str, Any]): The root dictionary to build into
            segments (List[tuple[str, int | None]]): Path segments from _parse_key_path
            value (Any): The value to set at the end of the path
        """
        current = result

        # Navigate through all segments except the last one
        for i, (field_name, array_index) in enumerate(segments[:-1]):
            next_segment = segments[i + 1]
            _, next_is_array = next_segment

            if array_index is not None:
                # Current segment is an array element
                if field_name not in current:
                    current[field_name] = []

                # Ensure the list is large enough
                while len(current[field_name]) <= array_index:
                    current[field_name].append(None)

                # Initialize the array element if needed
                if current[field_name][array_index] is None:
                    if next_is_array is not None:
                        # Next segment is also an array, so this should be a dict
                        current[field_name][array_index] = {}
                    else:
                        # Next segment is an object field
                        current[field_name][array_index] = {}

                current = current[field_name][array_index]
            else:
                # Current segment is an object field
                if field_name not in current:
                    if next_is_array is not None:
                        # Next segment is an array
                        current[field_name] = {}
                    else:
                        # Next segment is an object
                        current[field_name] = {}

                current = current[field_name]

        # Handle the last segment
        last_field, last_index = segments[-1]

        if last_index is not None:
            # Last segment is an array element - list of primitives
            if last_field not in current:
                current[last_field] = []

            while len(current[last_field]) <= last_index:
                current[last_field].append(None)

            current[last_field][last_index] = value
        else:
            # Last segment is a simple field
            current[last_field] = value

    def _create_command(self, data: Dict[str, Any], operation: str) -> OCICommand:
        """Create a command from the data.

        This method is used to create a command from the data.

        Args:
            data (Dict[str, Any]): A single row of data.

        Returns:
            OCICommand: A command.
        """
        mapping: dict[str, Any] = self.operation_mapping[operation]
        processed_data: dict[str, Any] = data.copy()

        command_class: type[OCICommand] | None = self.client._dispatch_table.get(
            mapping["command"]
        )

        if not command_class:
            raise ValueError(
                f"Command {mapping['command']} not found in dispatch table"
            )

        # Handle defaults needed in command if not given from user
        if mapping.get("defaults"):
            self._handle_defaults(processed_data, mapping["defaults"])
        # Handle nested types
        if mapping.get("nested_types"):
            self._handle_nested_types(processed_data, mapping["nested_types"])

        # Create command - pydantic will validate and error if data doesn't meet standards
        try:
            return command_class(**processed_data)
        except Exception as e:
            raise ValueError(f"Error creating command: {e}")

    def _handle_defaults(self, data: Dict[str, Any], defaults: Any) -> Dict:
        """
        Handles applying default fields needed in some classes but has been made optional for usability

        Args:
            data (Dict[str, Any]): The data to apply defaults to.
            defaults (Any): The defaults to apply.

        Returns:
            Dict: The data with defaults applied.
        """
        for key, value in defaults.items():
            if key not in data:
                data[key] = value
            elif isinstance(data[key], dict) and isinstance(value, dict):
                self._handle_defaults(data[key], value)
        return data

    def _handle_nested_types(
        self, processed_data: Dict[str, Any], nested_types: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handles nested types in the data.

        Supports choice structures (XSD choice elements) via explicit type fields.
        For nillable fields, use type field value OCINil (or 'null' in CSV) to explicitly set to None.

        Args:
            processed_data (Dict[str, Any]): The data to process.
            nested_types (Dict[str, Any]): The nested types to process.

        Returns:
            Dict[str, Any]: The processed data.
        """
        from mercury_ocip.utils.defines import to_snake_case, snake_to_camel

        for nested_field, nested_type_class in nested_types.items():
            # Handle choice structures (XSD choice elements) - process these first
            if isinstance(nested_type_class, dict) and "_choice" in nested_type_class:
                choice_options = nested_type_class["_choice"]

                # Get the explicit type field name (e.g., "endpoint_type" or defaults to "{field}_type")
                type_field = choice_options.get("_choice_field", f"{nested_field}_type")

                # Use .get() - safe even if type_field doesn't exist (returns None)
                choice_key = processed_data.get(type_field)

                # Remove the type field - it's just metadata, not part of the schema
                if type_field in processed_data:
                    processed_data.pop(type_field)

                # Handle explicit nil: if type is OCINil or None (from 'null' string), set field to None
                if choice_key is None or isinstance(choice_key, OCINil):
                    processed_data[nested_field] = OCINil()
                    continue

                # Normalise the choice key to snake_case to match our mapping keys
                if isinstance(choice_key, str):
                    choice_key = to_snake_case(choice_key)
                else:
                    # If it's not a string, skip (shouldn't happen, but be safe)
                    processed_data[nested_field] = None
                    continue

                # Get the chosen structure
                if choice_key not in choice_options:
                    raise ValueError(
                        f"Invalid choice type '{choice_key}' for field '{nested_field}'. "
                        f"Valid options: {list(k for k in choice_options.keys() if not k.startswith('_'))}"
                    )

                chosen_structure = choice_options[choice_key]

                # Get the data for the chosen option from ROOT LEVEL (not nested under field name)
                # Try both snake_case and camelCase versions
                chosen_data = processed_data.get(choice_key)
                if chosen_data is None:
                    camel_key = snake_to_camel(choice_key)
                    chosen_data = processed_data.get(camel_key)

                # If no data found, that's okay - might be empty structure
                if chosen_data is None:
                    chosen_data = {}

                # Remove the choice data from root level (we'll assign it to nested_field)
                if choice_key in processed_data:
                    processed_data.pop(choice_key)
                else:
                    camel_key = snake_to_camel(choice_key)
                    if camel_key in processed_data:
                        processed_data.pop(camel_key)

                # Process the chosen structure normally (it's just a regular nested type dict)
                if isinstance(chosen_structure, dict):
                    command_class_name, nested_structure = next(
                        iter(chosen_structure.items())
                    )
                    # Recursively process the nested structure
                    if nested_structure:
                        chosen_data = self._handle_nested_types(
                            chosen_data, nested_structure
                        )

                    # Create the command object
                    if command_class := self.client._dispatch_table.get(
                        command_class_name
                    ):
                        processed_data[nested_field] = command_class(**chosen_data)
                    else:
                        raise ValueError(
                            f"Command class '{command_class_name}' not found in dispatch table"
                        )
                else:
                    # Simple string type (shouldn't happen in choices, but handle it)
                    if command_class := self.client._dispatch_table.get(
                        chosen_structure
                    ):
                        processed_data[nested_field] = command_class(**chosen_data)
                    else:
                        raise ValueError(
                            f"Command class '{chosen_structure}' not found in dispatch table"
                        )
                continue

            # Universal Nillable handling - check if field value is Nillable (explicit nil)
            if isinstance(processed_data, dict):
                field_value = processed_data.get(nested_field)
                if isinstance(field_value, OCINil):
                    # Preserve Nillable - don't process, just keep it as-is
                    continue

            # Regular nested type handling (non-choice)
            nested_data: Any = ""
            # Try to get the data, but don't pop it yet
            if isinstance(processed_data, dict):
                nested_data = processed_data.get(nested_field)
                if not nested_data:
                    continue
                processed_data.pop(nested_field)
            elif isinstance(processed_data, list):
                nested_data = processed_data

            # If the field doesn't exist in the data, skip it
            if nested_data is None:
                continue

            if isinstance(nested_type_class, dict):
                command_class_name, nested_structure = next(
                    iter(nested_type_class.items())
                )
                # First, recursively process the nested structure
                nested_data = self._handle_nested_types(nested_data, nested_structure)

                # Then create the command object using the command class name
                if command_class := self.client._dispatch_table.get(command_class_name):
                    nested_data = command_class(**nested_data)

            elif isinstance(nested_data, list):
                for i in range(len(nested_data)):
                    if command_class := self.client._dispatch_table.get(
                        nested_type_class
                    ):
                        nested_data[i] = command_class(**nested_data[i])

            else:
                if command_class := self.client._dispatch_table.get(nested_type_class):
                    nested_data = command_class(**nested_data)

            processed_data[nested_field] = nested_data

        return processed_data

    def _execute_command(self, command: OCICommand) -> OCIResponse | None:
        """Execute a command.

        This method is used to execute a command.

        Args:
            command (OCICommand): The command to execute.
        """
        try:
            return cast(OCIResponse | None, self.client.command(command))
        except Exception as e:
            raise ValueError(f"Error executing command: {e}")
