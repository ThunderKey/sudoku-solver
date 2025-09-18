
# Sudoku Solver - Full Stack Application

A modern, full-stack Sudoku solver featuring a Vue.js frontend with FastAPI backend and a dynamic plugin system for custom solving algorithms.

## Architecture

- **Frontend**: Vue.js 3 with TypeScript, PrimeVue UI components, and Pinia state management
- **Backend**: FastAPI with automatic API documentation and CORS support
- **Plugin System**: Dynamic solver loading for custom algorithms
- **Development**: Nix flake environment with Poetry dependency management

## Features

- 🧩 Interactive Sudoku grid with real-time validation
- 🔌 Plugin system for custom solver algorithms
- 📂 Load puzzles from JSON/text files
- 👀 Step-by-step solution visualization with navigation
- 📊 Performance metrics and timing
- 💾 Export solutions with metadata
- 🌐 Modern web interface with responsive design
- 🚀 REST API for programmatic access

## Built-in Solvers

- **Backtracking Solver**: Classic recursive backtracking
- **Smart Backtracking**: Enhanced with Most Constrained Variable heuristic
- **Brute Force Solver**: Simple iterative approach
- **Logical Solver**: Uses logical deduction techniques
- **Constraint Propagation**: Advanced constraint propagation with search
- **Random Fill Solver**: Demonstration solver with random placement

## Development Setup

### Prerequisites

This project uses Nix flakes for reproducible development environments. If you don't have Nix installed:

```bash
# Install Nix
sh <(curl -L https://nixos.org/nix/install) --daemon

# Enable flakes (add to ~/.config/nix/nix.conf)
experimental-features = nix-command flakes
```

### Quick Start

```bash
# Enter development environment
nix develop

# Install dependencies
poetry install
npm install

# Start the application (runs both frontend and backend)
# Click the "Run" button in Replit or use:
# Frontend: node_modules/.bin/vite frontend --host 0.0.0.0 --port 5000
# Backend: python -m uvicorn backend:app --host 0.0.0.0 --port 8000 --reload
```

The application will be available at:
- **Frontend**: http://localhost:5000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Usage

### Web Interface

1. Open the application in your browser
2. Use the interactive grid to enter puzzle values
3. Load puzzles via file upload or use the sample puzzle
4. Select a solver algorithm and click "Solve"
5. Navigate through solution steps using the step controls

### Loading Puzzles

**File Upload**: Supports JSON and text formats

JSON format:
```json
{
  "grid": [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    ...
  ]
}
```

Text format:
```
5 3 0 0 7 0 0 0 0
6 0 0 1 9 5 0 0 0
0 9 8 0 0 0 0 6 0
...
```

### API Usage

The FastAPI backend provides a complete REST API:

```bash
# Get current grid state
curl http://localhost:8000/grid

# Update a cell
curl -X POST http://localhost:8000/grid/cell \
  -H "Content-Type: application/json" \
  -d '{"row": 0, "col": 2, "value": 7}'

# Solve puzzle
curl -X POST http://localhost:8000/solve \
  -H "Content-Type: application/json" \
  -d '{"solver_name": "Backtracking Solver", "show_steps": true}'

# Get available solvers
curl http://localhost:8000/solvers
```

## Creating Custom Solvers

Create a new Python file in the `plugins/` directory:

```python
# plugins/my_solver.py
import numpy as np
from typing import Optional, List, Tuple
from sudoku_core import SudokuSolver, SudokuValidator

class MySolver(SudokuSolver):
    def __init__(self):
        super().__init__()
        self.name = "My Custom Solver"
        self.description = "Description of my solving algorithm"
    
    def solve(self, grid: np.ndarray) -> Optional[np.ndarray]:
        """Solve the puzzle and return solution grid"""
        working_grid = grid.copy()
        
        # Implement your solving logic here
        if self._my_solve_logic(working_grid):
            return working_grid
        return None
    
    def solve_with_steps(self, grid: np.ndarray) -> Tuple[Optional[np.ndarray], List[dict]]:
        """Solve with step tracking for visualization"""
        steps = []
        working_grid = grid.copy()
        
        # Track each step for the UI
        steps.append({
            'grid': working_grid.copy(),
            'description': 'Starting custom solver',
            'move': None,
            'action': 'start'
        })
        
        # Your step-by-step solving logic here
        # Each step should append to the steps list
        
        return working_grid, steps
    
    def _my_solve_logic(self, grid: np.ndarray) -> bool:
        # Your solving implementation
        pass
```

The plugin will be automatically loaded when the backend starts. Use the `/plugins/reload` endpoint to reload plugins during development.

## Project Structure

```
sudoku-solver/
├── frontend/                 # Vue.js frontend application
│   ├── src/
│   │   ├── components/       # Vue components
│   │   ├── stores/          # Pinia state management
│   │   ├── views/           # Route views
│   │   └── main.ts         # App entry point
│   ├── package.json        # Frontend dependencies
│   └── vite.config.ts      # Vite configuration
├── backend.py              # FastAPI server and API endpoints
├── model.py                # Business logic and state management
├── sudoku_core.py          # Core Sudoku classes and validation
├── plugin_manager.py       # Plugin loading system
├── file_handler.py         # File I/O operations
├── solvers/                # Built-in solver algorithms
│   ├── backtracking_solver.py
│   └── brute_force_solver.py
├── plugins/                # Custom solver plugins
│   └── sample_solver.py
├── flake.nix               # Nix development environment
├── pyproject.toml          # Python dependencies (Poetry)
└── package.json            # Node.js dependencies
```

## API Endpoints

### Grid Management
- `GET /grid` - Get current grid state
- `POST /grid/cell` - Update single cell
- `POST /grid/load` - Upload puzzle file
- `GET /grid/sample` - Load sample puzzle
- `POST /grid/clear` - Clear grid
- `GET /grid/save` - Download current puzzle

### Solving
- `GET /solvers` - List available solvers
- `POST /solve` - Solve puzzle with specified solver
- `GET /solution` - Get solution step information
- `POST /solution/next` - Navigate to next step
- `POST /solution/prev` - Navigate to previous step
- `POST /solution/jump` - Jump to specific step

### System
- `GET /health` - Health check
- `POST /plugins/reload` - Reload solver plugins
- `GET /performance` - Get performance metrics

## Development

### Frontend Development

```bash
# Start frontend dev server
cd frontend
npm run dev

# Build for production
npm run build

# Lint code
npm run lint
```

### Backend Development

```bash
# Start backend with auto-reload
python -m uvicorn backend:app --reload --host 0.0.0.0 --port 8000

# Run with debugging
python -m uvicorn backend:app --reload --log-level debug
```

### Adding Dependencies

```bash
# Python dependencies
poetry add package-name

# Node.js dependencies
cd frontend && npm install package-name
```

## Performance Tips

- **Smart Backtracking** is usually fastest for most puzzles
- **Logical Solver** works well for easier puzzles  
- **Constraint Propagation** is best for very difficult puzzles
- Use step-by-step mode for learning (impacts performance)
- The API supports both direct solving and step-by-step visualization

## Deployment on Replit

This project is configured for Replit with:
- Automatic environment setup via Nix flakes
- Parallel workflow running frontend and backend
- Port forwarding (5000 → 80/443, 8000 internal)
- Hot reload for development

## Troubleshooting

### Common Issues

**WebSocket connection errors**: Normal when switching between steps rapidly, connections will reconnect automatically

**Plugin not loading**: Check console output for syntax errors, ensure plugin file is in `plugins/` directory

**CORS errors**: Backend is configured for common frontend ports, check `backend.py` CORS settings if using different ports

**File upload issues**: Ensure puzzle format matches expected JSON/text structure

### Development Tips

1. Use browser dev tools to inspect API calls
2. Check backend console for detailed error messages  
3. Use `/docs` endpoint for interactive API testing
4. Enable step-by-step mode to debug solver behavior

## License

This project is open source. Feel free to contribute by adding new solver algorithms, improving the UI, or enhancing the API!
