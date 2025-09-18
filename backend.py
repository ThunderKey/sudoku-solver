from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import json
import io
import time

from model import SudokuModel, SudokuValidator
from plugin_manager import PluginManager
from file_handler import FileHandler

app = FastAPI(title="Sudoku Solver API", version="1.0.0")

# Add CORS middleware for Vue.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:5173", 
        "http://0.0.0.0:5173",
        "http://localhost:5000",
        "http://0.0.0.0:5000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global application state
sudoku_model = SudokuModel()
plugin_manager = PluginManager()
file_handler = FileHandler()

# Pydantic models for API requests/responses
class CellUpdate(BaseModel):
    row: int
    col: int
    value: int

class SolveRequest(BaseModel):
    solver_name: str
    show_steps: bool = True

class JumpRequest(BaseModel):
    step_index: int

class ClearRequest(BaseModel):
    keep_given: bool = False

class Conflict(BaseModel):
    row: int
    col: int
    cells: List[List[int]]

class GridState(BaseModel):
    grid: List[List[int]]
    original_grid: List[List[int]]
    given_cells: List[List[bool]]
    is_empty: bool
    is_valid: bool
    is_complete: bool
    empty_count: int
    filled_count: int
    conflicts: List[Conflict]
    version: int

class SolverInfo(BaseModel):
    name: str
    description: str

class SolutionStepInfo(BaseModel):
    current_step: int
    total_steps: int
    can_go_prev: bool
    can_go_next: bool
    current_description: Optional[str]

class PerformanceMetrics(BaseModel):
    solve_time: float
    step_count: Optional[int]

class SolveResponse(BaseModel):
    success: bool
    message: str
    grid_state: GridState
    solution_info: Optional[SolutionStepInfo] = None
    performance_metrics: Optional[PerformanceMetrics] = None

# Helper functions
def serialize_grid_state() -> GridState:
    """Helper function to serialize grid state with proper type conversion"""
    state = sudoku_model.get_grid_state()
    
    # Convert conflicts to proper Conflict model structure
    conflicts = []
    for row, col, conflicting_cells in state['conflicts']:
        conflict = Conflict(
            row=int(row),
            col=int(col),
            cells=[[int(r), int(c)] for r, c in conflicting_cells]
        )
        conflicts.append(conflict)
    
    return GridState(
        grid=state['grid'].tolist(),
        original_grid=state['original_grid'].tolist(),
        given_cells=state['given_cells'].tolist(),
        is_empty=state['is_empty'],
        is_valid=state['is_valid'],
        is_complete=state['is_complete'],
        empty_count=int(state['empty_count']),
        filled_count=int(state['filled_count']),
        conflicts=conflicts,
        version=int(state['version'])
    )

# API Endpoints

@app.get("/")
async def root():
    return {"message": "Sudoku Solver API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/grid", response_model=GridState)
async def get_grid_state():
    """Get current grid state"""
    try:
        return serialize_grid_state()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting grid state: {str(e)}")

@app.post("/grid/cell", response_model=dict)
async def update_cell(cell_update: CellUpdate):
    """Update a single cell value"""
    try:
        success = sudoku_model.update_cell(cell_update.row, cell_update.col, cell_update.value)
        if not success:
            raise HTTPException(status_code=400, detail="Invalid cell update")
        return {"success": True, "message": "Cell updated successfully", "grid_state": serialize_grid_state()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating cell: {str(e)}")

@app.post("/grid/load")
async def load_puzzle(file: UploadFile = File(...)):
    """Load puzzle from uploaded file"""
    try:
        content = await file.read()
        
        # Create a temporary file-like object for the file handler
        temp_file = io.BytesIO(content)
        temp_file.name = file.filename
        
        grid = file_handler.load_puzzle(temp_file)
        sudoku_model.load_puzzle(grid)
        
        return {"success": True, "message": "Puzzle loaded successfully!", "grid_state": serialize_grid_state()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading puzzle: {str(e)}")

@app.get("/grid/sample")
async def load_sample_puzzle():
    """Load a predefined sample puzzle"""
    try:
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
        sudoku_model.load_puzzle(sample)
        return {"success": True, "message": "Sample puzzle loaded successfully!", "grid_state": serialize_grid_state()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading sample puzzle: {str(e)}")

@app.post("/grid/clear")
async def clear_grid(clear_request: ClearRequest):
    """Clear the grid"""
    try:
        sudoku_model.clear_puzzle(keep_given=clear_request.keep_given)
        return {"success": True, "message": "Grid cleared successfully!", "grid_state": serialize_grid_state()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing grid: {str(e)}")

@app.get("/grid/save")
async def save_puzzle():
    """Save current puzzle as JSON"""
    try:
        grid_state = sudoku_model.get_grid_state()
        json_data = file_handler.save_puzzle(grid_state['grid'])
        
        # Stream JSON data instead of writing to disk
        filename = f"sudoku_puzzle_{int(time.time())}.json"
        
        def generate_json():
            yield json_data.encode('utf-8')
        
        headers = {
            'Content-Disposition': f'attachment; filename={filename}'
        }
        
        return StreamingResponse(
            generate_json(),
            media_type='application/json',
            headers=headers
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving puzzle: {str(e)}")

@app.get("/solvers", response_model=List[SolverInfo])
async def get_available_solvers():
    """Get list of available solvers"""
    try:
        solvers = plugin_manager.get_available_solvers()
        return [
            SolverInfo(name=name, description=getattr(solver_class(), 'description', f'{name} solver'))
            for name, solver_class in solvers.items()
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting solvers: {str(e)}")

@app.post("/solve", response_model=SolveResponse)
async def solve_puzzle(solve_request: SolveRequest):
    """Solve the puzzle using specified solver"""
    try:
        solver_class = plugin_manager.get_solver(solve_request.solver_name)
        if not solver_class:
            raise HTTPException(status_code=404, detail=f"Solver '{solve_request.solver_name}' not found")
        
        solver = solver_class()
        current_grid = sudoku_model.get_grid_state()['grid']
        
        start_time = time.time()
        solution, steps = solver.solve_with_steps(current_grid)
        solve_time = time.time() - start_time
        
        if solution is None:
            raise HTTPException(status_code=400, detail="No solution found")
        
        if solve_request.show_steps:
            # Set solution steps in the model for step-by-step navigation
            sudoku_model.set_solution_steps(steps, solve_time)
        else:
            # Apply solution directly to the grid
            sudoku_model.load_puzzle(solution)
            sudoku_model.clear_solution_state()
        
        # Get updated grid state
        grid_state = serialize_grid_state()
        
        # Get solution info if steps are available
        solution_info = None
        if solve_request.show_steps and sudoku_model.solution_steps:
            sol_info = sudoku_model.get_solution_info()
            if sol_info:
                solution_info = SolutionStepInfo(**sol_info)
        
        # Get performance metrics
        perf_metrics = sudoku_model.get_performance_metrics()
        performance_metrics = None
        if perf_metrics:
            performance_metrics = PerformanceMetrics(**perf_metrics)
        
        return SolveResponse(
            success=True,
            message=f"Puzzle solved using {solve_request.solver_name}!",
            grid_state=grid_state,
            solution_info=solution_info,
            performance_metrics=performance_metrics
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error solving puzzle: {str(e)}")

@app.get("/solution", response_model=Optional[SolutionStepInfo])
async def get_solution_info():
    """Get solution step information"""
    try:
        solution_info = sudoku_model.get_solution_info()
        if solution_info is None:
            return None
        
        return SolutionStepInfo(**solution_info)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting solution info: {str(e)}")

@app.post("/solution/next")
async def next_solution_step():
    """Navigate to next solution step"""
    try:
        solution_info = sudoku_model.get_solution_info()
        if not solution_info or not solution_info['can_go_next']:
            raise HTTPException(status_code=400, detail="Cannot navigate to next step")
        
        success = sudoku_model.navigate_to_step(solution_info['current_step'] + 1)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to navigate to next step")
        
        sol_info = sudoku_model.get_solution_info()
        return {
            "success": True, 
            "message": "Navigated to next step",
            "grid_state": serialize_grid_state(),
            "solution_info": SolutionStepInfo(**sol_info) if sol_info else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error navigating to next step: {str(e)}")

@app.post("/solution/prev")
async def prev_solution_step():
    """Navigate to previous solution step"""
    try:
        solution_info = sudoku_model.get_solution_info()
        if not solution_info or not solution_info['can_go_prev']:
            raise HTTPException(status_code=400, detail="Cannot navigate to previous step")
        
        success = sudoku_model.navigate_to_step(solution_info['current_step'] - 1)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to navigate to previous step")
        
        sol_info = sudoku_model.get_solution_info()
        return {
            "success": True, 
            "message": "Navigated to previous step",
            "grid_state": serialize_grid_state(),
            "solution_info": SolutionStepInfo(**sol_info) if sol_info else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error navigating to previous step: {str(e)}")

@app.post("/solution/jump")
async def jump_to_solution_step(jump_request: JumpRequest):
    """Jump to specific solution step"""
    try:
        success = sudoku_model.navigate_to_step(jump_request.step_index)
        if not success:
            raise HTTPException(status_code=400, detail="Invalid step index")
        
        sol_info = sudoku_model.get_solution_info()
        return {
            "success": True, 
            "message": f"Jumped to step {jump_request.step_index}",
            "grid_state": serialize_grid_state(),
            "solution_info": SolutionStepInfo(**sol_info) if sol_info else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error jumping to solution step: {str(e)}")

@app.get("/performance", response_model=Optional[PerformanceMetrics])
async def get_performance_metrics():
    """Get performance metrics"""
    try:
        metrics = sudoku_model.get_performance_metrics()
        if metrics is None:
            return None
        
        return PerformanceMetrics(**metrics)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting performance metrics: {str(e)}")

@app.post("/plugins/reload")
async def reload_plugins():
    """Reload all solver plugins"""
    try:
        plugin_manager.reload_plugins()
        return {"success": True, "message": "Plugins reloaded successfully!"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reloading plugins: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)