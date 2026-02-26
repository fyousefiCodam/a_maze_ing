"""maze_core.py – Maze data structure.

Holds the rectangular grid, dimensions, entry/exit coordinates,
and the set of visited cells used during generation.
"""

from __future__ import annotations

import random


class Maze:
    """Rectangular grid maze.

    Each cell stores a 4-bit bitmask (N=1, E=2, S=4, W=8).
    A bit being SET means that wall is PRESENT.
    All cells start fully walled (value 15 = 0b1111).

    Args:
        width: Number of columns (must be > 0).
        height: Number of rows (must be > 0).
        entry: (x, y) of the entry cell.
        exit_pos: (x, y) of the exit cell.
        seed: Random seed for reproducibility.
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit_pos: tuple[int, int],
        seed: int | None = None,
    ) -> None:
        if width <= 0:
            raise ValueError("Width must be a positive integer.")
        if height <= 0:
            raise ValueError("Height must be a positive integer.")

        self.width = width
        self.height = height

        # Use `is not None` so that seed=0 is treated as a valid seed.
        if seed is not None:
            random.seed(seed)

        self.entry = self._validate_coord(entry, "entry")
        self.exit = self._validate_coord(exit_pos, "exit")

        if self.entry == self.exit:
            raise ValueError("Entry and exit points cannot be the same.")

        # All walls present at start (bitmask 1111 = 15)
        self.grid: list[list[int]] = [[15] * width for _ in range(height)]
        self.visited: set[tuple[int, int]] = set()

    def _validate_coord(
        self,
        coord: tuple[int, int],
        name: str,
    ) -> tuple[int, int]:
        """Validate that a coordinate is inside the maze bounds.

        Args:
            coord: (x, y) coordinate to validate.
            name: Human-readable name for error messages (e.g. 'entry').

        Returns:
            The validated (x, y) tuple.

        Raises:
            ValueError: If the coordinate is out of bounds.
        """
        x, y = coord
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise ValueError(
                f"{name} coordinate {coord} is outside maze bounds "
                f"({self.width}x{self.height})."
            )
        return coord

    def is_in_bounds(self, coord: tuple[int, int]) -> bool:
        """Return True if coord is a valid cell within the maze.

        Args:
            coord: (x, y) coordinate to check.

        Returns:
            True if inside bounds, False otherwise.
        """
        x, y = coord
        return 0 <= x < self.width and 0 <= y < self.height
