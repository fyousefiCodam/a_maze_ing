import sys
from typing import Dict


def error_exit(message: str) -> None:
    """
    Print a clear error message and exit the program cleanly.
    """
    print(f"Error: {message}")
    sys.exit(1)


def parse_config(path: str) -> Dict[str, str]:
    """
    Read the configuration file and perform format-level validation.
    Returns a dictionary containing raw string values.
    """
    config: Dict[str, str] = {}

    # ---- File access errors ----
    try:
        with open(path, "r") as file:
            lines = file.readlines()
    except FileNotFoundError:
        error_exit(f"Config file '{path}' not found.")
    except OSError:
        error_exit(f"Cannot open config file '{path}'.")

    # ---- Parse file line by line ----
    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()

        # Ignore comments and empty lines
        if not line or line.startswith("#"):
            continue

        # Enforce KEY=VALUE format
        if "=" not in line:
            error_exit(
                f"Invalid format at line {line_number}: expected KEY=VALUE."
            )

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if not key or not value:
            error_exit(
                f"Invalid key/value at line {line_number}: empty key or value."
            )

        config[key] = value

    # ---- Required keys validation ----
    required_keys = {
        "WIDTH",
        "HEIGHT",
        "ENTRY",
        "EXIT",
        "OUTPUT_FILE",
        "PERFECT",
    }

    missing_keys = required_keys - config.keys()
    if missing_keys:
        error_exit(
            f"Missing required config keys: {', '.join(sorted(missing_keys))}"
        )

    return config


def validate_config(raw_config: Dict[str, str]) -> Dict[str, object]:
    """
    Convert and validate configuration values.
    Returns a dictionary with validated, typed values.
    """

    validated: Dict[str, object] = {}

    # ---- WIDTH ----
    try:
        width = int(raw_config["WIDTH"])
    except ValueError:
        error_exit("WIDTH must be an integer.")

    if width <= 0:
        error_exit("WIDTH must be greater than 0.")

    validated["width"] = width

    # ---- HEIGHT ----
    try:
        height = int(raw_config["HEIGHT"])
    except ValueError:
        error_exit("HEIGHT must be an integer.")

    if height <= 0:
        error_exit("HEIGHT must be greater than 0.")

    validated["height"] = height

    # ---- ENTRY ----
    entry_raw = raw_config["ENTRY"].split(",")
    if len(entry_raw) != 2:
        error_exit("ENTRY must be in format x,y.")

    try:
        entry_x = int(entry_raw[0])
        entry_y = int(entry_raw[1])
    except ValueError:
        error_exit("ENTRY coordinates must be integers.")

    if not (0 <= entry_x < width and 0 <= entry_y < height):
        error_exit("ENTRY coordinates are outside maze bounds.")

    validated["entry"] = (entry_x, entry_y)

    # ---- EXIT ----
    exit_raw = raw_config["EXIT"].split(",")
    if len(exit_raw) != 2:
        error_exit("EXIT must be in format x,y.")

    try:
        exit_x = int(exit_raw[0])
        exit_y = int(exit_raw[1])
    except ValueError:
        error_exit("EXIT coordinates must be integers.")

    if not (0 <= exit_x < width and 0 <= exit_y < height):
        error_exit("EXIT coordinates are outside maze bounds.")

    if (exit_x, exit_y) == validated["entry"]:
        error_exit("ENTRY and EXIT must be different.")

    validated["exit"] = (exit_x, exit_y)

    # ---- PERFECT ----
    perfect_raw = raw_config["PERFECT"].lower()

    if perfect_raw == "true":
        validated["perfect"] = True
    elif perfect_raw == "false":
        validated["perfect"] = False
    else:
        error_exit("PERFECT must be True or False.")

    # ---- OUTPUT_FILE ----
    output_file = raw_config["OUTPUT_FILE"].strip()
    if not output_file:
        error_exit("OUTPUT_FILE cannot be empty.")

    validated["output_file"] = output_file

    return validated


def main() -> None:

    if len(sys.argv) != 2:
        error_exit("Usage: python3 a_maze_ing.py <config_file>")

    config_path = sys.argv[1]

    # ---- Config parsing and validating ----
    raw_config = parse_config(config_path)
    config = validate_config(raw_config)


    # Temporary confirmation output (for development only)
    print("Config file parsed successfully:")
    for key, value in config.items():
        print(f"{key} = {value}")



if __name__ == "__main__":
    main()
