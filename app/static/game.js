// Colors for game regions
const palette = [
    "#e41a1c", "#377eb8", "#4daf4a", "#984ea3",
    "#ff7f00", "#ffff33", "#a65628", "#f781bf",
    "#999999", "#66c2a5", "#4a2e74", "#a6d854"
  ];

// Holds what the back-end sends
let gameData,
  // Hold queen positions and 'X' marks on game board
  boardState = [],
  noteState = [],
  // Sound for buzzer boolean
    // Decided not to choose violence and defaulted to no audio
  soundOn = false,
  // Track for click and drag notes
  dragging = false,
  dragButton = null,
  lastToggledCell = null,
  // Game winning flag
  gameWon = false;

// Renders the SVG board
function draw(conflicts = [])
{
  const board = document.getElementById("board");
  // Clear previous board
  board.innerHTML = "";
  const size = gameData.size;
  
  // Get size of board to render
  const svgWidth = board.clientWidth;
  const svgHeight = board.clientHeight;
  const sq = Math.min(svgWidth, svgHeight) / size;

  // Fill in colors of the board
  for (let i = 0; i < size; i++)
  {
    for (let j = 0; j < size; j++)
    {
      const regionId = gameData.regions[i][j];
      let fillColor = palette[regionId % palette.length];

      // Highlights conflict cells
      if (conflicts.some(([x, y]) => x === i && y === j)) 
      {
          fillColor = "lightcoral";
      }

      // Draw one <rect> per cell on the board
      const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
      rect.setAttribute("x", j * sq);
      rect.setAttribute("y", i * sq);
      rect.setAttribute("width", sq);
      rect.setAttribute("height", sq);
      rect.setAttribute("fill", fillColor);
      rect.setAttribute("stroke", "black");

      // Disable context menu on right click
      rect.addEventListener("contextmenu", (e) => e.preventDefault());

      // Start drag or toggle
      rect.addEventListener("mousedown", (e) => {
          e.preventDefault();
          dragging = true;
          // 0 = left | 2 = right
          dragButton = e.button;
          lastToggledCell = `${i},${j}`;

          // Add queen to board
          if (e.button === 0) toggleQueen(i, j);
          // Add note to board
          else if (e.button === 2) toggleNote(i, j);
      });

      // While dragging right, chain note markings together
      rect.addEventListener("mouseenter", (e) => {
        // Exit if not dragging right click
        if (!dragging || dragButton !== 2) return;
        const cellId = `${i},${j}`;

        // Toggle note if different from last toggled cell
        if (cellId !== lastToggledCell)
        {
            lastToggledCell = cellId;
            toggleNote(i, j);
        }
      });

      // Add cell to board object
      board.appendChild(rect);

      // Draw a queen in the cell
      if (boardState[i][j])
      {
          const q = document.createElementNS("http://www.w3.org/2000/svg", "text");
          q.setAttribute("x", j * sq + sq / 2);
          q.setAttribute("y", i * sq + sq * 0.65);
          q.setAttribute("text-anchor", "middle");
          q.setAttribute("font-size", sq / 2);
          q.classList.add("queen");
          q.textContent = "♕";
          board.appendChild(q);
      }

      // Draw a note in the cell
      else if (noteState[i][j])
      {
          const x = document.createElementNS("http://www.w3.org/2000/svg", "text");
          x.setAttribute("x", j * sq + sq / 2);
          x.setAttribute("y", i * sq + sq * 0.6);
          x.setAttribute("text-anchor", "middle");
          x.classList.add("note");
          x.textContent = "X";
          board.appendChild(x);
      }
    }
  }
}

// Generate a new game
async function generate()
{
  gameWon = false;
  localStorage.removeItem("queenGameSave");
  // Call generate function and wait for {size: N, regions: [[…],[…],…], solution: […]}
  const res = await fetch("/generate");
  gameData = await res.json();

  //console.log(gameData);

  // Initialize empty game board (no queens or notes placed)
  const size = gameData.size;
  boardState = Array(size).fill().map(() => Array(size).fill(0));
  noteState = Array(size).fill().map(() => Array(size).fill(0));

  // Draw the board
  draw();
  document.getElementById("status").textContent = "Place one queen in each region.";
}

// Reset variables when mouse is released
document.addEventListener("mouseup", () => {
  dragging = false;
  dragButton = null;
  lastToggledCell = null;
});

// Place and remove queens from the board
function toggleQueen(i, j)
{
  // Don't update if the game is already won
  if (gameWon) return;

  const regionId = gameData.regions[i][j];
  const size = gameData.size;

  // Queen already in cell, so remove it
  if (boardState[i][j] === 1)
  {
    boardState[i][j] = 0;
  }
  
  // Add a queen to the cell
  else
  {
    // Remove an existing queen in the same region
    for (let x = 0; x < size; x++)
    {
      for (let y = 0; y < size; y++)
      {
          if (gameData.regions[x][y] === regionId)
          {
            // Set all locations in the region to empty
            boardState[x][y] = 0;
          }
      }
    }

    // Place new queen
    boardState[i][j] = 1;
  }

  //console.log("boardState before check:", JSON.stringify(boardState));

  // Recheck the board for conflicts and winning
  checkBoard();
}

// Place and remove notes on the board
function toggleNote(i, j)
{
  // Don't update if hte game is already won
  if (gameWon) return;

  // Flip current value of cell and redraw board
  if (boardState[i][j] === 0)
  {
    noteState[i][j] ^= 1;
    draw();
  }
}

// Check board for conflicts and win condition
async function checkBoard()
{
  // Fetch check from back-end
  const res = await fetch("/check", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ size: gameData.size, board: boardState, regions: gameData.regions })
  });

  // Wait for back-end to process the check
  const { win, conflicts } = await res.json();

  // Game won
  if (win)
  {
    gameWon = true;
    document.getElementById("status").textContent = "🎉 Congratulations!";
  }
  
  // Conflicts found on board
  else if (conflicts.length)
  {
    document.getElementById("status").textContent = "Conflicts detected!";

    // Play buzzer if at least 3 queens in conflict or queens too far apart
    if (soundOn && (conflicts.length >= 3 || euclideanTooFar(conflicts)))
    {
      document.getElementById("buzzer").play();
    }
  }

  //console.log("conflicts from backend:", conflicts);

  // Redraw board with conflicts
  draw(conflicts);
}

// See if queens are too far
function euclideanTooFar(conflicts)
{
  const queens = [];

  // Find all queen locations on board
  for (let i = 0; i < boardState.length; i++)
  {
    for (let j = 0; j < boardState.length; j++)
    {
      if (boardState[i][j] === 1)
      {
        queens.push([i, j]);
      }
    }
  }

  // Set of conflicting coordinates
  const conflictSet = new Set(conflicts.map(([x, y]) => `${x},${y}`));

  // Check each pair of conflicting queens
  for (let a = 0; a < queens.length; a++)
  {
    const [x1, y1] = queens[a];
    for (let b = a + 1; b < queens.length; b++)
    {
      const [x2, y2] = queens[b];
      if (conflictSet.has(`${x1},${y1}`) && conflictSet.has(`${x2},${y2}`))
      {
        // Compute distance between queens
        const dx = (x1 + 0.5) - (x2 + 0.5);
        const dy = (y1 + 0.5) - (y2 + 0.5);
        const dist = Math.sqrt(dx * dx + dy * dy);
        // Play buzzer if queens at least 5 square apart
          // Player likely didn't see the issue and needs a reminder
        if (dist >= 5) return true;
      }
    }
  }

  // Don't trigger the buzzer
  return false;
}

// Show game solution
function showSolution()
{
  // No valid solution to show (shouldn't happen)
  if (!gameData || !gameData.solution) return;

  const size = gameData.size;
  boardState = Array(size).fill().map(() => Array(size).fill(0));

  // Loop through solution list and update board to match
  for (let row = 0; row < size; row++)
  {
    const col = gameData.solution[row];
    boardState[row][col] = 1;
  }

  // Lock the board and redraw
  gameWon = true;
  draw();
  document.getElementById("status").textContent = "Solution revealed.";
}

// Toggles the dropdown for difficulty
function toggleDropdown()
{
  const menu = document.getElementById("difficultyMenu");
  menu.style.display = (menu.style.display === "block") ? "none" : "block";
}

// Clost dropdown if a click is detected outside it
document.addEventListener("click", (e) => {
  const wrapper = document.querySelector(".dropdown-wrapper");
  const menu = document.getElementById("difficultyMenu");

  if (!wrapper.contains(e.target))
  {
      menu.style.display = "none";
  }
});

// Save the current board
async function save()
{
  // Call save function from back-end
  await fetch("/save", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ board: boardState, notes: noteState, regions: gameData.regions, size: gameData.size })
  });
  document.getElementById("status").textContent = "Game state saved.";
}

// Load the saved board (if applicable)
async function load()
{
  // Game can't be won if board is loaded
  gameWon = false;
  // Call load function from back-end
  const res = await fetch("/load");
  const data = await res.json();

  // No saved state available to be loaded
  if (data.error)
  {
    document.getElementById("status").textContent = "No saved state.";
    return;
  }

  // Update parameters to saved state and redraw board
  gameData = { size: data.size, regions: data.regions };
  boardState = data.board;
  noteState = data.notes;
  draw();
  document.getElementById("status").textContent = "Loaded saved state.";
}

// Disable/enable sound
function toggleSound()
{
  // Flip boolean to opposite
  soundOn = !soundOn;
  document.querySelector("button[onclick='toggleSound()']").textContent = `🔊 Sound: ${soundOn ? "ON" : "OFF"}`;
}

// Changes difficulty of game
async function setDifficulty(level)
{
  //console.log(level);

  await fetch(`/difficulty/${level}`);
  // Regenerate game board when difficulty altered
  generate();
}

// Save the current game state in local storage
function save() {
  const data =
  {
    // Current time (used for automatic deletion)
    timestamp: Date.now(),
    size: gameData.size,
    board: boardState,
    notes: noteState,
    regions: gameData.regions
  };
  localStorage.setItem("queenGameSave", JSON.stringify(data));
  document.getElementById("status").textContent = "Game state saved.";
}

// Load the game state from local storage
function load()
{
  const raw = localStorage.getItem("queenGameSave");

  // No save state to load
  if (!raw)
  {
    document.getElementById("status").textContent = "No saved state.";
    return;
  }

  // See if state is 30 minutes old
  const data = JSON.parse(raw);
  const age = Date.now() - data.timestamp;
  const maxAge = 30 * 60 * 1000;

  // Remove the game if it's over the max age
  if (age > maxAge)
  {
    localStorage.removeItem("queenGameSave");
    document.getElementById("status").textContent = "Saved game expired.";
    return;
  }

  // Valid save state so load it and redraw the board
  gameData = { size: data.size, regions: data.regions };
  boardState = data.board;
  noteState = data.notes;
  gameWon = false;
  draw();

  document.getElementById("status").textContent = "Loaded saved state.";
}

// Always generate a puzzle on load
generate();