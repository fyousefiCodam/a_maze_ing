"""maze_generator.py – Public MazeGenerator class.

Combines maze construction, DFS carving, optional cycle addition,
'42' pattern embedding, and BFS solving into a single easy-to-use
class.

Usage example::

    from maze_generator import MazeGenerator

    gen = MazeGenerator(width=20, height=15, entry=(0, 0),
                        exit_pos=(19, 14), seed=42, perfect=True)
    gen.generate()
    grid = gen.grid           # list[list[int]], hex bitmask per cell
    path = gen.solve()        # e.g. "EESSSWW..."
    print(gen.width, gen.height)
"""

from __future__ import annotations

from bfs_solver import solve_bfs
from dfs_generator import generate_dfs
from forty_two import embed_42, get_42_cells
from maze_core import Maze
from open_area import add_cycles_safely


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
                            entry=(0, 0), exit_pos=(19, 14), seed=42)
        gen.generate()
        print(gen.grid)             # raw bitmask grid
        print(gen.solve())          # e.g. 'EESSWWSS...'
        print(gen.forbidden_cells)  # cells belonging to the '42' pattern
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

        # Pre-compute forbidden positions so the cycle-adder can skip them.
        # Actual stamping happens AFTER DFS (step 5).
        self._forbidden = get_42_cells(self.width, self.height)

        # Step 3: Carve the spanning tree (avoiding 42 cells so stamping
        # them later never destroys any carved passages).
        generate_dfs(self._maze, self._forbidden)

        # Step 4: Add loops for imperfect mazes (skips forbidden cells).
        if not self.perfect:
            add_cycles_safely(self._maze, self._forbidden)

        # Step 5: Stamp '42' pattern – overwrites whatever DFS carved there.
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
        return solve_bfs(self._maze, self._forbidden)
