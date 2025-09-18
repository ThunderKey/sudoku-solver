import numpy as np
from typing import Optional, List, Tuple
import copy

from sudoku_core import SudokuSolver, SudokuValidator

class BacktrackingSolver(SudokuSolver):
    """Classic backtracking solver with step-by-step capability"""
    
    def __init__(self):
        super().__init__()
        self.name = "Backtracking Solver"
        self.description = "Classic recursive backtracking algorithm"
        self.steps = []
    
    def solve(self, grid: np.ndarray) -> Optional[np.ndarray]:
        """Solve using backtracking algorithm"""
        working_grid = grid.copy()
        
        if self._solve_recursive(working_grid):
            return working_grid
        return None
    
    def solve_with_steps(self, grid: np.ndarray) -> Tuple[Optional[np.ndarray], List[dict]]:
        """Solve with detailed step tracking"""
        self.steps = []
        working_grid = grid.copy()
        
        # Add initial state
        self.steps.append({
            'grid': working_grid.copy(),
            'description': 'Initial puzzle state',
            'move': None,
            'action': 'start'
        })
        
        if self._solve_with_tracking(working_grid):
            return working_grid, self.steps
        return None, self.steps
    
    def _solve_recursive(self, grid: np.ndarray) -> bool:
        """Recursive backtracking solver"""
        # Find empty cell
        empty_cell = self._find_empty_cell(grid)
        if empty_cell is None:
            return True  # Puzzle solved
        
        row, col = empty_cell
        
        # Try numbers 1-9
        for num in range(1, 10):
            if SudokuValidator.is_valid_placement(grid, row, col, num):
                grid[row, col] = num
                
                if self._solve_recursive(grid):
                    return True
                
                # Backtrack
                grid[row, col] = 0
        
        return False
    
    def _solve_with_tracking(self, grid: np.ndarray) -> bool:
        """Recursive solver with step tracking"""
        # Find empty cell
        empty_cell = self._find_empty_cell(grid)
        if empty_cell is None:
            self.steps.append({
                'grid': grid.copy(),
                'description': 'Puzzle solved!',
                'move': None,
                'action': 'complete'
            })
            return True
        
        row, col = empty_cell
        
        # Try numbers 1-9
        for num in range(1, 10):
            if SudokuValidator.is_valid_placement(grid, row, col, num):
                grid[row, col] = num
                
                # Add step for placement
                self.steps.append({
                    'grid': grid.copy(),
                    'description': f'Try placing {num} at position ({row+1}, {col+1})',
                    'move': {'row': row, 'col': col, 'value': num},
                    'action': 'place'
                })
                
                if self._solve_with_tracking(grid):
                    return True
                
                # Backtrack
                grid[row, col] = 0
                self.steps.append({
                    'grid': grid.copy(),
                    'description': f'Backtrack: Remove {num} from ({row+1}, {col+1})',
                    'move': {'row': row, 'col': col, 'value': 0},
                    'action': 'backtrack'
                })
        
        return False
    
    def _find_empty_cell(self, grid: np.ndarray) -> Optional[Tuple[int, int]]:
        """Find the first empty cell (0) in the grid"""
        for row in range(9):
            for col in range(9):
                if grid[row, col] == 0:
                    return (row, col)
        return None

class SmartBacktrackingSolver(SudokuSolver):
    """Enhanced backtracking with Most Constrained Variable heuristic"""
    
    def __init__(self):
        super().__init__()
        self.name = "Smart Backtracking"
        self.description = "Backtracking with MCV heuristic for better performance"
    
    def solve(self, grid: np.ndarray) -> Optional[np.ndarray]:
        """Solve using smart backtracking"""
        working_grid = grid.copy()
        
        if self._solve_smart(working_grid):
            return working_grid
        return None
    
    def _solve_smart(self, grid: np.ndarray) -> bool:
        """Smart backtracking with MCV heuristic"""
        # Find the empty cell with the fewest possibilities
        best_cell = self._find_most_constrained_cell(grid)
        if best_cell is None:
            return True  # Puzzle solved
        
        row, col = best_cell
        possible_values = SudokuValidator.get_possible_values(grid, row, col)
        
        # Try each possible value
        for num in possible_values:
            grid[row, col] = num
            
            if self._solve_smart(grid):
                return True
            
            # Backtrack
            grid[row, col] = 0
        
        return False
    
    def _find_most_constrained_cell(self, grid: np.ndarray) -> Optional[Tuple[int, int]]:
        """Find empty cell with fewest possible values"""
        min_possibilities = 10
        best_cell = None
        
        for row in range(9):
            for col in range(9):
                if grid[row, col] == 0:
                    possibilities = len(SudokuValidator.get_possible_values(grid, row, col))
                    if possibilities < min_possibilities:
                        min_possibilities = possibilities
                        best_cell = (row, col)
                        
                        # If we find a cell with only one possibility, use it immediately
                        if min_possibilities == 1:
                            return best_cell
        
        return best_cell
