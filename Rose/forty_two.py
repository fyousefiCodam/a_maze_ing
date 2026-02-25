from maze_definition import Maze

# Pixel-art bitmap for "42"
# 1 = solid/closed cell (all 4 walls), 0 = leave as-is
PATTERN_42: list[list[int]] = [
    [1, 0, 1, 0, 0, 1, 1, 1],
    [1, 0, 1, 0, 0, 1, 0, 1],
    [1, 1, 1, 0, 0, 1, 1, 1],
    [0, 0, 1, 0, 0, 1, 1, 0],
    [0, 0, 1, 0, 0, 1, 1, 1],
]

PATTERN_H: int = len(PATTERN_42)        # 5 rows
PATTERN_W: int = len(PATTERN_42[0])     # 8 cols


def can_fit_42(maze: Maze) -> bool:
    """Check if the maze is big enough to contain the '42' pattern."""
    return maze.width >= PATTERN_W + 2 and maze.height >= PATTERN_H + 2


def embed_42(maze: Maze) -> set[tuple[int, int]]:
    """
    Stamp the '42' pattern into the maze by closing all 4 walls
    on the relevant cells. Returns the set of stamped cells.
    If the maze is too small, prints an error and returns empty set.
    """
    if not can_fit_42(maze):
        print("Error: maze is too small to display the '42' pattern.")
        return set()

    # Center the pattern in the maze
    origin_x: int = (maze.width - PATTERN_W) // 2
    origin_y: int = (maze.height - PATTERN_H) // 2

    stamped: set[tuple[int, int]] = set()

    for row in range(PATTERN_H):
        for col in range(PATTERN_W):
            if PATTERN_42[row][col]:
                x = origin_x + col
                y = origin_y + row
                maze.grid[y][x] = 0xF  # North|East|South|West all closed
                stamped.add((x, y))

    return stamped