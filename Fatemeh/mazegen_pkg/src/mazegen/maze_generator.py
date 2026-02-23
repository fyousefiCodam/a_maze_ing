"""
maze_generator.py – Reusable maze generation module.

Combines maze data structure, wall operations, DFS generator, and BFS solver
into a single importable MazeGenerator class.

Usage example::

    from maze_generator import MazeGenerator

    gen = MazeGenerator(width=20, height=15, entry=(0, 0), exit=(19, 14),
                        seed=42, perfect=True)
    gen.generate()
    grid   = gen.grid          # list[list[int]], hex bitmask per cell
    path   = gen.solve()       # e.g. "EESSSWW..."
    print(gen.width, gen.height)
"""

import random
from collections import deque
from enum import Enum
from typing import Optional, Set, Tuple


# Direction helpers
class Direction(Enum):
    """Cardinal directions stored as wall bitmasks (N=1, E=2, S=4, W=8)."""

    NORTH = 1
    EAST = 2
    SOUTH = 4
    WEST = 8

    @property
    def opposite(self) -> "Direction":
        """Return the direction opposite to this one."""
        opposites = {
            Direction.NORTH: Direction.SOUTH,
            Direction.SOUTH: Direction.NORTH,
            Direction.EAST: Direction.WEST,
            Direction.WEST: Direction.EAST,
        }
        return opposites[self]

    @property
    def delta(self) -> Tuple[int, int]:
        """Return (dx, dy) for one step in this direction."""
        deltas = {
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


# Maze data structure
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
        entry: Tuple[int, int],
        exit_pos: Tuple[int, int],
        seed: Optional[int] = None,
    ) -> None:
        if width <= 0:
            raise ValueError("Width must be a positive integer.")
        if height <= 0:
            raise ValueError("Height must be a positive integer.")

        self.width = width
        self.height = height

        if seed is not None:
            random.seed(seed)

        self.entry = self._validate_coord(entry, "entry")
        self.exit = self._validate_coord(exit_pos, "exit")

        if self.entry == self.exit:
            raise ValueError("Entry and exit points cannot be the same.")

        # All walls present at start (bitmask 1111 = 15)
        self.grid: list[list[int]] = [[15] * width for _ in range(height)]
        self.visited: Set[Tuple[int, int]] = set()

    def _validate_coord(
        self, coord: Tuple[int, int], name: str
    ) -> Tuple[int, int]:
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

    def is_in_bounds(self, coord: Tuple[int, int]) -> bool:
        """Return True if coord is a valid cell within the maze.

        Args:
            coord: (x, y) coordinate to check.

        Returns:
            True if inside bounds, False otherwise.
        """
        x, y = coord
        return 0 <= x < self.width and 0 <= y < self.height


# Wall operations
def _get_neighbours(
    maze: Maze,
    coord: Tuple[int, int],
) -> list[tuple[Tuple[int, int], Direction]]:
    """Return all in-bounds neighbours of a cell.

    Args:
        maze: The maze instance.
        coord: (x, y) of the cell.

    Returns:
        List of ((nx, ny), direction) tuples.
    """
    x, y = coord
    neighbours = []
    for direction in Direction:
        dx, dy = direction.delta
        neighbour: Tuple[int, int] = (x + dx, y + dy)
        if maze.is_in_bounds(neighbour):
            neighbours.append((neighbour, direction))
    return neighbours


def _remove_wall(
    maze: Maze,
    coord_a: Tuple[int, int],
    coord_b: Tuple[int, int],
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

    delta_map = {d.delta: d for d in Direction}
    direction = delta_map.get((dx, dy))
    if direction is None:
        raise ValueError(f"Cells {coord_a} and {coord_b} are not adjacent.")

    maze.grid[ay][ax] &= ~direction.value
    maze.grid[by][bx] &= ~direction.opposite.value


def _has_wall(
    maze: Maze,
    coord: Tuple[int, int],
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


# DFS maze generator  (Rose's algorithm)
def _generate_dfs(maze: Maze) -> None:
    """Generate a perfect maze using iterative Depth-First Search (DFS).

    Starts from the entry cell and carves passages using a random DFS walk.
    Every cell is visited exactly once, so the result is always a perfect
    maze (exactly one path between any two cells).

    Args:
        maze: The maze instance to carve in-place.
    """
    stack = [maze.entry]
    maze.visited.add(maze.entry)

    while stack:
        current = stack[-1]

        neighbours = _get_neighbours(maze, current)
        unvisited = [
            (coord, direction)
            for coord, direction in neighbours
            if coord not in maze.visited
        ]

        if unvisited:
            next_coord, direction = random.choice(unvisited)
            _remove_wall(maze, current, next_coord)
            maze.visited.add(next_coord)
            stack.append(next_coord)
        else:
            stack.pop()


# BFS solver  (Rose's algorithm)
def _solve_bfs(maze: Maze) -> str:
    """Find the shortest path from entry to exit using BFS.

    Args:
        maze: A generated maze instance.

    Returns:
        Path string using N/E/S/W characters (e.g. 'EESSNN').
        Returns an empty string if no path exists.
    """
    queue: deque[tuple[Tuple[int, int], list[str]]] = deque()
    queue.append((maze.entry, []))
    visited: Set[Tuple[int, int]] = {maze.entry}

    while queue:
        current, path = queue.popleft()

        if current == maze.exit:
            return "".join(path)

        for neighbour, direction in _get_neighbours(maze, current):
            if neighbour not in visited and not _has_wall(maze, current, direction):
                visited.add(neighbour)
                queue.append((neighbour, path + [direction.letter]))

    return ""


# Public MazeGenerator class
class MazeGenerator:
    """Generate and solve a rectangular maze.

    Args:
        width: Number of columns.
        height: Number of rows.
        entry: (x, y) entry cell.
        exit_pos: (x, y) exit cell.
        seed: Optional random seed for reproducibility.
        perfect: If True (default) the DFS algorithm guarantees a perfect
                 maze (exactly one path between any two cells).

    Example::

        gen = MazeGenerator(width=10, height=10,
                            entry=(0, 0), exit=(9, 9), seed=42)
        gen.generate()
        print(gen.grid)      # raw bitmask grid
        print(gen.solve())   # e.g. 'EESSWWSS...'
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry: Tuple[int, int],
        exit_pos: Tuple[int, int],
        seed: Optional[int] = None,
        perfect: bool = True,
    ) -> None:
        self.width = width
        self.height = height
        self.entry = entry
        self.exit_pos = exit_pos
        self.seed = seed
        self.perfect = perfect
        self._maze: Optional[Maze] = None

    def generate(self) -> None:
        """Generate the maze in-place.

        After calling this method, the ``grid`` property is available.
        """
        self._maze = Maze(
            width=self.width,
            height=self.height,
            entry=self.entry,
            exit_pos=self.exit_pos,
            seed=self.seed,
        )
        _generate_dfs(self._maze)

    @property
    def grid(self) -> list[list[int]]:
        """The generated maze grid (list of rows, each a list of bitmasks).

        Raises:
            RuntimeError: If generate() has not been called yet.
        """
        if self._maze is None:
            raise RuntimeError("Call generate() before accessing the grid.")
        return self._maze.grid

    def solve(self) -> str:
        """Return the shortest path from entry to exit as a direction string.

        Returns:
            String of N/E/S/W characters.

        Raises:
            RuntimeError: If generate() has not been called yet.
        """
        if self._maze is None:
            raise RuntimeError("Call generate() before calling solve().")
        return _solve_bfs(self._maze)
