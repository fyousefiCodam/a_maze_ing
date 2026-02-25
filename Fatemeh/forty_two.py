"""
forty_two.py – Embeds the "42" pattern into a generated maze.

The pattern is drawn using fully-closed cells (all 4 walls present).
It must be stamped AFTER maze generation so DFS carvings are overwritten.

The set of stamped cell coordinates (forbidden_cells) is returned so that
the BFS solver and cycle-adder can avoid routing through those cells.
"""

from __future__ import annotations

# Pixel-art bitmap for "42"
# 1 = solid cell (all 4 walls closed), 0 = leave as generated
PATTERN_42: list[list[int]] = [
    [1, 0, 1, 0, 0, 1, 1, 1],
    [1, 0, 1, 0, 0, 0, 0, 1],
    [1, 1, 1, 0, 0, 1, 1, 1],
    [0, 0, 1, 0, 0, 1, 1, 0],
    [0, 0, 1, 0, 0, 1, 1, 1],
]

PATTERN_H: int = len(PATTERN_42)    # 5 rows
PATTERN_W: int = len(PATTERN_42[0])  # 8 cols

# Minimum maze dimensions required to fit the pattern with a 1-cell border
MIN_WIDTH: int = PATTERN_W + 2
MIN_HEIGHT: int = PATTERN_H + 2


def can_fit_42(width: int, height: int) -> bool:
    """Return True if the maze is large enough to hold the '42' pattern.

    Args:
        width: Maze width in cells.
        height: Maze height in cells.

    Returns:
        True if the pattern fits with at least a 1-cell border on each side.
    """
    return width >= MIN_WIDTH and height >= MIN_HEIGHT


def get_42_cells(width: int, height: int) -> set[tuple[int, int]]:
    """Return the set of cell coordinates that the '42' pattern occupies.

    This can be called BEFORE generation to obtain the forbidden set that
    the DFS cycle-adder and BFS solver should avoid.

    Args:
        width: Maze width in cells.
        height: Maze height in cells.

    Returns:
        Set of (x, y) coordinates, or empty set if the maze is too small.
    """
    if not can_fit_42(width, height):
        return set()

    origin_x: int = (width - PATTERN_W) // 2
    origin_y: int = (height - PATTERN_H) // 2

    cells: set[tuple[int, int]] = set()
    for row in range(PATTERN_H):
        for col in range(PATTERN_W):
            if PATTERN_42[row][col]:
                cells.add((origin_x + col, origin_y + row))
    return cells


def embed_42(
    grid: list[list[int]],
    width: int,
    height: int,
) -> set[tuple[int, int]]:
    """Stamp the '42' pattern into the maze grid.

    Sets all 4 walls (value 0xF) on every cell that belongs to the pattern.
    Should be called AFTER maze generation so it overrides any carved paths.

    Args:
        grid: 2-D list of cell bitmasks (modified in-place).
        width: Maze width in cells.
        height: Maze height in cells.

    Returns:
        Set of stamped (x, y) coordinates (the forbidden_cells set).
        Returns an empty set and prints an error if the maze is too small.
    """
    if not can_fit_42(width, height):
        print(
            "Warning: maze is too small to display the '42' pattern "
            f"(need at least {MIN_WIDTH}x{MIN_HEIGHT}, "
            f"got {width}x{height})."
        )
        return set()

    origin_x: int = (width - PATTERN_W) // 2
    origin_y: int = (height - PATTERN_H) // 2

    stamped: set[tuple[int, int]] = set()
    for row in range(PATTERN_H):
        for col in range(PATTERN_W):
            if PATTERN_42[row][col]:
                x = origin_x + col
                y = origin_y + row
                grid[y][x] = 0xF   # North | East | South | West all closed
                stamped.add((x, y))

    return stamped
