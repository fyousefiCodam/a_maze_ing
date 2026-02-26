"""dfs_generator.py – Iterative Depth-First Search maze carver.

Carves a perfect spanning-tree maze from the entry cell outwards,
optionally skipping a set of forbidden cells so that a decorative
pattern can be stamped over the grid afterwards without corruption.
"""

from __future__ import annotations

import random

from .maze_core import Maze
from .wall_ops import get_neighbours, remove_wall


def generate_dfs(
    maze: Maze,
    forbidden_cells: set[tuple[int, int]] | None = None,
) -> None:
    """Generate a perfect maze using iterative Depth-First Search (DFS).

    Starts from the entry cell and carves passages using a random DFS walk.
    Skips ``forbidden_cells`` so that '42' pattern cells are never carved
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

        neighbours = get_neighbours(maze, current)
        unvisited = [
            (coord, direction)
            for coord, direction in neighbours
            if coord not in maze.visited and coord not in blocked
        ]

        if unvisited:
            next_coord, direction = random.choice(unvisited)
            remove_wall(maze, current, next_coord)
            maze.visited.add(next_coord)
            stack.append(next_coord)
        else:
            stack.pop()
