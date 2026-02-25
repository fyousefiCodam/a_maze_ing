"""
Maze generator module.
This module generates a maze using Depth-First Search (DFS). It can generate
either a perfect maze (single path between any two cells) or an imperfect
maze (multiple paths/loops) depending on the configuration.
"""
from __future__ import annotations
import random
from maze_definition import Maze
from walls import Direction, get_neighbours, remove_wall, has_wall


def has_3x3_open(maze: Maze, x: int, y: int) -> bool:
    """
    Checks if a 3 x3 block starting at(x, y) is fully open.

    Args:
        maze: The maze to check.
        x: Top-left x coordinate of the block.
        y: Top-left y coordinate of the block.

    Returns:
        True if the entire 3x3 area has no internal walls.
    """
    for row in range(y, y + 3):
        for col in range(x, x + 3):
            if col < x + 2:
                if has_wall(maze, (col, row), Direction.EAST):
                    return False
            if row < y + 2:
                if has_wall(maze, (col, row), Direction.SOUTH):
                    return False
    return True


def creates_3x3_nearby(maze: Maze, x: int, y: int) -> bool:
    """
    Check if any 3x3 block near (x, y) is fully open.

    Args:
        maze: The maze to check.
        x: x coordinate of the recently changed cell.
        y: y coordinate of the recently changed cell.

    Returns:
        True if a 3x3 open area exists nearby.
    """
    for dy in range(-2, 1):
        for dx in range(-2, 1):
            check_x = x + dx
            check_y = y + dy
            if (
                0 <= check_x <= maze.width - 3
                and 0 <= check_y <= maze.height - 3
            ):
                if has_3x3_open(maze, check_x, check_y):
                    return True
    return False


def add_wall_back(
    maze: Maze,
    coord_a: tuple[int, int],
    coord_b: tuple[int, int]
) -> None:
    """
    Restore a wall between two adjacent cells.

    Args:
        maze: The maze to modify.
        coord_a: First cell coordinates.
        coord_b: Second cell coordinates.

    Raises:
        ValueError: If the two cells are not adjacent.
    """
    ax, ay = coord_a
    bx, by = coord_b
    dx, dy = bx - ax, by - ay

    for direction in Direction:
        if direction.delta == (dx, dy):
            maze.grid[ay][ax] |= direction.value
            maze.grid[by][bx] |= direction.opposite.value
            return

    raise ValueError("Cells are not adjacent")


def add_cycles_safely(
    maze: Maze,
    forbidden_cells: set[tuple[int, int]],
    attempts: int = 300
) -> None:
    """
    Open extra walls to create loops while keeping the maze valid.

    Picks random cells and tries to open a wall to a neighbour. Rejects
    the opening if it would create a 3x3 open area. Skips forbidden cells
    to protect the '42' pattern.

    Args:
        maze: The maze to modify in place.
        forbidden_cells: Cells to never touch (e.g. the '42' pattern).
        attempts: Number of random attempts to try.
    """
    for _ in range(attempts):

        x = random.randint(0, maze.width - 1)
        y = random.randint(0, maze.height - 1)

        if (x, y) in forbidden_cells:
            continue

        neighbours = get_neighbours(maze, (x, y))
        random.shuffle(neighbours)

        for (nx, ny), direction in neighbours:

            if (nx, ny) in forbidden_cells:
                continue

            if not has_wall(maze, (x, y), direction):
                continue

            remove_wall(maze, (x, y), (nx, ny))

            if creates_3x3_nearby(maze, x, y):
                add_wall_back(maze, (x, y), (nx, ny))

            break


def generate_dfs(
    maze: Maze,
    seed: int,
) -> None:
    """
    Generate a perfect maze using iterative Depth-First Search.

    Starts from the maze entry and carves paths by removing walls between
    unvisited neighbours. Uses a stack to backtrack when stuck.

    Args:
        maze: The maze to generate in place.
        seed: Random seed for reproducibility.
    """
    random.seed(seed)
    stack = [maze.entry]
    maze.visited.add(maze.entry)

    while stack:
        current = stack[-1]

        neighbours = get_neighbours(maze, current)
        unvisited = [
            (coord, direction)
            for coord, direction in neighbours
            if coord not in maze.visited
        ]

        if unvisited:
            next_coord, direction = random.choice(unvisited)
            remove_wall(maze, current, next_coord)
            maze.visited.add(next_coord)
            stack.append(next_coord)
        else:
            stack.pop()


def generate_maze(
    maze: Maze,
    seed: int,
    perfect: bool,
    forbidden_cells: set[tuple[int, int]]
) -> None:
    """
    Generate a maze, either perfect or imperfect.

    Runs DFS to carve a perfect maze first. If perfect is False, opens
    extra walls to create loops. The '42' pattern is always stamped last
    to ensure it is never overwritten.

    Args:
        maze: The maze to generate in place.
        seed: Random seed for reproducibility.
        perfect: If True, keeps the maze perfect (single path).
        forbidden_cells: Cells reserved for the '42' pattern.
    """
    generate_dfs(maze, seed)

    if not perfect:
        add_cycles_safely(maze, forbidden_cells)


# def print_visual(self):
#     """Print ASCII visualization"""
#     # Top border
#     print('+' * (self.width * 2 + 1))
        
#     for row in range(self.height):
#         # Print cell row
#         line = '+'
#         for col in range(self.width):
#             cell = self.grid[row][col]
#             line += ' '  # Cell interior
#             # East wall
#             if cell & self.EAST:
#                 line += '+'
#             else:
#                 line += ' '
#     print(line)
            
#     # Print south walls
#     line = '+'
#     for col in range(self.width):
#         cell = self.grid[row][col]
#         # South wall
#         if cell & self.SOUTH:
#             line += '+'
#         else:
#             line += ' '
#         line += '+'
#     print(line)
