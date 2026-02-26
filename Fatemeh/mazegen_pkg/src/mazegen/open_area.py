"""open_area.py – 3x3 open-area guard and imperfect-maze cycle adder.

Ensures no corridor becomes wider than 2 cells (i.e. no fully open 3x3
block is ever created) when adding extra loops to an imperfect maze.
"""

from __future__ import annotations

import random

from .direction import Direction
from .maze_core import Maze
from .wall_ops import add_wall_back, get_neighbours, has_wall, remove_wall


def _has_3x3_open(maze: Maze, x: int, y: int) -> bool:
    """Check if a 3x3 block starting at (x, y) is fully open (no walls).

    Args:
        maze: The maze instance.
        x: Top-left x coordinate of the block.
        y: Top-left y coordinate of the block.

    Returns:
        True if the entire 3x3 area has no internal walls.
    """
    for row in range(y, y + 3):
        for col in range(x, x + 3):
            if col < x + 2:
                if has_wall(maze, (col, row), Direction.EAST):
                    return False
            if row < y + 2:
                if has_wall(maze, (col, row), Direction.SOUTH):
                    return False
    return True


def creates_3x3_nearby(maze: Maze, x: int, y: int) -> bool:
    """Check whether any 3x3 block near (x, y) is fully open.

    Called after opening a wall to decide whether to keep the change.

    Args:
        maze: The maze instance.
        x: x coordinate of the recently changed cell.
        y: y coordinate of the recently changed cell.

    Returns:
        True if a 3x3 open area exists in the vicinity.
    """
    for dy in range(-2, 1):
        for dx in range(-2, 1):
            check_x = x + dx
            check_y = y + dy
            if (
                0 <= check_x <= maze.width - 3
                and 0 <= check_y <= maze.height - 3
            ):
                if _has_3x3_open(maze, check_x, check_y):
                    return True
    return False


def add_cycles_safely(
    maze: Maze,
    forbidden_cells: set[tuple[int, int]],
    attempts: int = 300,
) -> None:
    """Open extra walls to create loops while keeping the maze valid.

    Picks random cells and tries to open a wall to a neighbour.  Rejects
    the opening if it would create a 3x3 open area.  Skips forbidden cells
    to protect the '42' pattern.

    Args:
        maze: The maze instance (modified in-place).
        forbidden_cells: Cells to never touch (e.g. the '42' pattern cells).
        attempts: Number of random attempts to make.
    """
    for _ in range(attempts):
        x = random.randint(0, maze.width - 1)
        y = random.randint(0, maze.height - 1)

        if (x, y) in forbidden_cells:
            continue

        neighbours = get_neighbours(maze, (x, y))
        random.shuffle(neighbours)

        for (nx, ny), direction in neighbours:
            if (nx, ny) in forbidden_cells:
                continue
            if not has_wall(maze, (x, y), direction):
                continue

            remove_wall(maze, (x, y), (nx, ny))

            if creates_3x3_nearby(maze, x, y):
                add_wall_back(maze, (x, y), (nx, ny))

            break
