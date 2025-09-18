import streamlit as st
import numpy as np
from typing import Dict, Any, Optional


class SudokuGridView:
    """View component for rendering the Sudoku grid"""
    
    def __init__(self):
        self._add_grid_styles()
    
    def _add_grid_styles(self):
        """Add CSS styles for the Sudoku grid"""
        st.markdown("""
        <style>
        /* Clean SudokuPad grid styling using aria-label selectors */
        input[aria-label^="Cell ("] {
            width: 50px !important;
            height: 50px !important;
            text-align: center !important;
            font-size: 18px !important;
            font-weight: bold !important;
            font-family: Arial, sans-serif !important;
            border-radius: 0 !important;
            border: 1px solid #ddd !important;
            background-color: #ffffff !important;
            color: #333333 !important;
            outline: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin: 0 !important;
            line-height: 1 !important;
            -webkit-appearance: none !important;
            -moz-appearance: none !important;
            appearance: none !important;
            transition: none !important;
        }
        
        /* Reset any default focus/active states first */
        input[aria-label^="Cell ("]:focus,
        input[aria-label^="Cell ("]:active {
            background-color: #ffffff !important;
            border: 1px solid #ddd !important;
            outline: 2px solid #4a90e2 !important;
            outline-offset: -2px !important;
        }
        
        /* Simple hover effect - only on actual hover */
        input[aria-label^="Cell ("]:hover:not(:focus) {
            background-color: #f0f8ff !important;
        }
        
        /* Given numbers (disabled inputs) styling */
        input[aria-label^="Cell ("]:disabled {
            background-color: #f8f9fa !important;
            color: #212529 !important;
            font-weight: bold !important;
            cursor: not-allowed !important;
            opacity: 1 !important;
        }
        
        /* Force white background for all non-disabled cells */
        input[aria-label^="Cell ("]:not(:disabled):not(:hover):not(:focus) {
            background-color: #ffffff !important;
        }
        
        /* 3x3 Box Separation - Bold black borders for authentic SudokuPad look */
        
        /* Right borders for columns 3 and 6 */
        input[aria-label$=",3)"], input[aria-label$=",6)"] {
            border-right: 3px solid #000000 !important;
        }
        
        /* Bottom borders for rows 3 and 6 */
        input[aria-label^="Cell (3,"], input[aria-label^="Cell (6,"] {
            border-bottom: 3px solid #000000 !important;
        }
        
        /* Outer frame borders - bold black */
        /* Top border for first row */
        input[aria-label^="Cell (1,"] {
            border-top: 3px solid #000000 !important;
        }
        
        /* Left border for first column */
        input[aria-label$=",1)"] {
            border-left: 3px solid #000000 !important;
        }
        
        /* Bottom border for last row */
        input[aria-label^="Cell (9,"] {
            border-bottom: 3px solid #000000 !important;
        }
        
        /* Right border for last column */
        input[aria-label$=",9)"] {
            border-right: 3px solid #000000 !important;
        }
        
        /* Clean layout without unnecessary styling */
        div[data-testid="column"] {
            padding: 0 !important;
            margin: 0 !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
        }
        
        /* Hide labels */
        label[data-testid="stTextInput-label"] {
            display: none !important;
        }
        
        /* Clean up spacing */
        .stTextInput > div > div {
            gap: 0 !important;
        }
        
        .stColumns > div {
            padding: 0 !important;
            margin: 0 !important;
        }
        
        /* Simple container - minimal styling */
        .sudoku-grid-wrapper {
            background: #ffffff;
            padding: 10px;
            margin: 16px auto;
            max-width: 470px;
            border: 3px solid #000000;
        }
        
        /* Force Arial font for consistent SudokuPad aesthetic */
        .stMarkdown h3, .stMarkdown h2, .stMarkdown h1 {
            font-family: Arial, sans-serif !important;
        }
        
        /* Global font consistency for app container */
        [data-testid="stAppViewContainer"], 
        .main .block-container,
        .stMarkdown,
        .stSelectbox label,
        .stButton button,
        .stMarkdown * {
            font-family: Arial, sans-serif !important;
        }
        
        /* Force Arial on main title specifically */
        .main .block-container > div:first-child h1,
        .main .block-container h1:first-of-type,
        h1 {
            font-family: Arial, sans-serif !important;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def render(self, controller) -> Dict[str, Any]:
        """Render the Sudoku grid and return any cell updates"""
        st.subheader("Sudoku Grid")
        
        # Create a visual wrapper div
        st.markdown('<div class="sudoku-grid-wrapper">', unsafe_allow_html=True)
        
        cell_updates = {}
        
        # Create 9x9 grid of number inputs
        for i in range(9):
            cols = st.columns(9)
            for j in range(9):
                with cols[j]:
                    key = f"cell_{i}_{j}_{st.session_state.grid_version}"
                    current_value = int(st.session_state.grid[i, j])
                    
                    # Determine if this is an original clue
                    is_given = st.session_state.original_grid[i, j] != 0
                    
                    # Text input for grid cells
                    display_value = str(current_value) if current_value != 0 else ""
                    text_value = st.text_input(
                        f"Cell ({i+1},{j+1})",
                        value=display_value,
                        max_chars=1,
                        key=key,
                        disabled=is_given,
                        label_visibility="collapsed"
                    )
                    
                    # Validate and convert text input
                    if text_value == "" or text_value == "0":
                        new_value = 0
                    elif text_value.isdigit() and 1 <= int(text_value) <= 9:
                        new_value = int(text_value)
                    else:
                        new_value = current_value  # Keep current value if invalid
                    
                    # Track cell updates
                    if new_value != current_value:
                        cell_updates[(i, j)] = new_value
        
        st.markdown('</div>', unsafe_allow_html=True)
        return cell_updates
    
    def display_validation_status(self, grid_state: Dict[str, Any]):
        """Display validation status for the current grid"""
        if grid_state['is_empty']:
            return
        
        if grid_state['is_valid']:
            st.success("✅ Current state is valid")
            if grid_state['is_complete']:
                st.balloons()
                st.success("🎉 Puzzle solved!")
        else:
            st.error("❌ Current state has conflicts")


class SidebarView:
    """View component for the sidebar controls"""
    
    def render(self, controller) -> Dict[str, Any]:
        """Render sidebar controls and return user actions"""
        actions = {}
        
        with st.sidebar:
            st.header("Controls")
            
            # File operations
            st.subheader("📁 File Operations")
            uploaded_file = st.file_uploader("Upload Sudoku puzzle", type=['json', 'txt'])
            if uploaded_file:
                actions['upload_file'] = uploaded_file
            
            if st.button("📥 Download Current Puzzle"):
                actions['download_puzzle'] = True
            
            # Grid operations
            st.subheader("🔧 Grid Operations")
            if st.button("Clear Grid"):
                actions['clear_grid'] = True
            
            if st.button("Load Sample Puzzle"):
                actions['load_sample'] = True
        
        return actions


class SolverControlsView:
    """View component for solver controls"""
    
    def render(self, controller) -> Dict[str, Any]:
        """Render solver controls and return user actions"""
        st.subheader("Solver Controls")
        actions = {}
        
        # Available solvers
        available_solvers = controller.get_available_solvers()
        solver_names = list(available_solvers.keys())
        
        if not solver_names:
            st.warning("No solvers available. Please check the solvers directory.")
            return actions
        
        selected_solver = st.selectbox("Choose Solver", solver_names)
        
        # Solver options
        show_steps = st.checkbox("Show step-by-step solution", value=True)
        
        # Solve button
        if st.button("🚀 Solve Puzzle", disabled=st.session_state.solving):
            actions['solve'] = {
                'solver_class': available_solvers[selected_solver],
                'show_steps': show_steps
            }
        
        return actions
    
    def render_step_controls(self, controller) -> Dict[str, Any]:
        """Render step-by-step solution controls"""
        step_info = controller.get_solution_step_info()
        actions = {}
        
        if not step_info:
            return actions
        
        st.subheader("Step-by-step Solution")
        
        col_prev, col_next = st.columns(2)
        with col_prev:
            if st.button("⬅️ Previous", disabled=not step_info['can_go_prev']):
                actions['navigate_step'] = 'prev'
        
        with col_next:
            if st.button("➡️ Next", disabled=not step_info['can_go_next']):
                actions['navigate_step'] = 'next'
        
        st.write(f"Step {step_info['current_step'] + 1} of {step_info['total_steps']}")
        
        return actions
    
    def display_performance_metrics(self, controller):
        """Display performance metrics"""
        metrics = controller.get_performance_metrics()
        if metrics:
            st.subheader("Performance")
            st.metric("Solve Time", f"{metrics['solve_time']:.4f}s")
            if 'step_count' in metrics:
                st.metric("Steps", metrics['step_count'])


class MainView:
    """Main view coordinator for the Sudoku application"""
    
    def __init__(self):
        self.grid_view = SudokuGridView()
        self.sidebar_view = SidebarView()
        self.solver_controls_view = SolverControlsView()
    
    def setup_page(self):
        """Set up the Streamlit page configuration"""
        st.set_page_config(
            page_title="Sudoku Solver with Plugin System",
            page_icon="🧩",
            layout="wide"
        )
        
        st.title("🧩 Sudoku Solver with Plugin System")
        st.markdown("Interactive Sudoku solver with custom algorithm support")
    
    def render(self, controller) -> Dict[str, Any]:
        """Render the complete UI and collect all user actions"""
        actions = {}
        
        # Render sidebar
        sidebar_actions = self.sidebar_view.render(controller)
        actions.update(sidebar_actions)
        
        # Main content area
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Render grid and collect cell updates
            cell_updates = self.grid_view.render(controller)
            if cell_updates:
                actions['cell_updates'] = cell_updates
            
            # Display validation status
            grid_state = controller.get_grid_state()
            self.grid_view.display_validation_status(grid_state)
        
        with col2:
            # Render solver controls
            solver_actions = self.solver_controls_view.render(controller)
            actions.update(solver_actions)
            
            # Render step controls if available
            step_actions = self.solver_controls_view.render_step_controls(controller)
            actions.update(step_actions)
            
            # Display performance metrics
            self.solver_controls_view.display_performance_metrics(controller)
        
        return actions