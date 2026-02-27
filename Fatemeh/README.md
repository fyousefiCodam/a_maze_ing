*This project has been created as part of the 42 curriculum by <fyousefi>, <hijohnso>.*

# A-Maze-ing

## Description

A-Maze-ing is a maze generator and solver written in Python. It generates mazes of
configurable size using a Depth-First Search (DFS) algorithm, and can produce either
a perfect maze (exactly one path between any two cells) or an imperfect maze (multiple
paths/loops). The maze is displayed in the terminal using ASCII art and always contains
a hidden "42" pattern drawn using fully closed cells. A shortest path from the entry to
the exit is computed using Breadth-First Search (BFS) and can be shown or hidden on demand.

## Instructions
Your project must be written in Python 3.10 or later.
• Your project must adhere to the flake8 coding standard.
• Your functions should handle exceptions gracefully to avoid crashes. Use try-except
blocks to manage potential errors. Prefer context managers for resources like files or
connections to ensure automatic cleanup. If your program crashes due to unhandled
exceptions during the review, it will be considered non-functional.
• All resources (e.g., file handles, network connections) must be properly managed to
prevent leaks. Use context managers where possible for automatic handling.
• Your code must include type hints for function parameters, return types, and variables where applicable (using the typing module). Use mypy for static type checking. All functions must pass mypy without errors.
• Include docstrings in functions and classes following PEP 257 (e.g., Google or
NumPy style) to document purpose, parameters, and returns.
Makefile
Include a Makefile in your project to automate common tasks. It must contain the
following rules (mandatory lint implies the specified flags; it is strongly recommended to
try –strict for enhanced checking):
• install: Install project dependencies using pip, uv, pipx, or any other package
manager of your choice.
• run: Execute the main script of your project (e.g., via Python interpreter).
• debug: Run the main script in debug mode using Python’s built-in debugger (e.g.,
pdb).
• clean: Remove temporary files or caches (e.g., __pycache__, .mypy_cache) to
keep the project environment clean.
5
A-Maze-ing This is the way
• lint: Execute the commands flake8 . and mypy . --warn-return-any
--warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs
--check-untyped-defs
• lint-strict (optional): Execute the commands flake8 . and mypy . --strict
Additional Guidelines
• Create test programs to verify project functionality (not submitted or graded). Use
frameworks like pytest or unittest for unit tests, covering edge cases.
• Include a .gitignore file to exclude Python artifacts.
• It is recommended to use virtual environments (e.g., venv or conda) for dependency
isolation during development

### Running the program

```bash
python3 a_maze_ing.py config.txt
```

### Other commands

```bash
make run        # run with default config
make debug      # run with Python debugger (pdb)
make lint       # run flake8 and mypy checks
make clean      # remove __pycache__ and .mypy_cache
```

## Configuration File Format

The configuration file must contain one `KEY=VALUE` pair per line.
Lines starting with `#` are treated as comments and ignored.

### Mandatory keys

| Key | Description | Example |
|-----|-------------|---------|
| `WIDTH` | Maze width in cells | `WIDTH=20` |
| `HEIGHT` | Maze height in cells | `HEIGHT=15` |
| `ENTRY` | Entry coordinates (x,y) | `ENTRY=0,0` |
| `EXIT` | Exit coordinates (x,y) | `EXIT=19,14` |
| `OUTPUT_FILE` | Output filename | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | Perfect maze? (True/False) | `PERFECT=True` |

### Optional keys

| Key | Description | Example |
|-----|-------------|---------|
| `SEED` | Random seed for reproducibility | `SEED=42` |
| `ALGORITHM` | Generation algorithm to use | `ALGORITHM=DFS` |

### Example config file

```
# A-Maze-ing default configuration
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
ALGORITHM=DFS
```

## Maze Generation Algorithm

### Depth-First Search (DFS)

The primary algorithm is an iterative DFS (also known as recursive backtracker):

1. Start at the entry cell, push it onto a stack and mark it visited
2. Peek at the top of the stack (current cell)
3. If the current cell has unvisited neighbours, pick one at random, remove
   the wall between them, mark it visited and push it onto the stack
4. If there are no unvisited neighbours, backtrack by popping the stack
5. Repeat until the stack is empty (all cells visited)

### Why DFS?

- Produces mazes with long winding corridors — more interesting to solve
- Simple to implement iteratively using a stack
- Naturally produces a perfect maze (spanning tree of the grid)
- Easy to control with a seed for full reproducibility

## Output File Format

The maze is written row by row, one hexadecimal digit per cell. Each digit encodes
which walls are closed using 4 bits:

| Bit | Direction |
|-----|-----------|
| 0 (LSB) | North |
| 1 | East |
| 2 | South |
| 3 | West |

A closed wall sets the bit to `1`, an open wall sets it to `0`.

After an empty line, three lines follow:
- Entry coordinates
- Exit coordinates
- Shortest path from entry to exit as a sequence of `N`, `E`, `S`, `W` letters

### Example output

```
9515391539551795151151153
EBABAE812853C1412BA81281Z
...

0,0
19,14
SWSESWSESWSSSEESEEEN...
```

## Visual Representation

The maze is rendered in the terminal using ASCII block characters. The display
shows walls, the entry point, the exit point, and optionally the shortest path.

### Interactions

| Key | Action |
|-----|--------|
| `1` | Re-generate a new maze |
| `2` | Show / hide the shortest path |
| `3` | Rotate wall colours |
| `4` | Animate solution path |
| `5` | Quit |

## Code Reusability

The maze generation logic is packaged as a standalone installable Python package
called `mazegen`. It can be installed via pip and imported into any project.

### Installation

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

### Basic usage

```python
from mazegen import MazeGenerator

# create and generate a maze
gen = MazeGenerator(width=20, height=15, seed=42, perfect=True)
gen.generate()

# access the grid
print(gen.maze.grid)

# get the solution path as coordinates
path_coords = gen.solve()

# get the solution as direction letters
path_dirs = gen.solution_directions()
print(path_dirs)  # ['S', 'S', 'E', 'E', ...]
```

### Custom parameters

```python
gen = MazeGenerator(
    width=30,        # maze width in cells
    height=20,       # maze height in cells
    seed=123,        # random seed for reproducibility
    perfect=False,   # False = imperfect maze with loops
    algorithm="DFS"  # generation algorithm
)
```

### Accessing the structure

```python
gen.generate()

gen.maze.grid      # 2D list of hex wall values
gen.maze.entry     # (x, y) entry coordinates
gen.maze.exit      # (x, y) exit coordinates
gen.maze.width     # maze width
gen.maze.height    # maze height

gen.solve()                  # returns list of (x,y) coordinates
gen.solution_directions()    # returns list of 'N','E','S','W' strings
```

## Team and Project Management

### Roles

| Member | Responsibilities |
|--------|-----------------|
| `<login1>` | Maze generation (DFS), cycle adding, BFS solver, "42" pattern |
| `<login2>` | Config parser, output file writer, terminal display, main entry point |

### Planning

Initially we planned to finish the generation and display in the first week and
spend the second week on the reusable package and README. In practice the "42"
pattern and the 3x3 open area constraint took longer than expected, pushing the
display work into the second week.

### What worked well

- Splitting the project cleanly down the middle (generation vs display) meant
  we rarely blocked each other
- Agreeing on the `Maze` class interface early made integration straightforward
- Using a seed from the start made debugging much easier — same maze every run

### What could be improved

- We could have written unit tests earlier — some bugs in wall coherence took
  a while to track down without them
- The "42" pattern sizing could be more flexible to support very small mazes

### Tools used

- Python 3.10+
- `flake8` for style checking
- `mypy` for static type checking
- `pytest` for unit testing
- `build` for packaging the reusable module
- Claude (AI) — used to help explain concepts, review code structure, and
  suggest improvements to docstrings and type hints

## Resources

- [Maze generation algorithms — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Depth-First Search maze generation — Jamis Buck's blog](http://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracker)
DFS LOGIC - https://medium.com/@nacerkroudir/randomized-depth-first-search-algorithm-for-maze-generation-fb2d83702742
- [Python `collections.deque` documentation](https://docs.python.org/3/library/collections.html#collections.deque)
- [Python `enum` documentation](https://docs.python.org/3/library/enum.html)
- [Bitwise operations in Python](https://wiki.python.org/moin/BitwiseOperators)
- [Python packaging guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [mypy documentation](https://mypy.readthedocs.io/en/stable/)
- [flake8 documentation](https://flake8.pycqa.org/en/latest/)

### AI usage

Claude (Anthropic) was used during this project for the following tasks:

- Explaining concepts such as bitwise operations, BFS/DFS data structures,
  and the parent-dict path reconstruction approach
- Reviewing code structure and suggesting how to split responsibilities across files
- Helping write and improve docstrings and type hints to meet mypy requirements
- Suggesting the combined approach for `add_cycles_safely` (pre-scanned candidates
  with 3x3 open area checking)
All AI-generated content was reviewed, tested, and understood before being used.