import sys
from typing import Dict, Tuple


def error_exit(message: str) -> None:
    """print error message and exit cleanly"""
    print(f"Error: {message}")
    sys.exit(1)


def parse_config(path: str) -> Dict[str, object]:
    """
    Read and validate the config file
    returns a dictionary with parsed values
    """
    config: Dict[str, object] = {}

    try:
        with open(path, "r") as file:
            lines = file.readlines()
    except FileNotFoundError:
        error_exit(f"Config file '{path}' not found.")
    except OSError:
        error_exit(f"Cannot open config file '{path}'.")
    
    for line_number, raw_line in enumerate(lines, start = 1):
        # remove spaces, tabs, \n
        line = raw_line.strip()

        #ignore comments and empty lines
        if not line or line.startswith("#"):
            continue
        
        # every valid config line must be: KEY=VALUE
        if "=" not in line:
            error_exit(f"Invalid format at line {line_number}: missing '='.")
        
        # splits the line into two parts -> 1 split only once
        key, value = line.split("=", 1)

        # remove extra spaces
        key = key.strip()
        value = value.strip()

        if not key or not value:
            error_exit(f"Invalid key/value at line {line_number}.")
        
        # adds the pair to the dictionary
        config[key] = value
    
    required_keys = {
        "WIDTH",
        "HEIGHT",
        "ENTRY",
        "EXIT",
        "OUTPUT_FILE",
        "PERFECT",
    }

    missing = required_keys - config.keys()
    if missing:
        error_exit(f"Missing required config keys: {', '.join(missing)}")

    return config


def main() -> None:
    if len(sys.argv) != 2:
        error_exit("Usage: python3 a_maze_ing.py <config_file>")

    config_path = sys.argv[1]
    config = parse_config(config_path)

    # Temporary confirmation output (will be removed later)
    print("Config file parsed successfully.")
    for key, value in config.items():
        print(f"{key} = {value}")


if __name__ == "__main__":
    main()

