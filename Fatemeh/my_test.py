import sys
from typing import Dict

from ascii_ui import run_ui


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
        error_exit("WIDTH must be integer.")

    if width <= 0:
        error_exit("WIDTHmust be greater than 0.")
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


def generate_maze(
    width: int,
    height: int,
    entry: tuple[int, int],
    exit_pos: tuple[int, int],
    seed: int = 42,
) -> tuple[list[list[int]], tuple[int, int], tuple[int, int], str]:
    """Generate a perfect maze using the recursive backtracker algorithm.

    The recursive backtracker (depth-first search with random neighbour
    selection) produces a perfect maze: every cell is reachable and there
    is exactly one path between any two cells.

    Wall bitmask per cell (matches subject spec):
        bit 0 (1) = North wall closed
        bit 1 (2) = East  wall closed
        bit 2 (4) = South wall closed
        bit 3 (8) = West  wall closed

    Args:
        width: Number of columns.
        height: Number of rows.
        entry: Entry cell (x, y).
        exit_pos: Exit cell (x, y).
        seed: Random seed for reproducibility.

    Returns:
        Tuple of (grid, entry, exit_pos, path_string).
    """
    import random
    from collections import deque

    rng = random.Random(seed)

    # Start with every wall closed (value 0b1111 = 15)
    grid: list[list[int]] = [[0xF] * width for _ in range(height)]

    # Direction helpers: (dx, dy, wall_from, wall_to)
    # wall_from = bit to clear in current cell
    # wall_to   = bit to clear in neighbour cell
    DIRS = [
        (0, -1, 0b0001, 0b0100),   # North: clear N in cur, S in neighbour
        (1,  0, 0b0010, 0b1000),   # East:  clear E in cur, W in neighbour
        (0,  1, 0b0100, 0b0001),   # South: clear S in cur, N in neighbour
        (-1, 0, 0b1000, 0b0010),   # West:  clear W in cur, E in neighbour
    ]

    # --- Recursive backtracker (iterative with explicit stack) ---
    visited: list[list[bool]] = [
        [False] * width for _ in range(height)
    ]
    start_x, start_y = entry
    stack = [(start_x, start_y)]
    visited[start_y][start_x] = True

    while stack:
        cx, cy = stack[-1]

        # Collect unvisited neighbours
        neighbours = []
        for dx, dy, wall_cur, wall_nb in DIRS:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < width and 0 <= ny < height:
                if not visited[ny][nx]:
                    neighbours.append((nx, ny, wall_cur, wall_nb))

        if neighbours:
            nx, ny, wall_cur, wall_nb = rng.choice(neighbours)
            # Carve passage: remove the shared wall in both cells
            grid[cy][cx] &= ~wall_cur
            grid[ny][nx] &= ~wall_nb
            visited[ny][nx] = True
            stack.append((nx, ny))
        else:
            stack.pop()

    # --- BFS to find the shortest path from entry to exit ---
    ex, ey = exit_pos
    prev: dict[tuple[int, int], tuple[int, int] | None] = {entry: None}
    queue: deque[tuple[int, int]] = deque([entry])

    DIR_LETTER = {
        (0, -1): 'N',
        (1,  0): 'E',
        (0,  1): 'S',
        (-1, 0): 'W',
    }
    DIR_WALL = {
        (0, -1): 0b0001,
        (1,  0): 0b0010,
        (0,  1): 0b0100,
        (-1, 0): 0b1000,
    }

    came_from: dict[tuple[int, int], tuple[tuple[int, int], str]] = {}

    found = False
    while queue and not found:
        cx, cy = queue.popleft()
        for (dx, dy), letter in DIR_LETTER.items():
            nx, ny = cx + dx, cy + dy
            nb = (nx, ny)
            if not (0 <= nx < width and 0 <= ny < height):
                continue
            # Only traverse if the wall in that direction is open
            if grid[cy][cx] & DIR_WALL[(dx, dy)]:
                continue
            if nb in came_from or nb == entry:
                continue
            came_from[nb] = ((cx, cy), letter)
            if nb == (ex, ey):
                found = True
                break
            queue.append(nb)

    # Reconstruct path string
    path_chars = []
    cur = (ex, ey)
    while cur in came_from:
        parent, letter = came_from[cur]
        path_chars.append(letter)
        cur = parent
    path_str = ''.join(reversed(path_chars))

    return grid, entry, exit_pos, path_str


def write_output_file(
    grid: list[list[int]],
    entry: tuple[int, int],
    exit: tuple[int, int],
    path: str,
    output_file: str
) -> None:
    """
    Write the maze output file in the required format.
    """
    try:
        with open(output_file, "w") as file:
            # Write maze grid (hex)
            for row in grid:
                hex_row = "".join(format(cell, "x") for cell in row)
                file.write(hex_row + "\n")

            file.write("\n")

            file.write(f"{entry[0]},{entry[1]}\n")
            file.write(f"{exit[0]},{exit[1]}\n")
            file.write(f"{path}\n")

    except OSError:
        error_exit(f"Cannot write to output file '{output_file}'.")


def main() -> None:
    """Run the maze generator and launch the interactive ASCII UI."""
    if len(sys.argv) != 2:
        error_exit("Usage: python3 a_maze_ing.py <config_file>")

    config_path = sys.argv[1]

    # Config parsing and validation
    raw_config = parse_config(config_path)
    config = validate_config(raw_config)

    output_file: str = str(config["output_file"])
    width: int = int(str(config["width"]))
    height: int = int(str(config["height"]))
    entry: tuple[int, int] = config["entry"]  # type: ignore[assignment]
    maze_exit: tuple[int, int] = config["exit"]  # type: ignore[assignment]

    # Optional seed from config (defaults to 42 if not provided)
    raw_seed = config.get("seed", "42")  # type: ignore[attr-defined]
    try:
        seed: int = int(str(raw_seed))
    except (ValueError, TypeError):
        seed = 42

    # Generate the maze using the recursive backtracker algorithm
    grid, entry, maze_exit, path = generate_maze(
        width=width,
        height=height,
        entry=entry,
        exit_pos=maze_exit,
        seed=seed,
    )

    # Write initial output file
    write_output_file(
        grid=grid,
        entry=entry,
        exit=maze_exit,
        path=path,
        output_file=output_file,
    )

    print("Output file generated successfully.")

    # Re-generate callback passed to the UI (option 1)
    # Each call uses a different seed so mazes vary on re-generate.
    _call_count = [0]

    def regenerate() -> tuple:  # type: ignore[type-arg]
        """Return a fresh maze with a new seed and write the output file."""
        _call_count[0] += 1
        new_grid, new_entry, new_exit, new_path = generate_maze(
            width=width,
            height=height,
            entry=entry,
            exit_pos=maze_exit,
            seed=seed + _call_count[0],
        )
        write_output_file(
            grid=new_grid,
            entry=new_entry,
            exit=new_exit,
            path=new_path,
            output_file=output_file,
        )
        return new_grid, new_entry, new_exit, new_path

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