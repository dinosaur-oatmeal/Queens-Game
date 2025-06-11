# Queen Puzzle Game

A web-based puzzle game where you place queens on a colored, region-based board so that no two queens attack each other. Each puzzle has a unique solution, and you can take notes, save your progress, and adjust difficulty.

### Visit the website [here](https://games.willmaberry.com/)

## Features

* **Unique-board generation**: Board regions generated server-side using a flood-fill algorithm seeded by a valid queen solution, then "carved" to ensure there's exactly one solution.
* **Interactive SVG board**: Drag, click, and right-click to place queens (♕) and notes (X) in cells.
* **Quality-of-life**:

  * Note-taking on cells to pencil-mark possibilities.
  * Save and load your game state locally (expires after 30 minutes).
  * Difficulty levels (Easy, Medium, Hard) control board size range.
  * Toggle sound effects for conflict buzzer.
  * Reveal solution when stuck.
* **Robust API**: Built with FastAPI and Pydantic for strict request/response models and input validation.
* **Docker-ready**: Containerize with Docker for easy deployment now or in the future.

## Tech Stack

* **Back-end**: Python, FastAPI, Pydantic, custom logic modules (`logic.py`) for puzzle generation and validation.
* **Front-end**: Vanilla JavaScript, SVG for board rendering, HTML/CSS.
* **Persistence**: Browser `localStorage` for save/load.
* **Containerization**: Docker.

## Getting Started

### Prerequisites

* Docker

### Build and Run with Docker

1. Build the Docker image:

   ```bash
   docker build -t queen-puzzle:latest .
   ```

2. Run the container:

   ```bash
   docker run -d --name queen-puzzle -p 8000:8000 queen-puzzle:latest
   ```

3. Open your browser at `http://localhost:8000`.

## Project Structure

```
├── Dockerfile
├── logic.py            # Core puzzle generation and validation logic
├── main.py             # FastAPI application
├── static/             # Front-end assets
│   ├── index.html
│   ├── style.css
│   ├── game.js
│   └── buzzer.mp3
└── README.md
```

## API Reference

### `GET /generate`

Generate a new puzzle.

**Response** (`GenerateResponse`):

```json
{
  "size": 8,
  "solution": [3, 1, 6, 4, 0, 7, 5, 2],
  "regions": [[...], [...], ...]
}
```

* `size`: board dimension (4 – 10).
* `solution`: column index per row for the unique solution.
* `regions`: 2D matrix assigning each cell a region ID.

### `POST /check`

Validate current board state.

**Request** (`CheckRequest`):

```json
{
  "size": 8,
  "board": [[0,1,0,...], ...],
  "regions": [[...], ...]
}
```

**Response** (`CheckResponse`):

```json
{
  "win": false,
  "conflicts": [[0,1], [2,5], ...]
}
```

* `win`: `true` if exactly one queen in each region and no attacks.
* `conflicts`: list of `[row, col]` pairs that violate rules.

### `GET /difficulty/{level}`

Set puzzle difficulty:

* `easy`: sizes 4–6
* `medium`: sizes 7–8
* `hard`: sizes 9–10

## Input Validation & Security

All API payloads are validated with Pydantic models enforcing:

* Matrix dimensions (`size × size`).
* Cell values (`0` or `1` for board/notes).
* Region IDs are non-negative integers.

Invalid or malformed requests return HTTP 422 errors.

## Front-end Overview

* **SVG Board Rendering**: JavaScript builds an `N × N` grid of `<rect>` elements colored by regions.
* **Event Handling**:

  * **Left-click**: Place or remove a queen in a region, ensuring one queen per region.
  * **Right-click drag**: Pencil X-marks for notes.
  * **Controls**: New game, save, load, difficulty menu, sound toggle, show solution.
* **Game Status**: Displays conflicts or victory message.
