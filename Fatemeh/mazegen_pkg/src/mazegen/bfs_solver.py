"""bfs_solver.py – BFS shortest-path solver for a generated maze.

Finds the shortest path from entry to exit, routing around any
forbidden cells (e.g. the decorative '42' pattern).
"""

from __future__ import annotations

from collections import deque

from .maze_core import Maze
from .wall_ops import get_neighbours, has_wall


def solve_bfs(
    maze: Maze,
    forbidden_cells: set[tuple[int, int]] | None = None,
) -> str:
    """Find the shortest path from entry to exit using BFS.

    Avoids ``forbidden_cells`` (the '42' pattern) so the solution path
    does not route through the decorative closed cells.

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
        current, path = queue.popleft()  # BFS: take from front

        if current == maze.exit:
            return "".join(path)

        for neighbour, direction in get_neighbours(maze, current):
            if neighbour in visited:
                continue
            if has_wall(maze, current, direction):
                continue
            if neighbour in blocked:
                continue
            visited.add(neighbour)
            queue.append((neighbour, path + [direction.letter]))

    return ""
