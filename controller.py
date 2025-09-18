import numpy as np
import time
from typing import Optional, Dict, Any, Tuple, List

from model import SudokuModel, SudokuValidator
from plugin_manager import PluginManager
from file_handler import FileHandler


class SudokuController:
    """Controller layer for the Sudoku application - handles business logic and user actions"""
    
    def __init__(self):
        self.model = SudokuModel()
        self.plugin_manager = PluginManager()
        self.file_handler = FileHandler()
        self.solving = False
        # Internal state attributes for view compatibility
        self.grid = None
        self.original_grid = None
        self.grid_version = 0
        self.solution_steps = []
        self.current_step = 0
        self.last_solve_time = None
        self.last_step_count = None
        self._sync_internal_state()
    
    
    def load_puzzle_from_file(self, uploaded_file) -> tuple[bool, str]:
        """Load puzzle from uploaded file"""
        try:
            grid = self.file_handler.load_puzzle(uploaded_file)
            self.model.load_puzzle(grid)
            self._sync_internal_state()
            return True, "Puzzle loaded successfully!"
        except Exception as e:
            return False, f"Error loading puzzle: {str(e)}"
    
    def save_current_puzzle(self) -> str:
        """Save current puzzle and return JSON data"""
        grid_state = self.model.get_grid_state()
        return self.file_handler.save_puzzle(grid_state['grid'])
    
    def clear_grid(self):
        """Clear the entire grid and reset state"""
        self.model.clear_puzzle(keep_given=False)
        self._sync_internal_state()
    
    def load_sample_puzzle(self):
        """Load a predefined sample puzzle"""
        sample = np.array([
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9]
        ])
        self.model.load_puzzle(sample)
        self._sync_internal_state()
    
    def _sync_internal_state(self):
        """Sync model state with internal state for view compatibility"""
        grid_state = self.model.get_grid_state()
        self.grid = grid_state['grid']
        self.original_grid = grid_state['original_grid']
        self.grid_version = grid_state['version']
        
        # Sync solution state
        solution_info = self.model.get_solution_info()
        if solution_info:
            # Convert SolutionStep objects back to dicts for view compatibility
            self.solution_steps = [step.to_dict() for step in self.model.solution_steps]
            self.current_step = solution_info['current_step']
        else:
            self.solution_steps = []
            self.current_step = 0
        
        # Sync metrics
        metrics = self.model.get_performance_metrics()
        if metrics:
            self.last_solve_time = metrics['solve_time']
            if 'step_count' in metrics:
                self.last_step_count = metrics['step_count']
    
    def update_cell(self, row: int, col: int, value: int) -> bool:
        """Update a cell value if the cell is not a given (original) value"""
        success = self.model.update_cell(row, col, value)
        if success:
            self._sync_internal_state()
        return success
    
    def get_grid_state(self) -> Dict[str, Any]:
        """Get current grid state and validation info"""
        return self.model.get_grid_state()
    
    def get_available_solvers(self) -> Dict[str, Any]:
        """Get available solvers from plugin manager"""
        return self.plugin_manager.get_available_solvers()
    
    def solve_puzzle(self, solver_class, show_steps: bool) -> tuple[bool, str]:
        """Solve the puzzle using the selected solver"""
        grid_state = self.model.get_grid_state()
        if grid_state['is_empty']:
            return False, "Please enter a puzzle first"
        
        self.solving = True
        self.model.is_solving = True
        
        try:
            # Create solver instance
            solver = solver_class()
            
            # Measure solve time
            start_time = time.time()
            current_grid = grid_state['grid']
            
            # Solve with or without steps
            if show_steps and hasattr(solver, 'solve_with_steps'):
                solution, steps = solver.solve_with_steps(current_grid.copy())
                if solution is not None:
                    solve_time = time.time() - start_time
                    self.model.set_solution_steps(steps, solve_time)
            else:
                solution = solver.solve(current_grid.copy())
                solve_time = time.time() - start_time
                if solution is not None:
                    self.model.last_solve_time = solve_time
                    # Apply solution immediately if not showing steps
                    self.model.current_grid.set_grid(solution, mark_as_given=False)
                    # Preserve original given cells
                    self.model.current_grid.given_cells = self.model.original_grid.given_cells.copy()
            
            self._sync_internal_state()
            
            if solution is not None:
                solve_time_str = f"{self.model.last_solve_time:.4f}s"
                return True, f"✅ Puzzle solved in {solve_time_str}!"
            else:
                return False, "❌ No solution found for this puzzle"
                
        except Exception as e:
            return False, f"Error solving puzzle: {str(e)}"
        finally:
            self.solving = False
            self.model.is_solving = False
    
    def navigate_solution_step(self, direction: str) -> bool:
        """Navigate through solution steps (direction: 'prev' or 'next')"""
        solution_info = self.model.get_solution_info()
        if not solution_info:
            return False
        
        if direction == 'prev':
            new_step = max(0, solution_info['current_step'] - 1)
        elif direction == 'next':
            new_step = min(solution_info['total_steps'] - 1, solution_info['current_step'] + 1)
        else:
            return False
        
        if new_step != solution_info['current_step']:
            success = self.model.navigate_to_step(new_step)
            if success:
                self._sync_internal_state()
            return success
        return False
    
    
    def get_solution_step_info(self) -> Optional[Dict[str, Any]]:
        """Get current solution step information"""
        return self.model.get_solution_info()
    
    def get_performance_metrics(self) -> Optional[Dict[str, Any]]:
        """Get performance metrics from last solve"""
        return self.model.get_performance_metrics()
    
    def process_cell_updates(self, cell_updates: Dict[Tuple[int, int], int]):
        """Process multiple cell updates"""
        any_updated = False
        for (row, col), value in cell_updates.items():
            if self.update_cell(row, col, value):
                any_updated = True
        return any_updated