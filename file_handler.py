import json
import numpy as np
from pathlib import Path
from typing import Optional

class FileHandler:
    """Handles loading and saving of Sudoku puzzles"""
    
    @staticmethod
    def load_puzzle(uploaded_file) -> np.ndarray:
        """Load a puzzle from an uploaded file"""
        if uploaded_file.type == "application/json":
            return FileHandler._load_json(uploaded_file)
        elif uploaded_file.type == "text/plain":
            return FileHandler._load_text(uploaded_file)
        else:
            raise ValueError(f"Unsupported file type: {uploaded_file.type}")
    
    @staticmethod
    def _load_json(uploaded_file) -> np.ndarray:
        """Load puzzle from JSON format"""
        try:
            content = json.load(uploaded_file)
            
            if isinstance(content, dict):
                # Check for different JSON formats
                if 'grid' in content:
                    grid_data = content['grid']
                elif 'puzzle' in content:
                    grid_data = content['puzzle']
                elif 'board' in content:
                    grid_data = content['board']
                else:
                    raise ValueError("JSON must contain 'grid', 'puzzle', or 'board' field")
            elif isinstance(content, list):
                grid_data = content
            else:
                raise ValueError("Invalid JSON format")
            
            grid = np.array(grid_data, dtype=int)
            
            if grid.shape != (9, 9):
                raise ValueError(f"Grid must be 9x9, got {grid.shape}")
            
            if not np.all((grid >= 0) & (grid <= 9)):
                raise ValueError("Grid values must be between 0 and 9")
            
            return grid
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
        except Exception as e:
            raise ValueError(f"Error loading JSON: {e}")
    
    @staticmethod
    def _load_text(uploaded_file) -> np.ndarray:
        """Load puzzle from text format"""
        try:
            content = uploaded_file.read().decode('utf-8')
            lines = content.strip().split('\n')
            
            # Filter out empty lines and comments
            grid_lines = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    grid_lines.append(line)
            
            if len(grid_lines) != 9:
                raise ValueError(f"Text format must have exactly 9 lines, got {len(grid_lines)}")
            
            grid = []
            for line in grid_lines:
                # Handle different separators
                if ',' in line:
                    row = [int(x.strip()) for x in line.split(',')]
                elif ' ' in line:
                    row = [int(x) for x in line.split()]
                else:
                    # Assume single digits without separators
                    row = [int(c) for c in line if c.isdigit()]
                
                if len(row) != 9:
                    raise ValueError(f"Each row must have exactly 9 numbers, got {len(row)}")
                
                grid.append(row)
            
            grid = np.array(grid, dtype=int)
            
            if not np.all((grid >= 0) & (grid <= 9)):
                raise ValueError("Grid values must be between 0 and 9")
            
            return grid
            
        except Exception as e:
            raise ValueError(f"Error loading text file: {e}")
    
    @staticmethod
    def save_puzzle(grid: np.ndarray, format: str = "json") -> str:
        """Save puzzle to string format"""
        if format.lower() == "json":
            return FileHandler._save_json(grid)
        elif format.lower() == "text":
            return FileHandler._save_text(grid)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    @staticmethod
    def _save_json(grid: np.ndarray) -> str:
        """Save puzzle as JSON string"""
        puzzle_data = {
            "grid": grid.tolist(),
            "format": "sudoku",
            "version": "1.0"
        }
        return json.dumps(puzzle_data, indent=2)
    
    @staticmethod
    def _save_text(grid: np.ndarray) -> str:
        """Save puzzle as text string"""
        lines = []
        lines.append("# Sudoku Puzzle")
        lines.append("# 0 represents empty cells")
        lines.append("")
        
        for row in grid:
            lines.append(" ".join(str(cell) for cell in row))
        
        return "\n".join(lines)
    
    @staticmethod
    def export_solution(original_grid: np.ndarray, solution_grid: np.ndarray, 
                       solver_name: str, solve_time: float) -> str:
        """Export both puzzle and solution with metadata"""
        export_data = {
            "original_puzzle": original_grid.tolist(),
            "solution": solution_grid.tolist(),
            "metadata": {
                "solver": solver_name,
                "solve_time_seconds": solve_time,
                "format": "sudoku_solution",
                "version": "1.0"
            }
        }
        return json.dumps(export_data, indent=2)
