"""
Sudoku Solver Plugins

This package contains custom solver implementations that extend the base SudokuSolver class.
Plugins are automatically discovered and loaded by the PluginManager.

To create a new solver plugin:
1. Create a new .py file in this directory
2. Import the SudokuSolver base class from sudoku_core
3. Create a class that inherits from SudokuSolver
4. Implement the required solve() method
5. Optionally implement solve_with_steps() for step-by-step visualization

Example:
    from sudoku_core import SudokuSolver
    
    class MySolver(SudokuSolver):
        def __init__(self):
            super().__init__()
            self.name = "My Custom Solver"
            self.description = "Description of my solver"
        
        def solve(self, grid):
            # Your solving logic here
            return solved_grid
"""
