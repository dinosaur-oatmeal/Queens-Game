import tkinter as tk
import random

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

'''
Generate one N-Queens solution
board_size: size of the board (square)
output: list where index = row, and value = column of queen
'''
def generate_queen_solution(board_size: int) -> list[int]:
    # Store queen placement
    sol = [-1] * board_size

    # Used columns, L -> R diag, and R -> L diag
    used_cols = set()
    used_diag1 = set()
    used_diag2 = set()

    # Loop through putting a queen in each row
    def backtrack(row):
        # Return copy of solution when at last row
        if row == board_size:
            return sol.copy()
        
        # Look through columns in a random order (avoids same solution)
        for col in random.sample(range(board_size), board_size):

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
            
            #print(f"undoing placement at ({row}, {col})")
            
            # Undo current placement if it's invalid in the future
            used_cols.remove(col)
            used_diag1.remove(row + col)
            used_diag2.remove(row - col)
        
        # All posibilities exhausted, so undo (backtrack to previous row)
        return None

    # Call function starting at row 0
    solution = backtrack(0)
    (f"generate_queen_solution({board_size}) -> {solution}")
    return solution

'''
Return true if queens can attack one another and false if not
row1, col1: position of the first queen
row2, col2: position of the second queen
output: True if they are in the same row, column, or diagonal; otherwise False
'''
def queens_attack(row1: int, col1: int, row2: int, col2: int) -> bool:
    # Rows, columns, and diagonal
    return row1 == row2 or col1 == col2 or abs(row1 - row2) == abs(col1 - col2)

'''
Find solution with each queen in a different colored region
region_board: 2D list of integers where region_board[row][col] = region_id
output: A list of solutions, where each solution maps (row, column): solution[row] = column
'''
def find_queen_solutions(region_board: list[list[int]]) -> list[list[int]]:
    n = len(region_board)
    # Dictionary mapping region ID to a list of board cells (row, col) in that region
    region_cells = {region_id: [] for region_id in range(n)}

    # Populate region's list with all cells in it
    for row in range(n):
        for col in range(n):
            # Location of a specific color
            region = region_board[row][col]
            # List of lists corresponding to board colors
            region_cells[region].append((row, col))

    # Sort regions by how many cells they have
        # Small cells sorted first (MRV heuristic)
    region_order = sorted(region_cells, key = lambda r: len(region_cells[r]))

    # Track which constraints are already used
    used_rows = set()
    used_cols = set()
    used_diag1 = set()
    used_diag2 = set()
    # Maps region_id to (row, col)
    queen_in_region = {}
    # keep track of solution locations found
    solutions = []

    # Recursive CSP solver
    def backtrack(region_index):
        # Only care if there's > 1 solution
        if len(solutions) >= 2:
            return
        
        # All regions assigned a queen
        if region_index == n:
            board_row_to_col = [-1] * n
            # Loop through region ids
            for region_id, (row, col) in queen_in_region.items():
                # Store column of queen placement in row position of list
                board_row_to_col[row] = col
            # Add to solutions
            solutions.append(board_row_to_col)
            #print(f"Found Solution: {board_row_to_col}")
            return
        
        current_region = region_order[region_index]
        #print(f"Trying to place queen for region {current_region} (index {region_index})")
        # Loop through all cells in current region
        for (row, col) in region_cells[current_region]:
            # Placement invalid so skip
            if (row in used_rows or col in used_cols or
                (row + col) in used_diag1 or (row - col) in used_diag2):
                continue

            # Add the queen to that position
                # Track location in used sets and then put in region list
            used_rows.add(row)
            used_cols.add(col)
            used_diag1.add(row + col)
            used_diag2.add(row - col)
            queen_in_region[current_region] = (row, col)
            # Recurse to the next region
            backtrack(region_index + 1)

            # Backtrack and undo the move
            used_rows.remove(row)
            used_cols.remove(col)
            used_diag1.remove(row + col)
            used_diag2.remove(row - col)
            del queen_in_region[current_region]

            # Early stopping
            if len(solutions) >= 2:
                return

    # Call backtrack starting at row 0
    backtrack(0)
    (f"find_queen_solutions: returning {len(solutions)} solution(s)")
    return solutions

'''
Sees if a given region of the board remains connected after removing a cell
region_board: 2D grid where each cell has a region ID
region_id: the ID of the region to check
cell_to_remove: (row, col) of the cell to remove from the region
output: True if all remaining cells in the region are still 4-connected; otherwise False
'''
def is_region_connected(region_board: list[list[int]], region_id: int, cell_to_remove: tuple[int, int]) -> bool:
    n = len(region_board)

    # Get all cells in the region except the one being removed
    cells = [(i, j)
             for i in range(n)
             for j in range(n)
             if region_board[i][j] == region_id and (i, j) != cell_to_remove
            ]
    
    # No cells left, so region is not connected
    if not cells:
        return False
    
    # Set of cells visited and stack of cells to visit
    visited = set()
    # Start from a remaining cell
    stack = [cells[0]]

    # DFS traversal to all cells in list
    while stack:
        row, col = stack.pop()

        # Skip visited cells
        if (row, col) in visited:
            continue

        # Add new cells to set
        visited.add((row, col))

        # Check 4 connected neighbors (up, down, left, right)
        for d_row, d_col in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor_row = row + d_row
            neighbor_col = col + d_col
        
            # Ensure neighbor cell inside board
            if (0 <= neighbor_row < n) and (0 <= neighbor_col < n):
                neighbor = (neighbor_row, neighbor_col)

                # Add to stack if part of same region and not removed cell
                if (region_board[neighbor_row][neighbor_col] == region_id and
                    neighbor != cell_to_remove and
                    neighbor not in visited):
                        stack.append(neighbor)

    # Region connected if we visited every cell
    return len(visited) == len(cells)

'''
Create regions of colors seeded from queen's solution placement
solution: list where index = row and value = column of each queen
board_size: size of the square board (N x N)
output: 2D list where each cell contains a region ID associated with a queen
'''
def generate_regions(solution: list[int], board_size: int) -> list[list[int]]:
    # Create an empty board
    board = [[None for _ in range(board_size)] for _ in range(board_size)]
    # Queue of cells to expand from (row, col, region_id)
    fringe = []

    # Place each queen's location as seed of region
    for region_id in range(board_size):
        row = region_id
        # Queen at (row, col) in solution
        col = solution[region_id]

        # Mark cell with its region
        board[row][col] = region_id
        #print(f"Seeded region {region_id} at cell ({row}, {col})")

        # Add neighbors to fringe (up, down, left, right)
        for d_row, d_col in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor_row = row + d_row
            neighbor_col = col + d_col

            # Ensure neighbor cell inside board
            if 0 <= neighbor_row < board_size and 0 <= neighbor_col < board_size:
                fringe.append((neighbor_row, neighbor_col, region_id))

    # Randomize filling by randomly picking cells
        # Helps keep layouts irregular
    while fringe:
        index = random.randrange(len(fringe))
        row, col, region_id = fringe.pop(index)

        # Skip cells already assigned
        if board[row][col] is not None:
            continue

        # Assign cell this region's ID
        board[row][col] = region_id
        #print(f"Filled cell ({row}, {col}) with region {region_id}")

        # Add neighbors to the frontier
        for d_row, d_col in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor_row = row + d_row
            neighbor_col = col + d_col

            # Ensure neighbor cell inside board and not already assigned
            if (0 <= neighbor_row < board_size and 0 <= neighbor_col < board_size and
                board[neighbor_row][neighbor_col] is None):
                fringe.append((neighbor_row, neighbor_col, region_id))
    
    # Final board output
    print("\nFinal region board:\n")
    for row in board:
        print(" ".join(str(cell) if cell is not None else '.' for cell in row))
    
    return board

'''
Modify regions to try and ensure only 1 valid solutiontarget_solution: the desired unique N-Queens solution (list of column positions)
region_board: 2D list where each cell has a region ID (initial configuration)
max_attempts: number of modification attempts before giving up
output: modified region_board with at most one valid N-Queens solution
'''
def carve_regions(target_solution: list[int], region_board: list[list[int]], max_attempts: int = 50) -> list[list[int]]:
    n = len(region_board)
    attempt = 0

    # Cap attempts at 1000
    while attempt < max_attempts:
        attempt += 1
        solutions = find_queen_solutions(region_board)

        # Return if uniqueness met
        if len(solutions) < 2:
            print(f"Uniqueness achieved after {attempt} attempt(s).")
            return region_board
        
        # Alternate solution that we want to get rid of
        alternate_solution = solutions[1]
        made_change = False

        for row in range(n):
            # Find first row where queen put in alternate column
            if alternate_solution[row] != target_solution[row]:
                wrong_col = alternate_solution[row]
                region_to_remove_from = region_board[row][wrong_col]

                # Try to remove cell from region by merging into a neighbor
                for d_row, d_col in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    neighbor_row = row + d_row
                    neighbor_col = wrong_col + d_col

                    # Ensure neighbor cell inside board
                    if (0 <= neighbor_row < n and 0 <= neighbor_col < n):
                        neighbor_region = region_board[neighbor_row][neighbor_col]

                        # See if regions are different and nsure region connectivity isn't broken
                        if (neighbor_region != region_to_remove_from and
                            is_region_connected(region_board, region_to_remove_from, (row, wrong_col))):
                            # Reassign to neighbor region
                            region_board[row][wrong_col] = neighbor_region
                            made_change = True
                            # Stop after successful change
                            break

                if made_change:
                    break
            
        if not made_change:
            print(f"Gave up after {attempt} attempt(s): can't modify further.")
            return region_board

    print(f"Maximum attempts ({max_attempts}) reached without enforcing uniqueness.")
    return region_board

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