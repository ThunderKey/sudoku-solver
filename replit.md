# Sudoku Solver with Plugin System

## Overview

This is an interactive Sudoku solver built with Streamlit that features a modular plugin architecture. The application allows users to load Sudoku puzzles from files, solve them using various algorithms, and visualize the solution process step-by-step. The core strength of this system is its extensible plugin manager that enables dynamic loading of custom solver algorithms without modifying the core codebase.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Streamlit Web Interface**: Single-page application using Streamlit for the user interface
- **Session State Management**: Maintains puzzle state, solution steps, and user progress across interactions
- **Interactive Grid Display**: Visual representation of the Sudoku grid with real-time updates
- **Sidebar Controls**: File upload, solver selection, and solution playback controls

### Backend Architecture
- **Modular Core System**: Separation of concerns with distinct modules for grid operations, validation, and solving
- **Plugin-Based Solver Architecture**: Dynamic loading system that discovers and imports solver plugins at runtime
- **Abstract Base Classes**: SudokuSolver base class defines the interface that all solver plugins must implement
- **State Tracking**: Comprehensive step-by-step solution tracking for visualization and debugging

### Core Components
- **SudokuGrid**: Handles grid state management and basic operations
- **SudokuValidator**: Provides validation logic for Sudoku rules and puzzle states
- **PluginManager**: Dynamically discovers and loads solver implementations from both built-in and custom plugin directories
- **FileHandler**: Manages loading puzzles from JSON and text file formats

### Data Storage
- **In-Memory State**: All puzzle data and solution steps stored in Streamlit session state
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