import tkinter as tk
import random
from collections import deque

size = 0
# List for solution of queen placements
    # Row 'r' solution[r] is solution column
solution = []
# region[r][c] = region index of cell(r, c)
regions = []
region_colors = []
# 0 is empty and 1 is queen
player_board = []
# 0 is no 'X' and 1 is 'X'
player_notes = []

# Canvas dimensions
canvas_width = 800
canvas_height = 800

# Number of queens in puzzle
rand_one = 4
rand_two = 16

# Color palette for regions
palette = [
    "#e41a1c",  # red
    "#377eb8",  # blue
    "#4daf4a",  # green
    "#984ea3",  # purple
    "#ff7f00",  # orange
    "#ffff33",  # yellow
    "#a65628",  # brown
    "#f781bf",  # pink
    "#999999",  # gray
    "#66c2a5",  # teal
    "#fc8d62",  # salmon
    "#8da0cb",  # periwinkle
    "#4a2e74",  # dark purple
    "#a6d854",  # lime green
    "#ffd92f",  # bright yellow
    "#e5c494",  # tan
]

# Generate N-Queens solution
def generate_queen_solution(n):
    # Store queen placement
    sol = [-1] * n

    # Used columns, L -> R diag, and R -> L diag
    used_cols = set()
    used_diag1 = set()
    used_diag2 = set()

    # Loop through putting a queen in each row
    def backtrack(row):
        # Return copy of solution when at last row
        if row == n:
            return sol.copy()
        
        # Look through columns in a random order (avoids same solution)
        for col in random.sample(range(n), n):

            # Skip placement because it's invalid
            if col in used_cols or (row + col) in used_diag1 or (row - col) in used_diag2:
                continue

            # Put queen in that location
            sol[row] = col

            # Add location to constraint lists
            used_cols.add(col)
            used_diag1.add(row + col)
            used_diag2.add(row - col)

            # Try placing a queen in the next row
            res = backtrack(row + 1)
            if res:
                return res
            
            # Undo current placement if it's invalid in the future
            used_cols.remove(col)
            used_diag1.remove(row + col)
            used_diag2.remove(row - col)
        
        # All posibilities exhausted, so undo (backtrack to previous row)
        return None

    # Call function starting at row 0
    return backtrack(0)

# Return true if queens can attack one another and false if not
def queens_attack(r1, c1, r2, c2):
    return r1 == r2 or c1 == c2 or abs(r1 - r2) == abs(c1 - c2)

# Stop after finding 2 solutions (test for uniqueness)
def find_queen_solutions(regs):
    # Dictionary of domains mapping regions (r) to list of valid placements (i, j)
    n = len(regs)
    domains = {r: [] for r in range(n)}

    # Populate region's list with all cells in it
    for i in range(n):
        for j in range(n):
            domains[regs[i][j]].append((i, j))
    
    # Sort regions by how many cells they have
        # Small cells sorted first
    region_order = sorted(domains, key = lambda r: len(domains[r]))

    # Track which constraints are already used
    used_rows = set()
    used_cols = set()
    used_diag1 = set()
    used_diag2 = set()
    # Map each region to queen's cell
    assign = {}
    # keep track of solution locations found
    solutions = []

    # Recursive CSP solver
    def backtrack(idx):
        # Unique solution >= 2
        if len(solutions) >= 2:
            return
        
        # All regions assigned
        if idx == n:
            perm = [-1] * n
            for r, (i, j) in assign.items():
                # Column 'j' stored in row 'i'
                perm[i] = j
            solutions.append(perm)
            return
        
        # Try all valid placements for current region
        region = region_order[idx]
        for i, j in domains[region]:
            # Placement invalid so skip
            if (i in used_rows or j in used_cols or
                    (i + j) in used_diag1 or (i - j) in used_diag2):
                continue
            # Add the queen to that position
            used_rows.add(i); used_cols.add(j)
            used_diag1.add(i + j); used_diag2.add(i - j)
            assign[region] = (i, j)
            # Recurse to the next region
            backtrack(idx + 1)

            # Backtrack and try next placement
            used_rows.remove(i); used_cols.remove(j)
            used_diag1.remove(i + j); used_diag2.remove(i - j)
            del assign[region]

            # Early stopping
            if len(solutions) >= 2:
                return

    # Call backtrack starting at row 0
    backtrack(0)
    return solutions

# Sees if a given region of the board remains connected after removing a cell
def is_region_connected(regs, region_id, remove_cell):
    n = len(regs)

    # Get all cells in the region except the one being removed
    cells = [(i, j) for i in range(n) for j in range(n)
             if regs[i][j] == region_id and (i, j) != remove_cell]
    
    # No cells left, so region is not connected
    if not cells:
        return False
    
    # Set of cells visited and stack of cells to visit
    visited = set()
    stack = [cells[0]]

    # DFS traversal to all cells in list
    while stack:
        i, j = stack.pop()

        # Skip visited cells
        if (i, j) in visited:
            continue

        # Add new cells to set
        visited.add((i, j))

        # Check 4 connected neighbors (up, down, left, right)
        for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ni, nj = i + di, j + dj

            # Add to stack if part of same region and not removed cell
            if (ni, nj) not in visited and 0 <= ni < n and 0 <= nj < n:
                if regs[ni][nj] == region_id and (ni, nj) != remove_cell:
                    stack.append((ni, nj))

    # Return if all cells visited or not
    return len(visited) == len(cells)

# Create regions of colors seeded from queen's solution placement
def generate_regions(sol, n):
    # Create an empty board
    regs = [[None] * n for _ in range(n)]
    # List used for filling cells into region
    frontier = []

    # Place each queen's location as seed of region
    for r in range(n):
        i, j = r, sol[r]
        regs[i][j] = r

        # Add neighbors of seed to the frontier of it's specific region
        for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ni, nj = i + di, j + dj
            if 0 <= ni < n and 0 <= nj < n:
                frontier.append((ni, nj, r))

    # Randomize filling by randomly picking a frontier cell
        # Helps keep layouts irregular
    while frontier:
        idx = random.randrange(len(frontier))
        i, j, r = frontier.pop(idx)

        # Skip cells already assigned
        if regs[i][j] is not None:
            continue

        # Assign this cell to region 'r'
        regs[i][j] = r
        # Add neighbors to the frontier
        for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ni, nj = i + di, j + dj
            if 0 <= ni < n and 0 <= nj < n and regs[ni][nj] is None:
                frontier.append((ni, nj, r))
    return regs

# Modify regions to ensure only 1 valid solution
def carve_regions(sol, regs):
    n = len(regs)

    # Loop until uniqueness met
    while True:
        # Returns up to 2 solutions
        sols = find_queen_solutions(regs)

        # Return once uniqueness is met
        if len(sols) < 2:
            return regs
        
        # Alternate solution (2nd) is solutions at 1
        alt = sols[1]
        made = False

        for r in range(n):
            # Find first row where queen put in "wrong" column
            if alt[r] != sol[r]:

                # Try to remove cell from it's current region
                i, j = r, alt[r]
                orig = regs[i][j]

                # Look at neighboring cells
                for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    ni, nj = i + di, j + dj

                    # See if we can remove that cell from the region
                    if 0 <= ni < n and 0 <= nj < n and regs[ni][nj] != orig:
                        if is_region_connected(regs, orig, (i, j)):
                            regs[i][j] = regs[ni][nj]
                            made = True
                            break
                break

        # Give up to avoid super long generations
        if not made:
            print("Warning: cannot enforce uniqueness further.")
            return regs

# Generate a puzzle
def generate_puzzle():
    global size, solution, regions, region_colors, player_board, player_notes, rand_one, rand_two

    # Number of queens in puzzle
    size = random.randint(rand_one, rand_two)

    # Generate queen placement
    solution = generate_queen_solution(size)
    # Generate regions around queens
    regs = generate_regions(solution, size)
    # Carve regions for uniqueness
    regions = carve_regions(solution, regs)
    # Colors of region
    region_colors = palette[:size]
    # Initialize board to no queens or notes placed
    player_board = [[0] * size for _ in range(size)]
    player_notes = [[0] * size for _ in range(size)]
    # Text for game description
    info_label.config(text = ("Place one queen in each colored region.\n"
                              "Queens attack in rows, columns, and diagonals."))

# Draw the board in the frame
def draw_board():
    canvas.delete("all")
    # Base case
    if size == 0:
        return
    
    # size each square based on current canvas size
    sq = min(canvas_width, canvas_height) / size
    for i in range(size):
        for j in range(size):
            # Paints square with corresponding region color
            color = region_colors[regions[i][j]]
            x1, y1 = j * sq, i * sq
            canvas.create_rectangle(x1, y1, x1 + sq, y1 + sq,
                                    fill = color, outline = "black")
            
            # Place queen icon in specific square
            if player_board[i][j] == 1:
                canvas.create_text(x1 + sq / 2, y1 + sq / 2, text = "♕",
                                   font = ("Arial", int(sq / 2)), fill = "black")
                
            # Place note icon in specific square
            elif player_notes[i][j] == 1:
                canvas.create_text(x1 + sq / 2, y1 + sq / 2, text = "X",
                                   font = ("Arial", int(sq / 3)), fill = "black")
    
    # Draw thick borders between regions for differentiation
    for i in range(size):
        for j in range(size):
            if j < size - 1 and regions[i][j] != regions[i][j + 1]:
                x = (j + 1) * sq
                canvas.create_line(x, i * sq, x, (i + 1) * sq, width = 2)
            if i < size - 1 and regions[i][j] != regions[i + 1][j]:
                y = (i + 1) * sq
                canvas.create_line(j * sq, y, (j + 1) * sq, y, width = 2)

# Check that player has solution
def check_win():
    # One queen per region and no attacks
    region_seen = set()
    positions = []

    # Loop through placed regions
    for i in range(size):
        for j in range(size):
            if player_board[i][j] == 1:
                reg = regions[i][j]
                # Region already seen
                if reg in region_seen:
                    return False
                region_seen.add(reg)
                positions.append((i, j))
    
    # Must have exactly one queen per region
    if len(region_seen) != size:
        return False
    
    # Ensure queens can't attack each other
    for idx, (r, c) in enumerate(positions):
        for (r2, c2) in positions[idx + 1:]:
            if queens_attack(r, c, r2, c2):
                return False
    return True

# Convert mouse into grid coordinate
def get_cell_from_event(event):
    if size == 0:
        return None
    
    # Convert screen (x, y) into a column, row
    sq = canvas_width / size
    j = int(event.x // sq)
    i = int(event.y // sq)
    if 0 <= i < size and 0 <= j < size:
        return (i, j)
    
    # Outside board
    return None

# Left-click to place queen
def on_click(event):
    cell = get_cell_from_event(event)
    if not cell:
        return
    i, j = cell
    reg = regions[i][j]
    # Remove a queen from the board
    if player_board[i][j] == 1:
        player_board[i][j] = 0
    else:
        # Clear any existing queen in region
        for x in range(size):
            for y in range(size):
                if regions[x][y] == reg:
                    player_board[x][y] = 0
        # Place new queen in the region
        player_board[i][j] = 1
    # Redraw the board
    draw_board()

    # See if the player won
    if check_win():
        info_label.config(text = "Congratulations! You found the solution!")
        canvas.unbind("<Button-1>")
        canvas.unbind("<Button-3>")

# Put a note on the board
def on_right_click(event):
    cell = get_cell_from_event(event)
    if not cell:
        return
    i, j = cell
    # Only allow 'X' on empty spaces
    if player_board[i][j] == 0:
        player_notes[i][j] ^= 1
        # Redraw board
        draw_board()

# Shows answer to puzzle
def reveal_solution():
    # Loop through and place all queens in correct position
    for r in range(size):
        for c in range(size):
            player_board[r][c] = 0
        player_board[r][solution[r]] = 1
    # Redraw board
    draw_board()
    info_label.config(text = "Solution revealed.")

# Reset the game
def reset_game():
    # Left and right click
    canvas.bind("<Button-1>", on_click)
    canvas.bind("<Button-3>", on_right_click)
    # Generate a puzzle and draw the new board
    generate_puzzle()
    draw_board()

# Resize GUI
def on_resize(event):
    global canvas_width, canvas_height
    canvas_width = event.width
    canvas_height = event.height
    # Redraw the board with new dimensions
    draw_board()

# GIU setup
root = tk.Tk()
root.title("Queens Game")
canvas = tk.Canvas(root, width = canvas_width, height = canvas_height)
canvas.pack(padx = 10, pady = 10, expand = True, fill = "both")
# Left-click, right-click, and GUI resizing
canvas.bind("<Button-1>", on_click)
canvas.bind("<Button-3>", on_right_click)
canvas.bind("<Configure>", on_resize)
info_label = tk.Label(root, text = "", font = ("Arial", 12), width = 60)
info_label.pack(pady = 5)
btn_frame = tk.Frame(root)
# Solution and reset buttons
sol_btn = tk.Button(btn_frame, text = "Show Solution", command = reveal_solution)
reset_btn = tk.Button(btn_frame, text = "Reset Game", command = reset_game)
btn_frame.pack(pady = 5, fill = "x")
sol_btn.pack(side = "left", padx = 5, expand = True, fill = "x")
reset_btn.pack(side = "left", padx = 5, expand = True, fill = "x")

reset_game()
root.mainloop()