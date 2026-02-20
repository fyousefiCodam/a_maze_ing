"""
Handles visual rendering of the maze in the terminal with ANSI colours,
interactive menu, path toggle, and colour cycling.
"""

import os
from typing import List, Tuple, Optional, Callable


# ANSI helpers


RESET = "\033[0m"

# Wall colour palette (background colours) – cycled by option 3
WALL_PALETTES: List[str] = [
    "\033[47m",   # white
    "\033[43m",   # yellow
    "\033[44m",   # blue
    "\033[41m",   # red
    "\033[42m",   # green
    "\033[45m",   # magenta
    "\033[46m",   # cyan
    "\033[100m",  # dark grey
]

OPEN_BG = "\033[40m"          # black  – open passage interior
PATH_BG = "\033[46m"          # cyan   – solution path
ENTRY_BG = "\033[45m"          # magenta – entry cell
EXIT_BG = "\033[41m"          # red     – exit cell

# Wall-direction bitmasks (from the subject spec)
NORTH: int = 0b0001   # bit 0
EAST:  int = 0b0010   # bit 1
SOUTH: int = 0b0100   # bit 2
WEST:  int = 0b1000   # bit 3

_PALETTE_NAMES: List[str] = [
    "White", "Yellow", "Blue", "Red",
    "Green", "Magenta", "Cyan", "Dark",
]


# Path utilities
def path_to_coords(
    entry: Tuple[int, int],
    path_str: str,
) -> List[Tuple[int, int]]:
    """Convert a path string (e.g. 'EESS') to a list of (x, y) cell coords.

    Args:
        entry: Starting (x, y) cell.
        path_str: Sequence of moves using N, E, S, W characters.

    Returns:
        Ordered list of (x, y) cells visited, including entry.
    """
    x, y = entry
    coords: List[Tuple[int, int]] = [(x, y)]
    move_map: dict = {
        'N': (0, -1),
        'S': (0, 1),
        'E': (1, 0),
        'W': (-1, 0),
    }
    for ch in path_str.upper():
        dx, dy = move_map.get(ch, (0, 0))
        x += dx
        y += dy
        coords.append((x, y))
    return coords


# Core renderer
def build_pixel_grid(
    grid: List[List[int]],
    width: int,
    height: int,
    entry: Tuple[int, int],
    exit_pos: Tuple[int, int],
    path_coords: Optional[List[Tuple[int, int]]] = None,
    show_path: bool = False,
) -> List[List[str]]:
    """Build a pixel grid from the maze data.

    The pixel grid has size (2*height+1) rows x (2*width+1) cols.
    Cell (cx, cy) maps to pixel centre (2*cx+1, 2*cy+1).
    Even-indexed rows/cols represent walls or corners.

    Pixel type codes:
        'W'  – wall (closed)
        'O'  – open passage
        'P'  – solution path
        'E'  – entry cell
        'X'  – exit cell

    Args:
        grid: 2-D list of cell bitmasks [row][col].
        width: Number of columns.
        height: Number of rows.
        entry: Entry cell (x, y).
        exit_pos: Exit cell (x, y).
        path_coords: List of (x, y) cells forming the solution.
        show_path: Whether to highlight the solution path.

    Returns:
        2-D list of pixel type codes.
    """
    pw = 2 * width + 1
    ph = 2 * height + 1

    # Initialise all pixels as walls
    pixels: List[List[str]] = [['W'] * pw for _ in range(ph)]

    path_set = set(path_coords) if path_coords and show_path else set()

    for cy in range(height):
        for cx in range(width):
            cell = grid[cy][cx]
            px = 2 * cx + 1
            py = 2 * cy + 1

            # Determine cell-interior type
            if (cx, cy) == entry:
                cell_type = 'E'
            elif (cx, cy) == exit_pos:
                cell_type = 'X'
            elif show_path and (cx, cy) in path_set:
                cell_type = 'P'
            else:
                cell_type = 'O'

            pixels[py][px] = cell_type

            # Open passage pixels where no wall exists
            if not (cell & NORTH) and cy > 0:
                pixels[py - 1][px] = 'O'
            if not (cell & SOUTH) and cy < height - 1:
                pixels[py + 1][px] = 'O'
            if not (cell & WEST) and cx > 0:
                pixels[py][px - 1] = 'O'
            if not (cell & EAST) and cx < width - 1:
                pixels[py][px + 1] = 'O'

    # Overlay path on passage pixels between consecutive path cells
    if path_coords and show_path:
        for i in range(len(path_coords) - 1):
            cx, cy = path_coords[i]
            nx, ny = path_coords[i + 1]
            # Pixel sitting between the two cell centres
            mid_px = cx + nx + 1   # == (2*cx+1 + 2*nx+1) // 2
            mid_py = cy + ny + 1
            if pixels[mid_py][mid_px] == 'O':
                pixels[mid_py][mid_px] = 'P'

    return pixels


def pixels_to_string(
    pixels: List[List[str]],
    wall_color_idx: int = 0,
) -> str:
    """Convert a pixel grid to a coloured ANSI string ready to print.

    Each pixel is rendered as two terminal characters wide so the output
    looks more square on typical monospace fonts.

    Args:
        pixels: 2-D list of pixel type codes from build_pixel_grid.
        wall_color_idx: Index into WALL_PALETTES.

    Returns:
        Multi-line string with ANSI escape codes.
    """
    wall_bg = WALL_PALETTES[wall_color_idx % len(WALL_PALETTES)]
    color_map: dict = {
        'W': wall_bg,
        'O': OPEN_BG,
        'P': PATH_BG,
        'E': ENTRY_BG,
        'X': EXIT_BG,
    }

    lines: List[str] = []
    for row in pixels:
        line = ""
        for pixel in row:
            bg = color_map.get(pixel, OPEN_BG)
            line += bg + "  " + RESET
        lines.append(line)
    return "\n".join(lines)


def render_maze(
    grid: List[List[int]],
    width: int,
    height: int,
    entry: Tuple[int, int],
    exit_pos: Tuple[int, int],
    path_str: str = "",
    show_path: bool = False,
    wall_color_idx: int = 0,
) -> str:
    """Render the full maze as a coloured terminal string.

    Args:
        grid: 2-D list of cell bitmasks [row][col].
        width: Number of columns.
        height: Number of rows.
        entry: Entry cell (x, y).
        exit_pos: Exit cell (x, y).
        path_str: Solution path string (e.g. 'EESS').
        show_path: Whether to display the solution path.
        wall_color_idx: Colour palette index for walls.

    Returns:
        ANSI-coloured string ready to be printed.
    """
    path_coords: Optional[List[Tuple[int, int]]] = None
    if path_str:
        path_coords = path_to_coords(entry, path_str)

    pixels = build_pixel_grid(
        grid, width, height, entry, exit_pos, path_coords, show_path
    )
    return pixels_to_string(pixels, wall_color_idx)


# Display helpers
def clear_screen() -> None:
    """Clear the terminal screen portably."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_maze_frame(
    maze_str: str,
    show_path: bool,
    wall_color_idx: int,
    entry: Tuple[int, int],
    exit_pos: Tuple[int, int],
) -> None:
    """Print the maze with a status bar above it.

    Args:
        maze_str: Pre-rendered ANSI maze string.
        show_path: Current path-visibility state.
        wall_color_idx: Current palette index.
        entry: Entry coordinates.
        exit_pos: Exit coordinates.
    """
    palette_name = _PALETTE_NAMES[wall_color_idx % len(_PALETTE_NAMES)]
    path_state = "\033[32mON\033[0m" if show_path else "\033[31mOFF\033[0m"

    print(
        f"\033[1m=== A-Maze-ing ===\033[0m  "
        f"Entry: {ENTRY_BG}  {RESET} \033[35m({entry[0]},{entry[1]})\033[0m  "
        f"Exit: {EXIT_BG}  {RESET} \033[31m({exit_pos[0]},{exit_pos[1]})\033[0m  "
        f"Path: {path_state}  "
        f"Walls: \033[1m{palette_name}\033[0m"
    )
    print()
    print(maze_str)
    print()


def print_legend() -> None:
    """Print a colour legend below the maze."""
    print(
        f"  {ENTRY_BG}  {RESET} Entry   "
        f"  {EXIT_BG}  {RESET} Exit    "
        f"  {PATH_BG}  {RESET} Solution path   "
        f"  {OPEN_BG}  {RESET} Passage"
    )
    print()


def print_menu() -> None:
    """Print the interactive menu."""
    print("\033[1m1.\033[0m Re-generate a new maze")
    print("\033[1m2.\033[0m Show / Hide path from entry to exit")
    print("\033[1m3.\033[0m Rotate maze wall colours")
    print("\033[1m4.\033[0m Quit")


# Main interactive loop
def run_ui(
    grid: List[List[int]],
    width: int,
    height: int,
    entry: Tuple[int, int],
    exit_pos: Tuple[int, int],
    path_str: str,
    regenerate_fn: Optional[Callable[[], Tuple[
        List[List[int]],
        Tuple[int, int],
        Tuple[int, int],
        str,
    ]]] = None,
) -> None:
    """Run the interactive ASCII terminal UI.

    Displays the maze and processes user input in a loop.

    Args:
        grid: 2-D list of cell bitmasks [row][col].
        width: Number of columns.
        height: Number of rows.
        entry: Entry cell (x, y).
        exit_pos: Exit cell (x, y).
        path_str: Solution path string (e.g. 'EENNESS...').
        regenerate_fn: Optional callback that returns a new
                       (grid, entry, exit_pos, path_str) tuple.
                       If None, option 1 shows a notice.
    """
    show_path: bool = False
    wall_color_idx: int = 0

    while True:
        clear_screen()

        maze_str = render_maze(
            grid, width, height, entry, exit_pos,
            path_str, show_path, wall_color_idx,
        )

        print_maze_frame(maze_str, show_path, wall_color_idx, entry, exit_pos)
        print_legend()
        print_menu()

        if regenerate_fn is None:
            print("\033[2m(Re-generate unavailable: no generator provided)\033[0m")

        try:
            choice = input("\nChoice (1-4): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if choice == '1':
            if regenerate_fn is not None:
                try:
                    grid, entry, exit_pos, path_str = regenerate_fn()
                    show_path = False  # Reset path display on new maze
                except Exception as exc:
                    clear_screen()
                    print(f"\033[31mError during regeneration: {exc}\033[0m")
                    input("Press Enter to continue...")
            else:
                input(
                    "\033[33mNo generator available yet. "
                    "Press Enter to continue...\033[0m"
                )

        elif choice == '2':
            show_path = not show_path

        elif choice == '3':
            wall_color_idx = (wall_color_idx + 1) % len(WALL_PALETTES)

        elif choice == '4':
            print("Goodbye!")
            break

        else:
            input("\033[33mInvalid choice. Press Enter to continue...\033[0m")


# Standalone entry-point (quick renderer test)
if __name__ == "__main__":
    # Demo with a small 3x3 maze matching maze.txt
    demo_grid: List[List[int]] = [
        [0xF, 0xE, 0xD],
        [0xB, 0x0, 0x7],
        [0x9, 0x3, 0x6],
    ]
    demo_entry: Tuple[int, int] = (0, 0)
    demo_exit: Tuple[int, int] = (2, 2)
    demo_path = "EESS"

    run_ui(
        grid=demo_grid,
        width=3,
        height=3,
        entry=demo_entry,
        exit_pos=demo_exit,
        path_str=demo_path,
    )
