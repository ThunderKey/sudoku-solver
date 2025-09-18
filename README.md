
# Sudoku Solver with Plugin System

An interactive Sudoku solver featuring a dynamic plugin system for custom solving algorithms.

## Features

- 🧩 Interactive Sudoku grid with validation
- 🔌 Plugin system for custom solver algorithms
- 📂 Load puzzles from JSON/text files
- 👀 Step-by-step solution visualization
- 📊 Performance metrics and timing
- 💾 Export solutions with metadata

## Built-in Solvers

- **Backtracking Solver**: Classic recursive backtracking
- **Smart Backtracking**: Enhanced with Most Constrained Variable heuristic
- **Brute Force Solver**: Simple iterative approach
- **Logical Solver**: Uses logical deduction techniques
- **Constraint Propagation**: Advanced constraint propagation with search

## Local Development Setup

### Using Poetry

If you have Poetry installed:

```bash
# Install dependencies
poetry install

# Run the application
python app.py
```

### Using pip

If you prefer pip:

```bash
# Install dependencies  
pip install numpy

# Run the application
python app.py
```

## Installing Nix and direnv

### Install Nix
```bash
# Single-user installation (recommended for most users)
sh <(curl -L https://nixos.org/nix/install) --no-daemon

# Multi-user installation (macOS/Linux with systemd)
sh <(curl -L https://nixos.org/nix/install) --daemon
```

### Install direnv
```bash
# On macOS with Homebrew
brew install direnv

# On Ubuntu/Debian
sudo apt install direnv

# On Arch Linux
sudo pacman -S direnv

# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
eval "$(direnv hook bash)"  # for bash
eval "$(direnv hook zsh)"   # for zsh
```

## Usage

### Running the App

1. Start the application:
   ```bash
   python app.py
   ```

2. The application will run as a command-line interface

### Loading Puzzles

**Manual Entry**: Click on grid cells to enter numbers directly

**File Upload**: Support for JSON and text formats

JSON format example:
```json
{
  "grid": [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    ...
  ]
}
```

Text format example:
```
5 3 0 0 7 0 0 0 0
6 0 0 1 9 5 0 0 0
0 9 8 0 0 0 0 6 0
...
```

### Solving Puzzles

1. Choose a solver algorithm from the dropdown
2. Enable "Show step-by-step solution" for detailed visualization
3. Click "🚀 Solve Puzzle"
4. Use Previous/Next buttons to navigate through solving steps

## Creating Custom Solvers

Create a new Python file in the `plugins/` directory:

```python
# plugins/my_solver.py
import numpy as np
from typing import Optional
from sudoku_core import SudokuSolver, SudokuValidator

class MySolver(SudokuSolver):
    def __init__(self):
        super().__init__()
        self.name = "My Custom Solver"
        self.description = "Description of my solver"
    
    def solve(self, grid: np.ndarray) -> Optional[np.ndarray]:
        # Implement your solving logic here
        working_grid = grid.copy()
        
        # Your algorithm here
        if self._my_solve_logic(working_grid):
            return working_grid
        return None
    
    def _my_solve_logic(self, grid: np.ndarray) -> bool:
        # Your solving implementation
        pass
```

The plugin will be automatically loaded on the next app restart.

## Project Structure

```
sudoku-solver/
├── app.py                    # Main application
├── sudoku_core.py           # Core Sudoku classes and validation
├── plugin_manager.py        # Plugin loading system
├── file_handler.py          # File I/O operations
├── solvers/                 # Built-in solver algorithms
│   ├── backtracking_solver.py
│   └── brute_force_solver.py
├── plugins/                 # Custom solver plugins
│   └── sample_solver.py
├── pyproject.toml          # Poetry configuration
└── README.md               # This file
```

## Development

### Code Style

Format code with:
```bash
poetry run black .
poetry run flake8 .
```

### Testing

Run tests with:
```bash
poetry run pytest
```

### Adding Dependencies

```bash
# Runtime dependencies
poetry add package-name

# Development dependencies
poetry add --group dev package-name
```

## Performance Tips

- **Smart Backtracking** is usually the fastest for most puzzles
- **Logical Solver** works well for easier puzzles
- **Constraint Propagation** is best for very difficult puzzles
- Use step-by-step mode only for learning/debugging (slower)

## Troubleshooting

### Common Issues

**Application issues**: Check the console output for error messages

**Solver not loading**: Check that your plugin file is in the `plugins/` directory and has no syntax errors

**File upload issues**: Ensure your puzzle file format matches the expected JSON/text structure

### Getting Help

1. Check the console output for error messages
2. Verify your puzzle format is correct
3. Try different solvers for comparison
4. Enable step-by-step mode to debug solving issues

## License

This project is open source. Feel free to contribute by adding new solver algorithms or improving the interface!
