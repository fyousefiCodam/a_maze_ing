import random
from maze_definition import Maze
from walls import Direction, get_neighbours, remove_wall


def generate_dfs(
        maze: Maze,
        seed: int,
) -> None:

    stack = [maze.entry]  # start from entry
    maze.visited.add(maze.entry)

    while stack:
        current = stack[-1]  # peak from the top 

        # get unvisited neighbours
        neighbours = get_neighbours(maze, current)
        unvisited = [
            (coord, direction)
            for coord, direction in neighbours
            if coord not in maze.visited   # only keep unvisted ones
        ]

        if unvisited:
            # pick a random neighbour
            next_coord, direction = random.choice(unvisited)

            # remove a wall between current and next

            remove_wall(maze, current, next_coord)
            maze.visited.add(next_coord)  # <- inside if unvisted
            stack.append(next_coord)  # <- inside if unvisted

            #  mark visited and push to stack
        else: 
            # dead end - backtrack
            stack.pop()


def print_visual(self):
    """Print ASCII visualization"""
    # Top border
    print('+' * (self.width * 2 + 1))
        
    for row in range(self.height):
        # Print cell row
        line = '+'
        for col in range(self.width):
            cell = self.grid[row][col]
            line += ' '  # Cell interior
            # East wall
            if cell & self.EAST:
                line += '+'
            else:
                line += ' '
    print(line)
            
    # Print south walls
    line = '+'
    for col in range(self.width):
        cell = self.grid[row][col]
        # South wall
        if cell & self.SOUTH:
            line += '+'
        else:
            line += ' '
        line += '+'
    print(line)
