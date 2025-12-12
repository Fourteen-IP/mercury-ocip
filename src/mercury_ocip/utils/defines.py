import re
import string
import secrets
import random


def to_snake_case(name: str) -> str:
    """Convert a string to snake_case format.

    Handles various input formats including CamelCase, spaced strings, and mixed cases.
    Inserts underscores at appropriate boundaries and converts to lowercase.

    Args:
        name: String to convert (e.g., "CamelCase", "Some Name", "XMLParser")

    Returns:
        String in snake_case format (e.g., "camel_case", "some_name", "xml_parser")

    Examples:
        >>> to_snake_case("CamelCase")
        'camel_case'
        >>> to_snake_case("Some Name Here")
        'some_name_here'
        >>> to_snake_case("XMLParser")
        'xml_parser'
    """
    name = name.strip()
    # Replace whitespace sequences with underscores
    name = re.sub(r"\s+", "_", name)
    # Insert underscore before uppercase letter following lowercase/number (CamelCase -> Camel_Case)
    name = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", name)
    # Insert underscore before lowercase letter following multiple uppercase (XMLParser -> XML_Parser)
    name = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", "_", name)
    return name.lower()


def snake_to_camel(name: str) -> str:
    parts = name.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


def is_snake_case(name: str) -> bool:
    return bool(re.fullmatch(r"[a-z]+(_[a-z0-9]+)*", name))


def is_camel_case(name: str) -> bool:
    return bool(re.fullmatch(r"[a-z]+(?:[A-Z][a-z0-9]*)*", name))


def is_boolean(name: str) -> bool:
    return bool(re.fullmatch(r"true|false", name.lower()))


def str_to_bool(name: str) -> bool:
    return name.lower() == "true"


def is_none(name: str) -> bool:
    data_type = isinstance(name, str)
    if not data_type:
        return False
    if name.lower().strip() == "none" or name.strip() == "":
        return True
    return False


def generate_secure(length: int = 16) -> str:
    """Generate a cryptographically secure random password string.

    Creates a password that meets Broadworks security requirements by ensuring
    at least one character from each required category (lowercase, uppercase,
    digit, symbol) is present, then fills the remainder with random characters
    and shuffles the result.

    Args:
        length: Desired password length (minimum 8 characters required)

    Returns:
        Randomly generated secure password string

    Raises:
        ValueError: If length is less than 8 characters

    Note:
        Uses secrets module for cryptographically secure random generation,
        ensuring the password is suitable for security-sensitive applications.
    """
    if length < 8:
        raise ValueError("Length Must Meet Broadworks Required Length Of 8")

    # Ensure at least one character from each required category
    lower_case_character_map = secrets.choice(string.ascii_lowercase)
    upper_case_character_map = secrets.choice(string.ascii_uppercase)
    digit_map = secrets.choice(string.digits)
    symbol_map = secrets.choice("!@#$%&*-_=+")

    # Fill remaining length with random characters from all allowed categories
    miscellaneous_character_map = string.ascii_letters + "!@#$%&*-_=+"
    miscellaneous_characters = [
        secrets.choice(miscellaneous_character_map) for _ in range(length - 4)
    ]

    # Combine required characters with miscellaneous ones
    secure_str = (
        list(
            lower_case_character_map + upper_case_character_map + digit_map + symbol_map
        )
        + miscellaneous_characters
    )
    # Shuffle to randomise the position of required characters
    random.shuffle(secure_str)

    return "".join(secure_str)


def normalise_phone_number(phone: str) -> str:
    """Normalise a phone number string by removing quotes and excess whitespace.

    Cleans phone number strings that may have been wrapped in quotes or contain
    leading/trailing whitespace. Returns an empty string for None or empty input.

    Args:
        phone: Phone number string that may contain quotes or whitespace

    Returns:
        Cleaned phone number string with quotes and whitespace removed, or empty
        string if input is None or empty

    Examples:
        >>> normalise_phone_number('"+1-4072383011"')
        '+1-4072383011'
        >>> normalise_phone_number("  '+1-4072383011'  ")
        '+1-4072383011'
        >>> normalise_phone_number("")
        ''
    """
    if not phone or phone.strip() == "":
        return ""

    # Remove outer quotes (single or double) and whitespace
    cleaned = phone.strip()
    if (cleaned.startswith('"') and cleaned.endswith('"')) or (
        cleaned.startswith("'") and cleaned.endswith("'")
    ):
        cleaned = cleaned[1:-1]

    return cleaned.strip()


def expand_phone_range(range_str: str) -> list[str]:
    """Expand a phone number range string into a list of individual numbers.

    Args:
        range_str: String like '+1-4072383011 - +1-4072383017'

    Returns:
        List of phone numbers in the range, e.g. ['+1-4072383011', '+1-4072383012', ...]
    """
    if " - " not in range_str:
        return [range_str]

    parts = range_str.split(" - ")
    if len(parts) != 2:
        return [range_str]

    start_str, end_str = parts[0].strip(), parts[1].strip()

    # Extract prefix (everything before the last number sequence) and numeric parts
    # For '+1-4072383011', we want prefix='+1-' and number='4072383011'
    # Regex matches digits at the end of the string to extract the numeric portion
    start_match = re.search(r"(\d+)$", start_str)
    end_match = re.search(r"(\d+)$", end_str)

    if not start_match or not end_match:
        return [range_str]

    start_num = int(start_match.group(1))
    end_num = int(end_match.group(1))
    # Extract the prefix by taking everything before the numeric match position
    prefix = start_str[: start_match.start()]

    # Generate all numbers in range (inclusive of both start and end)
    numbers = []
    for num in range(start_num, end_num + 1):
        numbers.append(f"{prefix}{num}")

    return numbers


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
