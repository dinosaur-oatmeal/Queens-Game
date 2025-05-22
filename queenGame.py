import tkinter as tk
import random
import math
import pygame

from queenGenerate import *

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
canvas_width = 1000
canvas_height = 1000

# Number of queens in puzzle
rand_one = 4
rand_two = 10

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
    "#4a2e74",  # dark purple
    "#a6d854",  # lime green
]

# Generate a puzzle
def generate_puzzle():
    global size, solution, regions, region_colors, player_board, player_notes, rand_one, rand_two

    while True:
        # Number of queens in puzzle
        size = random.randint(rand_one, rand_two)

        # Generate queen placement
        solution = generate_queen_solution(size)

        # Generate regions around queens
        regions = generate_regions(solution, size)

        # Carve regions for uniqueness
        carved_regions = carve_regions(solution, regions)

        # Verify that there's only one valid solution
        if len(find_queen_solutions(carved_regions)) < 2:
            regions = carved_regions
            break

    # Colors of region
    region_colors = palette[:size]
    # Initialize board to no queens or notes placed
    player_board = [[0] * size for _ in range(size)]
    player_notes = [[0] * size for _ in range(size)]

    # Text for game description
    info_label.config(text = ("Place one queen in each colored region.\n"
                            "Queens attack in rows, columns, and diagonals."))

def draw_board(conflicts = None):
    canvas.delete("all")
    # Base case
    if size == 0:
        return

    # size each square based on current canvas size
    sq = min(canvas_width, canvas_height) / size
    for i in range(size):
        for j in range(size):
            base_color = region_colors[regions[i][j]]
            x1, y1 = j * sq, i * sq

            # Highlight conflict
            if conflicts and (i, j) in conflicts:
                canvas.create_rectangle(x1, y1, x1 + sq, y1 + sq,
                                        fill = "lightcoral", outline = "black")
            
            # Paints square with corresponding region color
            else:
                canvas.create_rectangle(x1, y1, x1 + sq, y1 + sq,
                                        fill = base_color, outline = "black")

            # Place queen icon in specific square
            if player_board[i][j] == 1:
                queen_color = "red" if conflicts and (i, j) in conflicts else "black"
                canvas.create_text(x1 + sq / 2, y1 + sq / 2, text = "♕",
                                   font=("Arial", int(sq / 2)), fill = queen_color)

            # Place note icon in specific square
            elif player_notes[i][j] == 1:
                canvas.create_text(x1 + sq / 2, y1 + sq / 2, text = "X",
                                   font=("Arial", int(sq / 3)), fill = "black")

    # Draw thick borders between regions for differentiation
    for i in range(size):
        for j in range(size):
            if j < size - 1 and regions[i][j] != regions[i][j + 1]:
                x = (j + 1) * sq
                canvas.create_line(x, i * sq, x, (i + 1) * sq, width = 2)
            if i < size - 1 and regions[i][j] != regions[i + 1][j]:
                y = (i + 1) * sq
                canvas.create_line(j * sq, y, (j + 1) * sq, y, width = 2)

# See if queens are attacking each other
def check_conflicts():
    # Loop through queen positions
    positions = [(i, j) for i in range(size) for j in range(size) if player_board[i][j] == 1]
    # List of conflicts
    conflicts = []
    for idx, (r, c) in enumerate(positions):
        for (r2, c2) in positions[idx + 1:]:
            # See if queens are attacking one another
            if queens_attack(r, c, r2, c2):
                # Add to conflicts
                conflicts.extend([(r, c), (r2, c2)])
    
    # Only return unique positions
    return list(set(conflicts))

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

# Initialize mixer
pygame.mixer.init()
buzzer_sound = pygame.mixer.Sound("buzzer.mp3")

# Play the buzzer (allows overlaps)
def play_buzzer():
    buzzer_sound.play()

# Find Euclidean distance between 2 cells
def euclidean_too_far(board, conflicts):
    queen_positions = [(i, j) for i in range(size) for j in range(size) if board[i][j] == 1]

    # Only look at queens in conflict
    conflict_set = set(conflicts)

    for i, (x1, y1) in enumerate(queen_positions):
        for x2, y2 in queen_positions[i+1:]:
            if (x1, y1) in conflict_set and (x2, y2) in conflict_set:
                # Use center-of-cell positions
                dx = (x1 + 0.5) - (x2 + 0.5)
                dy = (y1 + 0.5) - (y2 + 0.5)
                dist = math.sqrt(dx**2 + dy**2)
                if dist >= 5:
                    #print(f"Euclidean distance: {dist:.2f} between {(x1, y1)} and {(x2, y2)}")
                    return True
    return False

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
    
    # Redraw the board with conflicts
    conflicts = check_conflicts()

    draw_board(conflicts)

    # See if the player won
    if check_win():
        info_label.config(text = "Congratulations! You found the solution!")
        canvas.unbind("<Button-1>")
        canvas.unbind("<Button-3>")
    elif conflicts:
        info_label.config(text = "NOT THE ANSWER | SKILL ISSUE")
        # Buzzer of doom
        if euclidean_too_far(player_board, conflicts) or len(conflicts) >= 3:
            #print(f"{conflicts}")
            play_buzzer()
    else:
        info_label.config(text = "")

        # 5% chance to randomly buzz if current board isn't the solution
        if not check_win() and random.random() < 0.05:
            info_label.config(text = "Random misfire buzzer!")
            play_buzzer()

# Track which cells we've already toggled in the current drag
dragged_cells = set()

# Right click to mark a singe note
def on_right_click(event):
    dragged_cells.clear()
    mark_note(event)

# Right click drag to mark multiple notes
def on_right_drag(event):
    mark_note(event)

# Marks a cell with a note
def mark_note(event):
    cell = get_cell_from_event(event)
    # No cell where click occured
    if not cell:
        return
    i, j = cell

    # Avoid flipping a cell twice during one drag
    if (i, j) in dragged_cells:
        return

    # Add cell to dragged set
    if player_board[i][j] == 0:
        player_notes[i][j] ^= 1
        dragged_cells.add((i, j))
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
canvas.bind("<B3-Motion>", on_right_drag)
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