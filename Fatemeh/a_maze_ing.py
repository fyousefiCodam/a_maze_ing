"""a_maze_ing.py – Entry point for the A-Maze-ing application.

Reads a config file, generates a maze, writes the output file, and
launches the interactive ASCII terminal UI.

Usage::

    python3 a_maze_ing.py config.txt
"""

from __future__ import annotations

import sys
from typing import Dict, List, NoReturn, Optional, Tuple

from ascii_ui import run_ui
from maze_generator import MazeGenerator


# ---------------------------------------------------------------------------
# Config types
# ---------------------------------------------------------------------------


class ValidatedConfig:
    """Validated, typed maze configuration parsed from a config file."""

    def __init__(
        self,
        width: int,
        height: int,
        entry: Tuple[int, int],
        exit: Tuple[int, int],
        perfect: bool,
        seed: Optional[int],
        output_file: str,
    ) -> None:
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.perfect = perfect
        self.seed = seed
        self.output_file = output_file


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def error_exit(message: str) -> NoReturn:
    """Print a clear error message and exit the program cleanly.

    Args:
        message: Human-readable error description.
    """
    print(f"Error: {message}")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Config parsing
# ---------------------------------------------------------------------------


def parse_config(path: str) -> Dict[str, str]:
    """Read the configuration file and perform format-level validation.

    Args:
        path: Path to the configuration file.

    Returns:
        Dictionary mapping config keys to their raw string values.
    """
    config: Dict[str, str] = {}

    try:
        with open(path, "r") as file:
            lines = file.readlines()
    except FileNotFoundError:
        error_exit(f"Config file '{path}' not found.")
    except OSError:
        error_exit(f"Cannot open config file '{path}'.")

    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()

        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            error_exit(
                f"Invalid format at line {line_number}: "
                "expected KEY=VALUE."
            )

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if not key or not value:
            error_exit(
                f"Invalid key/value at line {line_number}: "
                "empty key or value."
            )

        config[key] = value

    required_keys = {"WIDTH", "HEIGHT", "ENTRY",
                     "EXIT", "OUTPUT_FILE", "PERFECT"}
    missing_keys = required_keys - config.keys()
    if missing_keys:
        error_exit(
            f"Missing required config keys: {', '.join(sorted(missing_keys))}"
        )

    return config


def validate_config(raw_config: Dict[str, str]) -> ValidatedConfig:
    """Convert and validate configuration values.

    Args:
        raw_config: Dictionary of raw string config values.

    Returns:
        ValidatedConfig with validated, typed values.
    """
    # WIDTH
    try:
        width = int(raw_config["WIDTH"])
    except ValueError:
        error_exit("WIDTH must be an integer.")
    if width <= 0:
        error_exit("WIDTH must be greater than 0.")

    # HEIGHT
    try:
        height = int(raw_config["HEIGHT"])
    except ValueError:
        error_exit("HEIGHT must be an integer.")
    if height <= 0:
        error_exit("HEIGHT must be greater than 0.")

    # ENTRY
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

    # EXIT
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

    # PERFECT
    perfect_raw = raw_config["PERFECT"].lower()
    if perfect_raw == "true":
        perfect = True
    elif perfect_raw == "false":
        perfect = False
    else:
        error_exit("PERFECT must be True or False.")

    # SEED (optional)
    seed: Optional[int] = None
    if "SEED" in raw_config:
        try:
            seed = int(raw_config["SEED"])
        except ValueError:
            error_exit("SEED must be an integer.")

    # OUTPUT_FILE
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


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


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
            for row in grid:
                hex_row = "".join(format(cell, "x") for cell in row)
                file.write(hex_row + "\n")
            file.write("\n")
            file.write(f"{entry[0]},{entry[1]}\n")
            file.write(f"{exit_pos[0]},{exit_pos[1]}\n")
            file.write(f"{path}\n")
    except OSError:
        error_exit(f"Cannot write to output file '{output_file}'.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the maze generator and launch the interactive ASCII UI."""
    if len(sys.argv) != 2:
        error_exit("Usage: python3 a_maze_ing.py <config_file>")

    config = validate_config(parse_config(sys.argv[1]))

    width = config.width
    height = config.height
    entry = config.entry
    maze_exit = config.exit
    perfect = config.perfect
    seed = config.seed
    output_file = config.output_file

    def build_and_write(
        use_seed: Optional[int],
    ) -> Tuple[
        List[List[int]],
        Tuple[int, int],
        Tuple[int, int],
        str,
        set[Tuple[int, int]],
    ]:
        """Generate a maze, write the output file, return data for the UI."""
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
        write_output_file(gen.grid, entry, maze_exit, new_path, output_file)
        return gen.grid, entry, maze_exit, new_path, gen.forbidden_cells

    grid, _, _, path, forbidden = build_and_write(seed)
    print("Output file generated successfully.")

    def regenerate() -> Tuple[
        List[List[int]],
        Tuple[int, int],
        Tuple[int, int],
        str,
        set[Tuple[int, int]],
    ]:
        """Return a fresh random maze and write the updated output file."""
        return build_and_write(None)

    run_ui(
        grid=grid,
        width=width,
        height=height,
        entry=entry,
        exit_pos=maze_exit,
        path_str=path,
        forbidden_cells=forbidden,
        regenerate_fn=regenerate,
    )


if __name__ == "__main__":
    main()
