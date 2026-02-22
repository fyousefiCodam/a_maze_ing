from walls import get_neighbours, has_wall
from maze_definition import Maze
from collections import deque


def solve_bfs(maze: Maze) -> list[str]:

    queue = deque()
    queue.append((maze.entry, []))  # (current cell, path so far)
    visited = {maze.entry}

    while queue:
        current, path = queue.popleft()  # take from Front(not back!)

        if current == maze.exit:
            return path  # found it
        
        neighbours = get_neighbours(maze, current)
        for coord, direction in neighbours:
            if coord not in visited and not has_wall(maze, current, direction):
                visited.add(coord)
                queue.append((coord, path + [direction.name[0]]))

    return []   # no path found
