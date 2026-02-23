"""Output file validator – checks that a maze output file is coherent.

Run as::

    python3 output_validator.py maze.txt
"""

import sys


def validate(path: str) -> None:
    """Validate the maze output file format and wall coherence.

    Args:
        path: Path to the maze output file.
    """
    try:
        with open(path, "r") as f:
            content = f.read()
    except OSError as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    parts = content.strip().split("\n\n")
    if len(parts) != 2:
        print("Error: File must have a maze grid and a metadata block separated by a blank line.")
        sys.exit(1)

    grid_lines = parts[0].splitlines()
    meta_lines = parts[1].splitlines()

    if len(meta_lines) < 3:
        print("Error: Metadata block must have entry, exit, and path lines.")
        sys.exit(1)

    # Parse grid
    height = len(grid_lines)
    width = len(grid_lines[0]) if height > 0 else 0
    grid: list[list[int]] = []

    for row_idx, line in enumerate(grid_lines):
        if len(line) != width:
            print(f"Error: Row {row_idx} has wrong length.")
            sys.exit(1)
        try:
            row = [int(c, 16) for c in line]
        except ValueError:
            print(f"Error: Invalid hex character in row {row_idx}.")
            sys.exit(1)
        grid.append(row)

    # Check wall coherence (N=1, E=2, S=4, W=8)
    errors = 0
    for y in range(height):
        for x in range(width):
            cell = grid[y][x]
            # East wall of (x,y) must match West wall of (x+1,y)
            if x + 1 < width:
                east = bool(cell & 2)
                west_neighbour = bool(grid[y][x + 1] & 8)
                if east != west_neighbour:
                    print(f"  Incoherent E/W wall at ({x},{y})<->({x+1},{y})")
                    errors += 1
            # South wall of (x,y) must match North wall of (x,y+1)
            if y + 1 < height:
                south = bool(cell & 4)
                north_neighbour = bool(grid[y + 1][x] & 1)
                if south != north_neighbour:
                    print(f"  Incoherent S/N wall at ({x},{y})<->({x},{y+1})")
                    errors += 1

    if errors:
        print(f"Validation FAILED: {errors} wall coherence error(s).")
        sys.exit(1)

    print(f"Validation PASSED: {width}x{height} maze, walls are coherent.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 output_validator.py <maze_file>")
        sys.exit(1)
    validate(sys.argv[1])
