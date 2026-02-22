"""This file contains the main maze class and the error handling of the
maze inputs, it contains the maze data structure and other validations"""
import random

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


class Maze:
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

