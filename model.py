import numpy as np
from typing import Optional, List, Tuple, Dict, Any
from enum import Enum
from dataclasses import dataclass, field
import copy


class CellType(Enum):
    """Enumeration for different cell types"""
    EMPTY = "empty"
    GIVEN = "given"    # Original puzzle values
    SOLVED = "solved"  # User or solver filled values


@dataclass
class Cell:
    """Represents a single Sudoku cell"""
    value: int = 0
    cell_type: CellType = CellType.EMPTY
    possible_values: List[int] = field(default_factory=list)
    
    def is_empty(self) -> bool:
        return self.value == 0
    
    def is_given(self) -> bool:
        return self.cell_type == CellType.GIVEN


@dataclass
class SolutionStep:
    """Represents a step in the solution process"""
    grid: np.ndarray
    description: str
    move: Optional[Tuple[int, int, int]] = None  # (row, col, value)
    action: str = 'step'
    
    def to_dict(self) -> dict:
        """Convert to dictionary format for backwards compatibility"""
        return {
            'grid': self.grid.copy(),
            'description': self.description,
            'move': self.move,
            'action': self.action
        }


class SudokuGrid:
    """Enhanced core Sudoku grid with better state management"""
    
    def __init__(self, grid: Optional[np.ndarray] = None):
        if grid is not None:
            self.grid = grid.copy()
        else:
            self.grid = np.zeros((9, 9), dtype=int)
        
        # Track which cells are given (original puzzle values)
        self.given_cells = np.zeros((9, 9), dtype=bool)
        self._mark_given_cells()
    
    def _mark_given_cells(self):
        """Mark non-zero cells as given cells"""
        self.given_cells = self.grid != 0
    
    def set_grid(self, new_grid: np.ndarray, mark_as_given: bool = True):
        """Set a new grid and optionally mark non-zero cells as given"""
        self.grid = new_grid.copy()
        if mark_as_given:
            self.given_cells = new_grid != 0
    
    def get_grid(self) -> np.ndarray:
        """Get a copy of the current grid"""
        return self.grid.copy()
    
    def set_cell(self, row: int, col: int, value: int) -> bool:
        """Set a cell value if valid and not a given cell"""
        if not (0 <= row < 9 and 0 <= col < 9 and 0 <= value <= 9):
            return False
        
        if self.given_cells[row, col]:
            return False  # Cannot modify given cells
        
        self.grid[row, col] = value
        return True
    
    def get_cell(self, row: int, col: int) -> int:
        """Get cell value"""
        if 0 <= row < 9 and 0 <= col < 9:
            return self.grid[row, col]
        return -1
    
    def is_given_cell(self, row: int, col: int) -> bool:
        """Check if a cell is a given (original) cell"""
        if 0 <= row < 9 and 0 <= col < 9:
            return self.given_cells[row, col]
        return False
    
    def clear(self, keep_given: bool = True):
        """Clear the grid, optionally keeping given cells"""
        if keep_given:
            # Only clear non-given cells
            self.grid[~self.given_cells] = 0
        else:
            # Clear everything
            self.grid = np.zeros((9, 9), dtype=int)
            self.given_cells = np.zeros((9, 9), dtype=bool)
    
    def copy(self):
        """Create a deep copy of this grid"""
        new_grid = SudokuGrid(self.grid)
        new_grid.given_cells = self.given_cells.copy()
        return new_grid
    
    def get_grid_info(self) -> Dict[str, Any]:
        """Get comprehensive information about the grid"""
        return {
            'grid': self.get_grid(),
            'given_cells': self.given_cells.copy(),
            'empty_count': np.sum(self.grid == 0),
            'filled_count': np.sum(self.grid != 0),
            'given_count': np.sum(self.given_cells)
        }


class SudokuValidator:
    """Enhanced Sudoku puzzle validation utilities"""
    
    @staticmethod
    def is_valid_placement(grid: np.ndarray, row: int, col: int, num: int) -> bool:
        """Check if placing num at (row, col) is valid"""
        if num == 0:  # Empty cell is always valid
            return True
        
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
        return bool(np.all(grid != 0)) and SudokuValidator.is_valid_state(grid)
    
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
    
    @staticmethod
    def get_conflicts(grid: np.ndarray) -> List[Tuple[int, int, List[Tuple[int, int]]]]:
        """Get all conflicts in the grid as (row, col, conflicting_cells)"""
        conflicts = []
        
        for row in range(9):
            for col in range(9):
                if grid[row, col] != 0:
                    conflicting_cells = []
                    num = grid[row, col]
                    
                    # Check row conflicts
                    for c in range(9):
                        if c != col and grid[row, c] == num:
                            conflicting_cells.append((row, c))
                    
                    # Check column conflicts
                    for r in range(9):
                        if r != row and grid[r, col] == num:
                            conflicting_cells.append((r, col))
                    
                    # Check 3x3 box conflicts
                    box_row, box_col = 3 * (row // 3), 3 * (col // 3)
                    for r in range(box_row, box_row + 3):
                        for c in range(box_col, box_col + 3):
                            if (r != row or c != col) and grid[r, c] == num:
                                if (r, c) not in conflicting_cells:
                                    conflicting_cells.append((r, c))
                    
                    if conflicting_cells:
                        conflicts.append((row, col, conflicting_cells))
        
        return conflicts


class SudokuModel:
    """Main model class that manages the complete Sudoku puzzle state"""
    
    def __init__(self):
        self.current_grid = SudokuGrid()
        self.original_grid = SudokuGrid()
        self.validator = SudokuValidator()
        
        # Solution state
        self.solution_steps: List[SolutionStep] = []
        self.current_step = 0
        self.is_solving = False
        
        # Metrics
        self.last_solve_time: Optional[float] = None
        self.step_count: Optional[int] = None
        
        # Version for UI updates
        self.version = 0
    
    def load_puzzle(self, grid: np.ndarray):
        """Load a new puzzle"""
        self.current_grid.set_grid(grid, mark_as_given=True)
        self.original_grid.set_grid(grid, mark_as_given=True)
        self.clear_solution_state()
        self._increment_version()
    
    def clear_puzzle(self, keep_given: bool = False):
        """Clear the puzzle"""
        if keep_given:
            self.current_grid.clear(keep_given=True)
        else:
            self.current_grid.clear(keep_given=False)
            self.original_grid.clear(keep_given=False)
        self.clear_solution_state()
        self._increment_version()
    
    def update_cell(self, row: int, col: int, value: int) -> bool:
        """Update a cell value"""
        success = self.current_grid.set_cell(row, col, value)
        if success:
            self._increment_version()
        return success
    
    def get_cell_value(self, row: int, col: int) -> int:
        """Get a cell value"""
        return self.current_grid.get_cell(row, col)
    
    def is_given_cell(self, row: int, col: int) -> bool:
        """Check if a cell is from the original puzzle"""
        return self.current_grid.is_given_cell(row, col)
    
    def get_grid_state(self) -> Dict[str, Any]:
        """Get comprehensive grid state information"""
        grid = self.current_grid.get_grid()
        is_empty = np.array_equal(grid, np.zeros((9, 9)))
        
        return {
            'grid': grid,
            'original_grid': self.original_grid.get_grid(),
            'given_cells': self.current_grid.given_cells.copy(),
            'is_empty': is_empty,
            'is_valid': self.validator.is_valid_state(grid) if not is_empty else True,
            'is_complete': self.validator.is_complete(grid) if not is_empty else False,
            'empty_count': np.sum(grid == 0),
            'filled_count': np.sum(grid != 0),
            'conflicts': self.validator.get_conflicts(grid) if not is_empty else [],
            'version': self.version
        }
    
    def set_solution_steps(self, steps: List[dict], solve_time: float):
        """Set solution steps from solver"""
        # Convert dict steps to SolutionStep objects
        self.solution_steps = [
            SolutionStep(
                grid=step['grid'].copy(),
                description=step['description'],
                move=step.get('move'),
                action=step.get('action', 'step')
            ) for step in steps
        ]
        self.current_step = 0
        self.last_solve_time = solve_time
        self.step_count = len(steps)
    
    def clear_solution_state(self):
        """Clear all solution-related state"""
        self.solution_steps = []
        self.current_step = 0
        self.is_solving = False
        self.last_solve_time = None
        self.step_count = None
    
    def navigate_to_step(self, step_index: int) -> bool:
        """Navigate to a specific solution step"""
        if 0 <= step_index < len(self.solution_steps):
            self.current_step = step_index
            step = self.solution_steps[step_index]
            self.current_grid.set_grid(step.grid, mark_as_given=False)
            # Preserve original given cells
            self.current_grid.given_cells = self.original_grid.given_cells.copy()
            self._increment_version()
            return True
        return False
    
    def get_solution_info(self) -> Optional[Dict[str, Any]]:
        """Get solution step information"""
        if not self.solution_steps:
            return None
        
        return {
            'current_step': self.current_step,
            'total_steps': len(self.solution_steps),
            'can_go_prev': self.current_step > 0,
            'can_go_next': self.current_step < len(self.solution_steps) - 1,
            'current_description': self.solution_steps[self.current_step].description if self.solution_steps else None
        }
    
    def get_performance_metrics(self) -> Optional[Dict[str, Any]]:
        """Get performance metrics"""
        if self.last_solve_time is None:
            return None
        
        metrics = {'solve_time': self.last_solve_time}
        if self.step_count is not None:
            metrics['step_count'] = self.step_count
        
        return metrics
    
    def _increment_version(self):
        """Increment version for UI updates"""
        self.version += 1
    
    def get_version(self) -> int:
        """Get current version number"""
        return self.version


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
                'grid': solution.copy(),
                'description': 'Final solution',
                'move': None,
                'action': 'complete'
            })
        return solution, steps