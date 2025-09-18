import numpy as np
from typing import Optional, List, Tuple
import random

from sudoku_core import SudokuSolver, SudokuValidator

class RandomFillSolver(SudokuSolver):
    """Sample plugin that demonstrates the plugin system"""
    
    def __init__(self):
        super().__init__()
        self.name = "Random Fill Solver"
        self.description = "Randomly fills cells with valid values (demonstration only)"
    
    def solve(self, grid: np.ndarray) -> Optional[np.ndarray]:
        """Solve by randomly filling valid values"""
        working_grid = grid.copy()
        max_attempts = 1000
        
        for attempt in range(max_attempts):
            # Find empty cells
            empty_cells = SudokuValidator.get_empty_cells(working_grid)
            
            if not empty_cells:
                # Check if we have a valid solution
                if SudokuValidator.is_complete(working_grid):
                    return working_grid
                else:
                    # Invalid state, restart
                    working_grid = grid.copy()
                    continue
            
            # Pick a random empty cell
            row, col = random.choice(empty_cells)
            
            # Get possible values for this cell
            possible_values = SudokuValidator.get_possible_values(working_grid, row, col)
            
            if possible_values:
                # Randomly choose a valid value
                value = random.choice(possible_values)
                working_grid[row, col] = value
            else:
                # No valid values, restart
                working_grid = grid.copy()
        
        # If we couldn't solve randomly, fall back to backtracking
        return self._backtrack_solve(grid.copy())
    
    def solve_with_steps(self, grid: np.ndarray) -> Tuple[Optional[np.ndarray], List[dict]]:
        """Solve with step tracking"""
        steps = []
        working_grid = grid.copy()
        
        steps.append({
            'grid': working_grid.copy(),
            'description': 'Starting random fill solver',
            'move': None,
            'action': 'start'
        })
        
        max_attempts = 100  # Fewer attempts for step tracking
        
        for attempt in range(max_attempts):
            empty_cells = SudokuValidator.get_empty_cells(working_grid)
            
            if not empty_cells:
                if SudokuValidator.is_complete(working_grid):
                    steps.append({
                        'grid': working_grid.copy(),
                        'description': 'Puzzle solved with random filling!',
                        'move': None,
                        'action': 'complete'
                    })
                    return working_grid, steps
                else:
                    working_grid = grid.copy()
                    steps.append({
                        'grid': working_grid.copy(),
                        'description': 'Invalid state reached, restarting...',
                        'move': None,
                        'action': 'restart'
                    })
                    continue
            
            # Pick a random empty cell
            row, col = random.choice(empty_cells)
            possible_values = SudokuValidator.get_possible_values(working_grid, row, col)
            
            if possible_values:
                value = random.choice(possible_values)
                working_grid[row, col] = value
                
                steps.append({
                    'grid': working_grid.copy(),
                    'description': f'Randomly placed {value} at ({row+1}, {col+1})',
                    'move': {'row': row, 'col': col, 'value': value},
                    'action': 'place'
                })
            else:
                working_grid = grid.copy()
                steps.append({
                    'grid': working_grid.copy(),
                    'description': 'No valid moves, restarting...',
                    'move': None,
                    'action': 'restart'
                })
        
        # Fall back to backtracking
        result = self._backtrack_solve(grid.copy())
        if result is not None:
            steps.append({
                'grid': result.copy(),
                'description': 'Random approach failed, solved with backtracking',
                'move': None,
                'action': 'fallback'
            })
        
        return result, steps
    
    def _backtrack_solve(self, grid: np.ndarray) -> Optional[np.ndarray]:
        """Simple backtracking fallback"""
        empty_cell = self._find_empty_cell(grid)
        if empty_cell is None:
            return grid
        
        row, col = empty_cell
        
        for num in range(1, 10):
            if SudokuValidator.is_valid_placement(grid, row, col, num):
                grid[row, col] = num
                
                result = self._backtrack_solve(grid)
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

class ConstraintPropagationSolver(SudokuSolver):
    """Advanced solver using constraint propagation"""
    
    def __init__(self):
        super().__init__()
        self.name = "Constraint Propagation"
        self.description = "Uses constraint propagation with search"
    
    def solve(self, grid: np.ndarray) -> Optional[np.ndarray]:
        """Solve using constraint propagation"""
        # Initialize possibility sets for each cell
        possibilities = self._initialize_possibilities(grid)
        
        # Apply constraint propagation
        if not self._propagate_constraints(grid, possibilities):
            return None
        
        # If not solved, use search with propagation
        return self._search_with_propagation(grid, possibilities)
    
    def _initialize_possibilities(self, grid: np.ndarray) -> List[List[set]]:
        """Initialize possibility sets for each cell"""
        possibilities = [[set() for _ in range(9)] for _ in range(9)]
        
        for row in range(9):
            for col in range(9):
                if grid[row, col] == 0:
                    possibilities[row][col] = set(SudokuValidator.get_possible_values(grid, row, col))
                else:
                    possibilities[row][col] = {grid[row, col]}
        
        return possibilities
    
    def _propagate_constraints(self, grid: np.ndarray, possibilities: List[List[set]]) -> bool:
        """Apply constraint propagation"""
        changed = True
        
        while changed:
            changed = False
            
            # Apply naked singles
            for row in range(9):
                for col in range(9):
                    if grid[row, col] == 0 and len(possibilities[row][col]) == 1:
                        value = list(possibilities[row][col])[0]
                        grid[row, col] = value
                        
                        # Remove this value from peers
                        if self._eliminate_from_peers(possibilities, row, col, value):
                            changed = True
                        else:
                            return False
            
            # Apply hidden singles
            if self._apply_hidden_singles_propagation(grid, possibilities):
                changed = True
        
        return True
    
    def _eliminate_from_peers(self, possibilities: List[List[set]], row: int, col: int, value: int) -> bool:
        """Eliminate value from all peers of the cell"""
        # Row peers
        for c in range(9):
            if c != col and value in possibilities[row][c]:
                possibilities[row][c].remove(value)
                if len(possibilities[row][c]) == 0:
                    return False
        
        # Column peers
        for r in range(9):
            if r != row and value in possibilities[r][col]:
                possibilities[r][col].remove(value)
                if len(possibilities[r][col]) == 0:
                    return False
        
        # Box peers
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if (r != row or c != col) and value in possibilities[r][c]:
                    possibilities[r][c].remove(value)
                    if len(possibilities[r][c]) == 0:
                        return False
        
        return True
    
    def _apply_hidden_singles_propagation(self, grid: np.ndarray, possibilities: List[List[set]]) -> bool:
        """Apply hidden singles with propagation"""
        changed = False
        
        # Check rows, columns, and boxes for hidden singles
        # Implementation similar to LogicalSolver but with possibility sets
        # This is a simplified version
        
        return changed
    
    def _search_with_propagation(self, grid: np.ndarray, possibilities: List[List[set]]) -> Optional[np.ndarray]:
        """Search with constraint propagation"""
        # Find cell with minimum possibilities
        min_possibilities = 10
        best_cell = None
        
        for row in range(9):
            for col in range(9):
                if grid[row, col] == 0 and len(possibilities[row][col]) < min_possibilities:
                    min_possibilities = len(possibilities[row][col])
                    best_cell = (row, col)
        
        if best_cell is None:
            return grid  # Solved
        
        row, col = best_cell
        
        for value in list(possibilities[row][col]):
            # Make a copy and try this value
            test_grid = grid.copy()
            test_possibilities = [row[:] for row in possibilities]
            
            test_grid[row, col] = value
            test_possibilities[row][col] = {value}
            
            if self._eliminate_from_peers(test_possibilities, row, col, value):
                if self._propagate_constraints(test_grid, test_possibilities):
                    result = self._search_with_propagation(test_grid, test_possibilities)
                    if result is not None:
                        return result
        
        return None
