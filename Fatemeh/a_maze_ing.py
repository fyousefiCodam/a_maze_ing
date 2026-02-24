import sys
from typing import Dict, List, NoReturn, Optional, Tuple, TypedDict

from ascii_ui import run_ui
from maze_generator import MazeGenerator


class ValidatedConfig(TypedDict):
    """Typed structure for validated maze configuration."""

    width: int
    height: int
    entry: Tuple[int, int]
    exit: Tuple[int, int]
    perfect: bool
    seed: Optional[int]
    output_file: str


def error_exit(message: str) -> NoReturn:
    """Print a clear error message and exit the program cleanly.

    Args:
        message: Human-readable error description.
    """
    print(f"Error: {message}")
    sys.exit(1)


def parse_config(path: str) -> Dict[str, str]:
    """Read the configuration file and perform format-level validation.

    Returns a dictionary containing raw string values.

    Args:
        path: Path to the configuration file.

    Returns:
        Dictionary mapping config keys to their raw string values.
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
                f"Invalid format at line {line_number}: "
                f"expected KEY=VALUE."
            )

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if not key or not value:
            error_exit(
                f"Invalid key/value at line {line_number}: "
                f"empty key or value."
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
            f"Missing required config keys: "
            f"{', '.join(sorted(missing_keys))}"
        )

    return config


def validate_config(raw_config: Dict[str, str]) -> ValidatedConfig:
    """Convert and validate configuration values.

    Args:
        raw_config: Dictionary of raw string config values.

    Returns:
        ValidatedConfig TypedDict with validated, typed values.
    """
    # ---- WIDTH ----
    try:
        width = int(raw_config["WIDTH"])
    except ValueError:
        error_exit("WIDTH must be an integer.")

    if width <= 0:
        error_exit("WIDTH must be greater than 0.")

    # ---- HEIGHT ----
    try:
        height = int(raw_config["HEIGHT"])
    except ValueError:
        error_exit("HEIGHT must be an integer.")

    if height <= 0:
        error_exit("HEIGHT must be greater than 0.")

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

    if (exit_x, exit_y) == (entry_x, entry_y):
        error_exit("ENTRY and EXIT must be different.")

    # ---- PERFECT ----
    perfect_raw = raw_config["PERFECT"].lower()

    if perfect_raw == "true":
        perfect = True
    elif perfect_raw == "false":
        perfect = False
    else:
        error_exit("PERFECT must be True or False.")

    # ---- SEED (optional) ----
    seed: Optional[int] = None
    if "SEED" in raw_config:
        try:
            seed = int(raw_config["SEED"])
        except ValueError:
            error_exit("SEED must be an integer.")

    # ---- OUTPUT_FILE ----
    output_file = raw_config["OUTPUT_FILE"].strip()
    if not output_file:
        error_exit("OUTPUT_FILE cannot be empty.")

    return ValidatedConfig(
        width=width,
        height=height,
        entry=(entry_x, entry_y),
        exit=(exit_x, exit_y),
        perfect=perfect,
        seed=seed,
        output_file=output_file,
    )


def write_output_file(
    grid: List[List[int]],
    entry: Tuple[int, int],
    exit_pos: Tuple[int, int],
    path: str,
    output_file: str,
) -> None:
    """Write the maze output file in the required format.

    Args:
        grid: 2-D list of cell bitmasks.
        entry: Entry coordinates (x, y).
        exit_pos: Exit coordinates (x, y).
        path: Solution path string (e.g. 'EESSNN').
        output_file: Output filename.
    """
    try:
        with open(output_file, "w") as file:
            # Write maze grid (hex)
            for row in grid:
                hex_row = "".join(format(cell, "x") for cell in row)
                file.write(hex_row + "\n")

            file.write("\n")

            file.write(f"{entry[0]},{entry[1]}\n")
            file.write(f"{exit_pos[0]},{exit_pos[1]}\n")
            file.write(f"{path}\n")

    except OSError:
        error_exit(f"Cannot write to output file '{output_file}'.")


def path_to_positions(
    entry: tuple[int, int],
    path: str
) -> list[tuple[int, int]]:
    x, y = entry
    positions = [(x, y)]

    for move in path:
        if move == "N":
            y -= 1
        elif move == "S":
            y += 1
        elif move == "E":
            x += 1
        elif move == "W":
            x -= 1
        positions.append((x, y))

    return positions


def main() -> None:
    """Run the maze generator and launch the interactive ASCII UI."""
    if len(sys.argv) != 2:
        error_exit("Usage: python3 a_maze_ing.py <config_file>")

    config_path = sys.argv[1]

    # Config parsing and validation
    raw_config = parse_config(config_path)
    config = validate_config(raw_config)

    width: int = config["width"]
    height: int = config["height"]
    entry: Tuple[int, int] = config["entry"]
    maze_exit: Tuple[int, int] = config["exit"]
    perfect: bool = config["perfect"]
    seed: Optional[int] = config["seed"]
    output_file: str = config["output_file"]

    # Inner helper: generate, solve, write, return UI data
    def build_and_write(
        use_seed: Optional[int],
    ) -> Tuple[List[List[int]], Tuple[int, int], Tuple[int, int], str]:
        """Generate a maze, write output file, return data for the UI."""
        gen = MazeGenerator(
            width=width,
            height=height,
            entry=entry,
            exit_pos=maze_exit,
            seed=use_seed,
            perfect=perfect,
        )
        gen.generate()
        new_path = gen.solve()
        write_output_file(
            gen.grid, entry, maze_exit, new_path, output_file
        )
        return gen.grid, entry, maze_exit, new_path

    # Generate initial maze (using seed from config if provided)
    grid, _, _, path = build_and_write(seed)

    print("Output file generated successfully.")

    # Re-generate callback passed to the UI (option 1)
    def regenerate() -> (
        Tuple[List[List[int]], Tuple[int, int], Tuple[int, int], str]
    ):
        """Return a fresh random maze and write the updated output file."""
        return build_and_write(None)

    # Launch the interactive ASCII UI
    run_ui(
        grid=grid,
        width=width,
        height=height,
        entry=entry,
        exit_pos=maze_exit,
        path_str=path,
        regenerate_fn=regenerate,
    )


if __name__ == "__main__":
    main()
