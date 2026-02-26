"""wall_ops.py – Low-level wall operations on a Maze grid.

Provides helpers to query neighbours, remove/restore walls, and test
whether a specific wall is present.  All functions operate on a Maze
instance and leave the grid in a consistent (mirrored) state.
"""

from __future__ import annotations

from direction import Direction
from maze_core import Maze


def get_neighbours(
    maze: Maze,
    coord: tuple[int, int],
) -> list[tuple[tuple[int, int], Direction]]:
    """Return all in-bounds neighbours of a cell.

    Args:
        maze: The maze instance.
        coord: (x, y) of the cell.

    Returns:
        List of ((nx, ny), direction) tuples.
    """
    x, y = coord
    neighbours: list[tuple[tuple[int, int], Direction]] = []
    for direction in Direction:
        dx, dy = direction.delta
        neighbour: tuple[int, int] = (x + dx, y + dy)
        if maze.is_in_bounds(neighbour):
            neighbours.append((neighbour, direction))
    return neighbours


def remove_wall(
    maze: Maze,
    coord_a: tuple[int, int],
    coord_b: tuple[int, int],
) -> None:
    """Remove the wall between two adjacent cells (updates both sides).

    Args:
        maze: The maze instance.
        coord_a: First cell (x, y).
        coord_b: Second cell (x, y), must be directly adjacent to coord_a.

    Raises:
        ValueError: If the cells are not adjacent.
    """
    ax, ay = coord_a
    bx, by = coord_b
    dx, dy = bx - ax, by - ay

    delta_map: dict[tuple[int, int], Direction] = {
        d.delta: d for d in Direction
    }
    direction = delta_map.get((dx, dy))
    if direction is None:
        raise ValueError(f"Cells {coord_a} and {coord_b} are not adjacent.")

    maze.grid[ay][ax] &= ~direction.value
    maze.grid[by][bx] &= ~direction.opposite.value


def add_wall_back(
    maze: Maze,
    coord_a: tuple[int, int],
    coord_b: tuple[int, int],
) -> None:
    """Restore a wall between two adjacent cells (undo a removal).

    Args:
        maze: The maze instance.
        coord_a: First cell (x, y).
        coord_b: Second cell (x, y), must be directly adjacent to coord_a.

    Raises:
        ValueError: If the cells are not adjacent.
    """
    ax, ay = coord_a
    bx, by = coord_b
    dx, dy = bx - ax, by - ay

    for direction in Direction:
        if direction.delta == (dx, dy):
            maze.grid[ay][ax] |= direction.value
            maze.grid[by][bx] |= direction.opposite.value
            return

    raise ValueError(f"Cells {coord_a} and {coord_b} are not adjacent.")


def has_wall(
    maze: Maze,
    coord: tuple[int, int],
    direction: Direction,
) -> bool:
    """Return True if the given wall is present on the cell.

    Args:
        maze: The maze instance.
        coord: (x, y) of the cell.
        direction: The wall direction to check.

    Returns:
        True if the wall exists, False if open.
    """
    x, y = coord
    return bool(maze.grid[y][x] & direction.value)
