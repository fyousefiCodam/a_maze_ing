from collections import deque
from maze_definition import Maze
from walls import get_neighbours, has_wall


def solve_bfs(
    maze: Maze,
    forbidden_cells: set[tuple[int, int]]
) -> list[tuple[int, int]]:
    """
    Find the shortest path from maze entry to exit using BFS.

    Args:
        maze: The maze to solve.
        forbidden_cells: Cells to avoid (e.g. the '42' pattern).

    Returns:
        List of (x, y) coordinates from entry to exit.

    Raises:
        ValueError: If no path exists from entry to exit.
    """
    queue: deque[tuple[int, int]] = deque()
    queue.append(maze.entry)

    visited: set[tuple[int, int]] = {maze.entry}

    # same idea as maze.visited in your DFS — track where we came from
    came_from: dict[tuple[int, int], tuple[int, int] | None] = {}
    came_from[maze.entry] = None

    while queue:
        current = queue.popleft()  # take from front (BFS, not DFS)

        if current == maze.exit:
            break

        # same neighbour loop as your DFS
        neighbours = get_neighbours(maze, current)
        for coord, direction in neighbours:
            if coord in visited:
                continue
            if has_wall(maze, current, direction):
                continue
            if coord in forbidden_cells:
                continue

            visited.add(coord)
            queue.append(coord)
            came_from[coord] = current  # remember where we came from

    if maze.exit not in came_from:
        raise ValueError(
            "Error: Exit is not reachable from the entry."
        )

    # backtrack from exit to entry, just like unwinding a stack
    current = maze.exit
    backtrace: list[tuple[int, int]] = []
    while current is not None:
        backtrace.append(current)
        current = came_from[current]

    return list(reversed(backtrace))


def path_to_directions(path: list[tuple[int, int]]) -> list[str]:
    """
    Convert coordinate path to direction letters (N, E, S, W).

    Args:
        path: List of (x, y) coordinates from entry to exit.

    Returns:
        List of direction letters.
    """
    from walls import Direction

    letters: list[str] = []
    for i in range(len(path) - 1):
        x1, y1 = path[i]
        x2, y2 = path[i + 1]
        dx, dy = x2 - x1, y2 - y1
        for direction in Direction:
            if direction.delta == (dx, dy):
                letters.append(direction.name[0])
                break
    return letters
