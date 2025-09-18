import numpy as np
from typing import Optional, List, Tuple

class SudokuGrid:
    """Core Sudoku grid operations and utilities"""
    
    def __init__(self, grid: Optional[np.ndarray] = None):
        if grid is not None:
            self.grid = grid.copy()
        else:
            self.grid = np.zeros((9, 9), dtype=int)
    
    def get_grid(self) -> np.ndarray:
        """Get a copy of the current grid"""
        return self.grid.copy()
    
    def set_cell(self, row: int, col: int, value: int) -> bool:
        """Set a cell value if valid"""
        if 0 <= row < 9 and 0 <= col < 9 and 0 <= value <= 9:
            self.grid[row, col] = value
            return True
        return False
    
    def get_cell(self, row: int, col: int) -> int:
        """Get cell value"""
        if 0 <= row < 9 and 0 <= col < 9:
            return self.grid[row, col]
        return -1
    
    def clear(self):
        """Clear the entire grid"""
        self.grid = np.zeros((9, 9), dtype=int)
    
    def copy(self):
        """Create a copy of this grid"""
        return SudokuGrid(self.grid)

class SudokuValidator:
    """Sudoku puzzle validation utilities"""
    
    @staticmethod
    def is_valid_placement(grid: np.ndarray, row: int, col: int, num: int) -> bool:
        """Check if placing num at (row, col) is valid"""
        # Check row
        for c in range(9):
            if c != col and grid[row, c] == num:
                return False
        
        # Check column
        for r in range(9):
            if r != row and grid[r, col] == num:
                return False
        
        # Check 3x3 box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if (r != row or c != col) and grid[r, c] == num:
                    return False
        
        return True
    
    @staticmethod
    def is_valid_state(grid: np.ndarray) -> bool:
        """Check if the current grid state is valid"""
        for row in range(9):
            for col in range(9):
                if grid[row, col] != 0:
                    # Temporarily remove the number and check if it's valid to place
                    temp = grid[row, col]
                    grid[row, col] = 0
                    valid = SudokuValidator.is_valid_placement(grid, row, col, temp)
                    grid[row, col] = temp
                    if not valid:
                        return False
        return True
    
    @staticmethod
    def is_complete(grid: np.ndarray) -> bool:
        """Check if the puzzle is completely solved"""
        return np.all(grid != 0) and SudokuValidator.is_valid_state(grid)
    
    @staticmethod
    def get_empty_cells(grid: np.ndarray) -> List[Tuple[int, int]]:
        """Get list of empty cell coordinates"""
        empty_cells = []
        for row in range(9):
            for col in range(9):
                if grid[row, col] == 0:
                    empty_cells.append((row, col))
        return empty_cells
    
    @staticmethod
    def get_possible_values(grid: np.ndarray, row: int, col: int) -> List[int]:
        """Get list of possible values for a cell"""
        if grid[row, col] != 0:
            return []
        
        possible = []
        for num in range(1, 10):
            if SudokuValidator.is_valid_placement(grid, row, col, num):
                possible.append(num)
        return possible

class SudokuSolver:
    """Base class for Sudoku solvers"""
    
    def __init__(self):
        self.name = "Base Solver"
        self.description = "Base solver class"
    
    def solve(self, grid: np.ndarray) -> Optional[np.ndarray]:
        """Solve the puzzle and return solution grid"""
        raise NotImplementedError("Subclasses must implement solve method")
    
    def solve_with_steps(self, grid: np.ndarray) -> Tuple[Optional[np.ndarray], List[dict]]:
        """Solve with step-by-step tracking"""
        # Default implementation just calls solve
        solution = self.solve(grid)
        steps = []
        if solution is not None:
            steps.append({
                'grid': solution,
                'description': 'Final solution',
                'move': None
            })
        return solution, steps
