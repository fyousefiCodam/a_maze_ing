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


def main() -> None:

    if len(sys.argv) != 2:
        error_exit("Usage: python3 a_maze_ing.py <config_file>")

    config_path = sys.argv[1]

    # ---- Config parsing ----
    config = parse_config(config_path)

    # Temporary confirmation output (for development only)
    print("Config file parsed successfully:")
    for key, value in config.items():
        print(f"{key} = {value}")


if __name__ == "__main__":
    main()
