import streamlit as st
import numpy as np
import time
from pathlib import Path
import json

from sudoku_core import SudokuGrid, SudokuValidator
from plugin_manager import PluginManager
from file_handler import FileHandler
from solvers.backtracking_solver import BacktrackingSolver

# Initialize session state
if 'grid' not in st.session_state:
    st.session_state.grid = np.zeros((9, 9), dtype=int)
if 'original_grid' not in st.session_state:
    st.session_state.original_grid = np.zeros((9, 9), dtype=int)
if 'solution_steps' not in st.session_state:
    st.session_state.solution_steps = []
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0
if 'solving' not in st.session_state:
    st.session_state.solving = False
if 'plugin_manager' not in st.session_state:
    st.session_state.plugin_manager = PluginManager()

def main():
    st.set_page_config(
        page_title="Sudoku Solver with Plugin System",
        page_icon="🧩",
        layout="wide"
    )
    
    st.title("🧩 Sudoku Solver with Plugin System")
    st.markdown("Interactive Sudoku solver with custom algorithm support")
    
    # Initialize components
    validator = SudokuValidator()
    plugin_manager = st.session_state.plugin_manager
    file_handler = FileHandler()
    
    # Sidebar for controls
    with st.sidebar:
        st.header("Controls")
        
        # File operations
        st.subheader("📁 File Operations")
        uploaded_file = st.file_uploader("Upload Sudoku puzzle", type=['json', 'txt'])
        if uploaded_file:
            try:
                grid = file_handler.load_puzzle(uploaded_file)
                st.session_state.grid = grid
                st.session_state.original_grid = grid.copy()
                st.success("Puzzle loaded successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error loading puzzle: {str(e)}")
        
        if st.button("📥 Download Current Puzzle"):
            puzzle_data = file_handler.save_puzzle(st.session_state.grid)
            st.download_button(
                label="Download JSON",
                data=puzzle_data,
                file_name="sudoku_puzzle.json",
                mime="application/json"
            )
        
        # Grid operations
        st.subheader("🔧 Grid Operations")
        if st.button("Clear Grid"):
            st.session_state.grid = np.zeros((9, 9), dtype=int)
            st.session_state.original_grid = np.zeros((9, 9), dtype=int)
            st.session_state.solution_steps = []
            st.session_state.current_step = 0
            st.rerun()
        
        if st.button("Load Sample Puzzle"):
            # Load a sample puzzle
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
            st.session_state.grid = sample
            st.session_state.original_grid = sample.copy()
            st.session_state.solution_steps = []
            st.session_state.current_step = 0
            st.rerun()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Sudoku Grid")
        render_sudoku_grid(validator)
        
        # Validation status
        if not np.array_equal(st.session_state.grid, np.zeros((9, 9))):
            is_valid = validator.is_valid_state(st.session_state.grid)
            if is_valid:
                st.success("✅ Current state is valid")
                if validator.is_complete(st.session_state.grid):
                    st.balloons()
                    st.success("🎉 Puzzle solved!")
            else:
                st.error("❌ Current state has conflicts")
    
    with col2:
        st.subheader("Solver Controls")
        
        # Available solvers
        available_solvers = plugin_manager.get_available_solvers()
        solver_names = list(available_solvers.keys())
        
        if not solver_names:
            st.warning("No solvers available. Please check the solvers directory.")
            return
        
        selected_solver = st.selectbox("Choose Solver", solver_names)
        
        # Solver options
        show_steps = st.checkbox("Show step-by-step solution", value=True)
        
        # Solve button
        if st.button("🚀 Solve Puzzle", disabled=st.session_state.solving):
            if np.array_equal(st.session_state.grid, np.zeros((9, 9))):
                st.warning("Please enter a puzzle first")
            else:
                solve_puzzle(available_solvers[selected_solver], show_steps, validator)
        
        # Step-by-step controls
        if st.session_state.solution_steps and show_steps:
            st.subheader("Step-by-step Solution")
            
            col_prev, col_next = st.columns(2)
            with col_prev:
                if st.button("⬅️ Previous", disabled=st.session_state.current_step <= 0):
                    st.session_state.current_step = max(0, st.session_state.current_step - 1)
                    apply_step(st.session_state.current_step)
                    st.rerun()
            
            with col_next:
                if st.button("➡️ Next", disabled=st.session_state.current_step >= len(st.session_state.solution_steps) - 1):
                    st.session_state.current_step = min(len(st.session_state.solution_steps) - 1, st.session_state.current_step + 1)
                    apply_step(st.session_state.current_step)
                    st.rerun()
            
            st.write(f"Step {st.session_state.current_step + 1} of {len(st.session_state.solution_steps)}")
        
        # Performance metrics
        if 'last_solve_time' in st.session_state:
            st.subheader("Performance")
            st.metric("Solve Time", f"{st.session_state.last_solve_time:.4f}s")
            if 'last_step_count' in st.session_state:
                st.metric("Steps", st.session_state.last_step_count)

def render_sudoku_grid(validator):
    """Render the interactive Sudoku grid"""
    st.markdown("""
    <style>
    .sudoku-container {
        display: grid;
        grid-template-columns: repeat(9, 1fr);
        gap: 2px;
        max-width: 450px;
        margin: 0 auto;
    }
    .sudoku-cell {
        width: 45px;
        height: 45px;
        text-align: center;
        border: 1px solid #ccc;
        font-size: 18px;
        font-weight: bold;
    }
    .sudoku-given {
        background-color: #f0f0f0;
        color: #333;
    }
    .sudoku-user {
        background-color: white;
        color: #0066cc;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create 9x9 grid of number inputs
    for i in range(9):
        cols = st.columns(9)
        for j in range(9):
            with cols[j]:
                key = f"cell_{i}_{j}"
                current_value = int(st.session_state.grid[i, j]) if st.session_state.grid[i, j] != 0 else None
                
                # Determine if this is an original clue
                is_given = st.session_state.original_grid[i, j] != 0
                
                new_value = st.number_input(
                    f"Cell ({i+1},{j+1})",
                    min_value=0,
                    max_value=9,
                    value=current_value,
                    step=1,
                    key=key,
                    disabled=is_given,
                    label_visibility="collapsed"
                )
                
                if new_value is None:
                    new_value = 0
                
                if new_value != st.session_state.grid[i, j]:
                    st.session_state.grid[i, j] = new_value
                    st.rerun()

def solve_puzzle(solver_class, show_steps, validator):
    """Solve the puzzle using the selected solver"""
    st.session_state.solving = True
    
    try:
        # Create solver instance
        solver = solver_class()
        
        # Measure solve time
        start_time = time.time()
        
        # Solve with or without steps
        if show_steps and hasattr(solver, 'solve_with_steps'):
            solution, steps = solver.solve_with_steps(st.session_state.grid.copy())
            st.session_state.solution_steps = steps
            st.session_state.current_step = 0
            st.session_state.last_step_count = len(steps)
        else:
            solution = solver.solve(st.session_state.grid.copy())
            st.session_state.solution_steps = []
        
        end_time = time.time()
        st.session_state.last_solve_time = end_time - start_time
        
        if solution is not None:
            if show_steps and st.session_state.solution_steps:
                # Start with original grid, user can step through
                pass
            else:
                # Apply solution immediately
                st.session_state.grid = solution
            st.success(f"✅ Puzzle solved in {st.session_state.last_solve_time:.4f}s!")
        else:
            st.error("❌ No solution found for this puzzle")
            
    except Exception as e:
        st.error(f"Error solving puzzle: {str(e)}")
    finally:
        st.session_state.solving = False
        st.rerun()

def apply_step(step_index):
    """Apply a specific step from the solution"""
    if step_index < len(st.session_state.solution_steps):
        step = st.session_state.solution_steps[step_index]
        st.session_state.grid = step['grid'].copy()

if __name__ == "__main__":
    main()
