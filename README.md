# Queens Game

An interactive puzzle game featuring **AI-generated N-Queens challenges**. The goal of the game is to place exactly one queen in each uniquely colored region without conflict. Every puzzle guarantees a unique solution!

## 🎯 How the AI Generates Your Puzzle

The puzzle generation AI algorithm creates each puzzle in three steps:

1. **Randomized N-Queens Solver**: Utilizing backtracking, a valid arrangement of queens for boards sized between 4 and 10 is randomly generated, helping create a variety of difficulty levels.

2. **Region Seeding & Expansion**: Each queen's placement acts as the seed for its region. A randomized flood-fill process expands these seeds, creating visually distinct, irregularly shaped regions that naturally guide queen placement during the game.

3. **Ensuring Unique Solutions**: A constraint-satisfaction algorithm employs the minimum remaining values (MRV) heuristic and iterative region carving. It methodically merges cells and eliminates alternative solutions until only one valid arrangement remains.

## 🚀 Game Features

### Customizable, Randomized Board Sizes

* **Tailored Difficulty**: Every puzzle randomly chooses between 4 and 10 queens, perfect for casual playing or strategic challenges.
* **Endless Variety**: Each puzzle is freshly generated on reset, mitigating the chances of receiving the same puzzle twice.

### Smart N-Queens Solver

* **Dynamic Puzzle Generation**: Uses randomized column orders to guarantee unpredictable layouts every time.
* **Optimized Efficiency**: Tracks placements with constraints for instant validity checks, speeding up puzzle generation dramatically.

### Visually Appealing Region Generation

* **Queen-based Region Formation**: Each queen's location initializes a distinct region, creating natural guides for queen placement.
* **Organic Layout**: Randomized flood-filling results in visually engaging, color-coded regions with clear boundaries.

### Unique Puzzle Assurance

* **Robust Conflict Checking**: Quickly detects multiple solutions, prioritizing regions with fewer placement options for rapid puzzle refinement.
* **Adaptive Merging**: Safely merges conflicting cells into neighboring regions, maintaining connectivity while enforcing a singular solution.

### Instant Conflict Feedback

* **Real-Time Detection**: Immediate visual feedback highlights conflicts whenever queens threaten each other in rows, columns, or diagonals.
