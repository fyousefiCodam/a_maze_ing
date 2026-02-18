import random
"""This file contains the main maze class and the error handling of the
maze inputs, it contains the maze data structure and other validations"""


from enum import Enum
from typing import Set, Tuple


class Ansi(str, Enum):
    """ansi codes to make the output readable"""

    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    BG_CYAN = "\033[46m"

    def __str__(self) -> str:
        return self.value


class maze:
    """ This is for creating a rectangular maze
    and each cell in the maze has walls on all the four
    sides and they are defined in accordance to their
    bit position when a particlar wall is removed from
    (North, East, West, South)"""
    def __init__(self, height: int,
                 width: int,
                 entry: tuple[int, int],
                 exit: tuple[int, int],
                 seed: int) -> None:
        # validate that the width is a positive number it cannot be
        # 0 or negative
        if width <= 0:
            raise ValueError("Width must be a positive integer.")
        if height <= 0:
            raise ValueError("Height must be a positive integer.")

        self.width = width
        self.height = height

        # Use `is not None` so that seed=0 is treated as a valid seed.
        if seed is not None:
            random.seed(seed)

        self.entry = self.coordinate_validation(entry, name="entry")
        self.exit = self.coordinate_validation(exit, name="exit")

        if self.entry == self.exit:
            raise ValueError("Entry and exit points cannot be the same.")

        # Each cell is initialized to 15 (bitmask 1111), meaning all four
        # walls are present.
        self.grid: list[list[int]] = [[15] * width for _ in range(height)]
        self.visited: Set[Tuple[int, int]] = set()

    def is_in_bounds(self, coord: tuple[int, int]) -> bool:
        """Return True if coord lies within the maze grid, False otherwise."""
        x, y = coord
        # `and` is correct here: both axes must be in range simultaneously.
        return 0 <= x < self.width and 0 <= y < self.height

    def coordinate_validation(self,
                              coord: tuple[int, int],
                              name: str = "coordinate") -> tuple[int, int]:
        """
        Validate that a coordinate lies within the maze bounds.

        Raises ValueError if out of bounds.
        Returns the coordinate unchanged on success.
        """
        if not self.is_in_bounds(coord):
            raise ValueError(
                f"'{name}' coordinate {coord} is out of maze bounds "
                f"(width={self.width}, height={self.height})."
            )
        return coord


def entry(self, entry: tuple[int, int]) -> tuple[int, int]:
    # validates and returns the entry coordinates
    return self.valid_coordinates(entry, name="entry")


def exit(self, exit: tuple[int, int]) -> tuple[int, int]:
    # validates and returns the exit coordinates
    return self.valid_coordinates(exit, name="exit")
