import numpy as np
from typing import Optional, List, Tuple
import itertools

from sudoku_core import SudokuSolver, SudokuValidator

class BruteForceSolver(SudokuSolver):
    """Brute force solver that tries all combinations"""
    
    def __init__(self):
        super().__init__()
        self.name = "Brute Force Solver"
        self.description = "Tries all possible combinations (very slow, for demonstration)"
    
    def solve(self, grid: np.ndarray) -> Optional[np.ndarray]:
        """Solve using brute force approach"""
        working_grid = grid.copy()
        empty_cells = SudokuValidator.get_empty_cells(working_grid)
        
        if not empty_cells:
            return working_grid if SudokuValidator.is_valid_state(working_grid) else None
        
        # For demonstration, limit to small numbers of empty cells
        if len(empty_cells) > 20:
            # Fall back to backtracking for large puzzles
            return self._fallback_solve(working_grid)
        
        # Generate all possible combinations for empty cells
        for combination in itertools.product(range(1, 10), repeat=len(empty_cells)):
            test_grid = working_grid.copy()
            
            # Fill in the combination
            for i, (row, col) in enumerate(empty_cells):
                test_grid[row, col] = combination[i]
            
            # Check if this is a valid solution
            if SudokuValidator.is_valid_state(test_grid) and SudokuValidator.is_complete(test_grid):
                return test_grid
        
        return None
    
    def _fallback_solve(self, grid: np.ndarray) -> Optional[np.ndarray]:
        """Fallback to backtracking for large puzzles"""
        # Simple backtracking implementation
        empty_cell = self._find_empty_cell(grid)
        if empty_cell is None:
            return grid
        
        row, col = empty_cell
        
        for num in range(1, 10):
            if SudokuValidator.is_valid_placement(grid, row, col, num):
                grid[row, col] = num
                
                result = self._fallback_solve(grid)
                if result is not None:
                    return result
                
                grid[row, col] = 0
        
        return None
    
    def _find_empty_cell(self, grid: np.ndarray) -> Optional[Tuple[int, int]]:
        """Find first empty cell"""
        for row in range(9):
            for col in range(9):
                if grid[row, col] == 0:
                    return (row, col)
        return None

class LogicalSolver(SudokuSolver):
    """Solver using logical deduction techniques"""
    
    def __init__(self):
        super().__init__()
        self.name = "Logical Solver"
        self.description = "Uses naked singles and hidden singles techniques"
    
    def solve(self, grid: np.ndarray) -> Optional[np.ndarray]:
        """Solve using logical techniques"""
        working_grid = grid.copy()
        
        # Keep applying logical techniques until no more progress
        progress = True
        while progress:
            progress = False
            
            # Apply naked singles
            if self._apply_naked_singles(working_grid):
                progress = True
            
            # Apply hidden singles
            if self._apply_hidden_singles(working_grid):
                progress = True
            
            # Check if solved
            if SudokuValidator.is_complete(working_grid):
                return working_grid
        
        # If logical techniques aren't enough, fall back to backtracking
        return self._fallback_solve(working_grid)
    
    def _apply_naked_singles(self, grid: np.ndarray) -> bool:
        """Fill cells that have only one possible value"""
        progress = False
        
        for row in range(9):
            for col in range(9):
                if grid[row, col] == 0:
                    possible = SudokuValidator.get_possible_values(grid, row, col)
                    if len(possible) == 1:
                        grid[row, col] = possible[0]
                        progress = True
        
        return progress
    
    def _apply_hidden_singles(self, grid: np.ndarray) -> bool:
        """Fill cells where a number can only go in one place in a row/col/box"""
        progress = False
        
        # Check rows
        for row in range(9):
            for num in range(1, 10):
                possible_cols = []
                for col in range(9):
                    if grid[row, col] == 0 and SudokuValidator.is_valid_placement(grid, row, col, num):
                        possible_cols.append(col)
                
                if len(possible_cols) == 1:
                    grid[row, possible_cols[0]] = num
                    progress = True
        
        # Check columns
        for col in range(9):
            for num in range(1, 10):
                possible_rows = []
                for row in range(9):
                    if grid[row, col] == 0 and SudokuValidator.is_valid_placement(grid, row, col, num):
                        possible_rows.append(row)
                
                if len(possible_rows) == 1:
                    grid[possible_rows[0], col] = num
                    progress = True
        
        # Check 3x3 boxes
        for box_row in range(3):
            for box_col in range(3):
                for num in range(1, 10):
                    possible_cells = []
                    
                    for r in range(box_row * 3, (box_row + 1) * 3):
                        for c in range(box_col * 3, (box_col + 1) * 3):
                            if grid[r, c] == 0 and SudokuValidator.is_valid_placement(grid, r, c, num):
                                possible_cells.append((r, c))
                    
                    if len(possible_cells) == 1:
                        row, col = possible_cells[0]
                        grid[row, col] = num
                        progress = True
        
        return progress
    
    def _fallback_solve(self, grid: np.ndarray) -> Optional[np.ndarray]:
        """Fallback to backtracking"""
        empty_cell = self._find_empty_cell(grid)
        if empty_cell is None:
            return grid
        
        row, col = empty_cell
        
        for num in range(1, 10):
            if SudokuValidator.is_valid_placement(grid, row, col, num):
                grid[row, col] = num
                
                result = self._fallback_solve(grid)
                if result is not None:
                    return result
                
                grid[row, col] = 0
        
        return None
    
    def _find_empty_cell(self, grid: np.ndarray) -> Optional[Tuple[int, int]]:
        """Find first empty cell"""
        for row in range(9):
            for col in range(9):
                if grid[row, col] == 0:
                    return (row, col)
        return None
