"""
maze_generator.py – Reusable maze generation module.

Combines maze data structure, wall operations, DFS generator, cycle adder,
BFS solver, and '42' pattern embedding into a single importable MazeGenerator
class.

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
from forty_two import embed_42, get_42_cells


# ---------------------------------------------------------------------------
# Direction helpers
# ---------------------------------------------------------------------------


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
    def delta(self) -> tuple[int, int]:
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


# ---------------------------------------------------------------------------
# Maze data structure
# ---------------------------------------------------------------------------


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
        self, coord: tuple[int, int], name: str
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


# ---------------------------------------------------------------------------
# Wall operations
# ---------------------------------------------------------------------------


def _get_neighbours(
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


def _remove_wall(
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

    delta_map = {d.delta: d for d in Direction}
    direction = delta_map.get((dx, dy))
    if direction is None:
        raise ValueError(f"Cells {coord_a} and {coord_b} are not adjacent.")

    maze.grid[ay][ax] &= ~direction.value
    maze.grid[by][bx] &= ~direction.opposite.value


def _add_wall_back(
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


def _has_wall(
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


# ---------------------------------------------------------------------------
# 3x3 open-area detection
# ---------------------------------------------------------------------------


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
                if _has_wall(maze, (col, row), Direction.EAST):
                    return False
            if row < y + 2:
                if _has_wall(maze, (col, row), Direction.SOUTH):
                    return False
    return True


def _creates_3x3_nearby(maze: Maze, x: int, y: int) -> bool:
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


# ---------------------------------------------------------------------------
# Cycle addition for imperfect mazes
# ---------------------------------------------------------------------------


def _add_cycles_safely(
    maze: Maze,
    forbidden_cells: set[tuple[int, int]],
    attempts: int = 300,
) -> None:
    """Open extra walls to create loops while keeping the maze valid.

    Picks random cells and tries to open a wall to a neighbour. Rejects
    the opening if it would create a 3x3 open area. Skips forbidden cells
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

        neighbours = _get_neighbours(maze, (x, y))
        random.shuffle(neighbours)

        for (nx, ny), direction in neighbours:
            if (nx, ny) in forbidden_cells:
                continue

            if not _has_wall(maze, (x, y), direction):
                continue

            _remove_wall(maze, (x, y), (nx, ny))

            if _creates_3x3_nearby(maze, x, y):
                _add_wall_back(maze, (x, y), (nx, ny))

            break


# ---------------------------------------------------------------------------
# DFS maze generator
# ---------------------------------------------------------------------------


def _generate_dfs(
    maze: Maze,
    forbidden_cells: set[tuple[int, int]] | None = None,
) -> None:
    """Generate a perfect maze using iterative Depth-First Search (DFS).

    Starts from the entry cell and carves passages using a random DFS walk.
    Skips forbidden_cells so that '42' pattern cells are never carved
    through — stamping them later won't break any existing passages.

    Args:
        maze: The maze instance to carve in-place.
        forbidden_cells: Cells the DFS must never enter (e.g. '42' cells).
    """
    blocked: set[tuple[int, int]] = forbidden_cells or set()

    stack = [maze.entry]
    maze.visited.add(maze.entry)

    while stack:
        current = stack[-1]

        neighbours = _get_neighbours(maze, current)
        unvisited = [
            (coord, direction)
            for coord, direction in neighbours
            if coord not in maze.visited and coord not in blocked
        ]

        if unvisited:
            next_coord, direction = random.choice(unvisited)
            _remove_wall(maze, current, next_coord)
            maze.visited.add(next_coord)
            stack.append(next_coord)
        else:
            stack.pop()


# ---------------------------------------------------------------------------
# BFS solver
# ---------------------------------------------------------------------------


def _solve_bfs(
    maze: Maze,
    forbidden_cells: set[tuple[int, int]] | None = None,
) -> str:
    """Find the shortest path from entry to exit using BFS.

    Avoids forbidden_cells (the '42' pattern) so the solution path does
    not route through the decorative closed cells.

    Args:
        maze: A generated maze instance.
        forbidden_cells: Optional set of cells to skip during search.

    Returns:
        Path string using N/E/S/W characters (e.g. 'EESSNN').
        Returns an empty string if no path exists.
    """
    blocked: set[tuple[int, int]] = forbidden_cells or set()

    queue: deque[tuple[tuple[int, int], list[str]]] = deque()
    queue.append((maze.entry, []))
    visited: set[tuple[int, int]] = {maze.entry}

    while queue:
        current, path = queue.popleft()

        if current == maze.exit:
            return "".join(path)

        for neighbour, direction in _get_neighbours(maze, current):
            if neighbour in visited:
                continue
            if _has_wall(maze, current, direction):
                continue
            if neighbour in blocked:
                continue
            visited.add(neighbour)
            queue.append((neighbour, path + [direction.letter]))

    return ""


# ---------------------------------------------------------------------------
# Public MazeGenerator class
# ---------------------------------------------------------------------------


class MazeGenerator:
    """Generate and solve a rectangular maze with an embedded '42' pattern.

    Args:
        width: Number of columns.
        height: Number of rows.
        entry: (x, y) entry cell.
        exit_pos: (x, y) exit cell.
        seed: Optional random seed for reproducibility.
        perfect: If True (default) the maze has exactly one path between
                 any two cells (DFS spanning tree, no extra loops).
                 If False, extra loops are added safely (no 3x3 open areas).

    Example::

        gen = MazeGenerator(width=20, height=15,
                            entry=(0, 0), exit=(19, 14), seed=42)
        gen.generate()
        print(gen.grid)            # raw bitmask grid
        print(gen.solve())         # e.g. 'EESSWWSS...'
        print(gen.forbidden_cells) # cells belonging to the '42' pattern
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit_pos: tuple[int, int],
        seed: int | None = None,
        perfect: bool = True,
    ) -> None:
        self.width = width
        self.height = height
        self.entry = entry
        self.exit_pos = exit_pos
        self.seed = seed
        self.perfect = perfect
        self._maze: Maze | None = None
        self._forbidden: set[tuple[int, int]] = set()

    def generate(self) -> None:
        """Generate the maze in-place.

        Steps:
          1. Build the Maze data structure (all walls present).
          2. Pre-compute the '42' pattern cell positions (forbidden set).
          3. Run DFS to carve a perfect spanning tree.
          4. If perfect=False, add safe cycles avoiding forbidden cells
             and keeping corridors at most 2 cells wide (no 3x3 open areas).
          5. Stamp the '42' pattern last (overrides any DFS carvings).

        After calling this method the ``grid`` and ``forbidden_cells``
        properties are available.
        """
        self._maze = Maze(
            width=self.width,
            height=self.height,
            entry=self.entry,
            exit_pos=self.exit_pos,
            seed=self.seed,
        )

        # Pre-compute forbidden positions so cycle-adder can avoid them.
        # Actual stamping happens AFTER DFS (step 5).
        self._forbidden = get_42_cells(self.width, self.height)

        # Step 3: Carve the spanning tree (avoiding 42 cells so stamping
        # them later never destroys any carved passages)
        _generate_dfs(self._maze, self._forbidden)

        # Step 4: Add loops for imperfect mazes (skips forbidden cells)
        if not self.perfect:
            _add_cycles_safely(self._maze, self._forbidden)

        # Step 5: Stamp '42' pattern – overwrites whatever DFS carved there
        self._forbidden = embed_42(self._maze.grid, self.width, self.height)

    @property
    def grid(self) -> list[list[int]]:
        """The generated maze grid (list of rows, each a list of bitmasks).

        Raises:
            RuntimeError: If generate() has not been called yet.
        """
        if self._maze is None:
            raise RuntimeError("Call generate() before accessing the grid.")
        return self._maze.grid

    @property
    def forbidden_cells(self) -> set[tuple[int, int]]:
        """Set of (x, y) cells occupied by the '42' pattern.

        These cells have all 4 walls closed (value 0xF).
        The BFS solver avoids them automatically.

        Raises:
            RuntimeError: If generate() has not been called yet.
        """
        if self._maze is None:
            raise RuntimeError(
                "Call generate() before accessing forbidden_cells."
            )
        return self._forbidden

    def solve(self) -> str:
        """Return the shortest path from entry to exit as a direction string.

        The path routes around the '42' pattern cells.

        Returns:
            String of N/E/S/W characters.

        Raises:
            RuntimeError: If generate() has not been called yet.
        """
        if self._maze is None:
            raise RuntimeError("Call generate() before calling solve().")
        return _solve_bfs(self._maze, self._forbidden)
