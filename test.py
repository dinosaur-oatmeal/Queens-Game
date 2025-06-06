import random
from itertools import product

# Import core functions from your queenPuzzle module
from logic import *

# Brute force a puzzle
def brute_force_solutions(regions, size):
    # Dictionary mapping region ID to a list of board cells (row, col) in that region
    region_cells = {r: [] for r in range(size)}
    for row in range(size):
        for col in range(size):
            # List of lists corresponding to board colors
            region_cells[regions[row][col]].append((row, col))

    valid_solutions = []
    # Iterate over all combinations (one cell per region)
    for placement in product(*(region_cells[r] for r in range(size))):
        # Check queen-attack constraint
        ok = True
        for a in range(size):
            for b in range(a + 1, size):
                r1, c1 = placement[a]
                r2, c2 = placement[b]
                # See if queens can attack
                if queens_attack(r1, c1, r2, c2):
                    ok = False
                    break
            if not ok:
                break
        
        # Solution is valid
        if ok:
            valid_solutions.append(placement)

    return valid_solutions

def main(rand_one = 4, rand_two = 8):
    # Loop through 1000 puzzles and brute force their solutions
        # Ensure puzzle generation only outputs puzzles with one answer
    total_unique = 0
    for i in range(500):
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

            # Regenerate if more solutions
            print(f"Regenerating puzzle")

        # Brute force to verify only one solution
        sols = brute_force_solutions(carved_regions, size)
        count = len(sols)
        # Increment total unique
        if count == 1:
            total_unique += 1
        
        print(f"\ntest {i}: Generated {size}*{size} puzzle, found {count} valid placement(s).")
    
    print(f"\n\n{total_unique} unique solutions")

if __name__ == "__main__":
    main()