# Sudoku Solver with Plugin System

## Overview

This is an interactive Sudoku solver built with Streamlit that features a modular plugin architecture. The application allows users to load Sudoku puzzles from files, solve them using various algorithms, and visualize the solution process step-by-step. The core strength of this system is its extensible plugin manager that enables dynamic loading of custom solver algorithms without modifying the core codebase.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows the **Model-View-Controller (MVC)** architectural pattern for clean separation of concerns and maintainability.

### Model Layer (model.py)
- **SudokuModel**: Central model class managing complete puzzle state, solution tracking, and performance metrics
- **SudokuGrid**: Enhanced grid operations with given/solved cell distinction and state management
- **SudokuValidator**: Comprehensive validation utilities with conflict detection and rule checking
- **SolutionStep**: Structured data class for step-by-step solution tracking
- **Data Integrity**: Maintains separation between original puzzle and current state

### View Layer (view.py)  
- **MainView**: Primary view coordinator that orchestrates all UI components
- **SudokuGridView**: Renders the interactive 9x9 grid with authentic styling and cell input handling
- **SidebarView**: File operations and grid management controls
- **SolverControlsView**: Solver selection, step navigation, and performance display
- **Clean Separation**: Views only handle presentation logic and user input collection

### Controller Layer (controller.py)
- **SudokuController**: Central business logic coordinator managing user actions
- **Model-View Mediation**: Bridges interactions between model state and view rendering
- **Action Processing**: Handles file I/O, puzzle solving, step navigation, and cell updates
- **State Synchronization**: Maintains compatibility with Streamlit session state for optimal performance

### Application Entry Point (app.py)
- **Streamlined Coordinator**: Minimal main application that initializes MVC components
- **Action Dispatcher**: Central handler for all user interactions through clean action dictionary pattern
- **Clean Architecture**: Separates initialization, rendering, and action handling into distinct phases

### Data Storage
- **Model-Centric State**: All puzzle data centrally managed through SudokuModel
- **Session State Bridge**: Controller maintains backward compatibility with Streamlit session patterns
- **File-Based Input**: Support for JSON and text file formats for puzzle import
- **No Persistent Database**: Stateless application with no permanent data storage

### Solver Plugin System
- **Plugin Discovery**: Automatic detection of solver classes in `solvers/` and `plugins/` directories
- **Dynamic Loading**: Runtime import and instantiation of solver classes using Python's importlib
- **Standardized Interface**: All solvers implement the base SudokuSolver class with required `solve()` and optional `solve_with_steps()` methods
- **Built-in Algorithms**: Includes backtracking and brute force solvers as reference implementations

## External Dependencies

### Core Framework
- **Streamlit**: Web application framework for the user interface
- **NumPy**: Numerical computing library for grid operations and array handling

### Python Standard Library
- **importlib**: Dynamic module importing for plugin system
- **pathlib**: Modern path handling for file operations
- **json**: JSON file format support for puzzle loading
- **typing**: Type hints for better code documentation and IDE support

### File Format Support
- **JSON Format**: Structured puzzle data with flexible field naming (grid, puzzle, or board)
- **Text Format**: Plain text puzzle representation for simple file imports

### Plugin Architecture Dependencies
- **inspect**: Runtime introspection for plugin validation
- **sys**: System-specific parameters and functions for module management
- **os**: Operating system interface for file system operations