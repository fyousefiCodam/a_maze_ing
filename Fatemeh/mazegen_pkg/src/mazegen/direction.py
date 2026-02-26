"""direction.py – Cardinal direction enum with bitmask, delta, and letter.

Used by the maze data structure and all algorithms that traverse the grid.
"""

from __future__ import annotations

from enum import Enum


class Direction(Enum):
    """Cardinal directions stored as wall bitmasks (N=1, E=2, S=4, W=8)."""

    NORTH = 1
    EAST = 2
    SOUTH = 4
    WEST = 8

    @property
    def opposite(self) -> "Direction":
        """Return the direction opposite to this one."""
        opposites: dict["Direction", "Direction"] = {
            Direction.NORTH: Direction.SOUTH,
            Direction.SOUTH: Direction.NORTH,
            Direction.EAST: Direction.WEST,
            Direction.WEST: Direction.EAST,
        }
        return opposites[self]

    @property
    def delta(self) -> tuple[int, int]:
        """Return (dx, dy) for one step in this direction."""
        deltas: dict["Direction", tuple[int, int]] = {
            Direction.NORTH: (0, -1),
            Direction.EAST: (1, 0),
            Direction.SOUTH: (0, 1),
            Direction.WEST: (-1, 0),
        }
        return deltas[self]

    @property
    def letter(self) -> str:
        """Return the single-letter code used in path strings."""
        return self.name[0]  # 'N', 'E', 'S', 'W'
