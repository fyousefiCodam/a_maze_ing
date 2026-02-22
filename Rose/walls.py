"""
Wall operations for the Maze.

Directions are stored as bitmasks on each cell:
    N=1, E=2, S=4, W=8

A bit being SET means that wall is PRESENT.
Removing a wall clears the bit on both neighbouring cells.
"""
from enum import Enum
from maze_definition import Maze


class Direction(Enum):
    """
    Cardinal directions as bitmasks.

    Each direction knows:
      - its bitmask (the wall it represents on a cell)
      - its opposite (the wall on the neighbouring cell)
      - its (dx, dy) delta in grid coordinates
        grid[y][x]: North decrements y, South increments y.
    """
    NORTH = 1
    EAST = 2
    SOUTH = 4
    WEST = 8

    @property
    def opposite(self) -> "Direction":
        opposites = {
            Direction.NORTH: Direction.SOUTH,
            Direction.SOUTH: Direction.NORTH,
            Direction.EAST: Direction.WEST,
            Direction.WEST: Direction.EAST
        }
        return opposites[self]

    @property
    def delta(self) -> tuple[int, int]:
        """Return (dx, dy) for one step in this direction."""
        deltas = {
            Direction.NORTH: (0, -1),
            Direction.EAST: (1, 0),
            Direction.SOUTH: (0, 1),
            Direction.WEST: (-1, 0)
        }
        return deltas[self]


def get_neighbours(
        maze: Maze,
        coord: tuple[int, int]
) -> list[tuple[tuple[int, int], Direction]]:
    """
    Return all in-bounds neighbours of coord.

    Each entry is ((nx, ny), direction) where direction is the direction
    you travel FROM coord TO reach that neighbour.
    """
    x, y = coord
    neighbours = []

    for direction in Direction:
        dx, dy = direction.delta
        neighbour = (x + dx, y + dy)
        if maze.is_in_bounds(neighbour):
            neighbours.append((neighbour, direction))

    return neighbours


def remove_wall(
        maze: Maze,
        coord_a: tuple[int, int],
        coord_b: tuple[int, int]
) -> None:
    """
    Remove the wall between two adjacent cells.

    coord_a and coord_b must be direct neighbours (one step apart).
    Raises ValueError if they are not adjacent.
    Updates both cells so the wall is removed on both sides.
    """
    ax, ay = coord_a
    bx, by = coord_b
    dx = bx - ax
    dy = by - ay

    # figure out the diection from the delta
    delta_to_direction = {}
    for d in Direction:
        delta_to_direction[d.delta] = d

    direction = delta_to_direction.get((dx, dy))
    if Direction is None:
        raise ValueError(
            f"cells {coord_a} and {coord_b} are not adjacent"
        )

    # clear the wall bit on coord_a
    maze.grid[ay][ax] &= ~direction.value

    # clear the opposite wall bit on coord_b
    maze.grid[by][bx] &= ~direction.opposite.value


def has_wall(
    maze: Maze,
    coord: tuple[int, int],
    direction: Direction
) -> bool:
    """
    Return True if the given wall is present on this cell, False otherwise.
    """

    x, y = coord
    return bool(maze.grid[y][x] & direction.value)
