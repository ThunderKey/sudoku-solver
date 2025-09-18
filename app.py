from controller import SudokuController
from view import MainView


def main():
    """Main application entry point using MVC architecture"""
    # Initialize MVC components
    controller = SudokuController()
    view = MainView()
    
    # Set up page
    view.setup_page()
    
    # Render UI and get user actions
    actions = view.render(controller)
    
    # Process actions through controller
    handle_actions(controller, actions)


def handle_actions(controller: SudokuController, actions: dict):
    """Handle user actions through the controller"""
    # File operations
    if 'upload_file' in actions:
        success, message = controller.load_puzzle_from_file(actions['upload_file'])
        if success:
            print(message)
        else:
            print(f"Error: {message}")
    
    if 'download_puzzle' in actions:
        puzzle_data = controller.save_current_puzzle()
        print(f"Puzzle data ready for download: {len(puzzle_data)} bytes")
    
    # Grid operations
    if 'clear_grid' in actions:
        controller.clear_grid()
    
    if 'load_sample' in actions:
        controller.load_sample_puzzle()
    
    # Cell updates
    if 'cell_updates' in actions:
        if controller.process_cell_updates(actions['cell_updates']):
            # Grid was updated, no need to rerun as updates are handled in real-time
            pass
    
    # Solver operations
    if 'solve' in actions:
        solver_data = actions['solve']
        success, message = controller.solve_puzzle(
            solver_data['solver_class'], 
            solver_data['show_steps']
        )
        if success:
            print(message)
        else:
            print(f"Error: {message}")
    
    # Step navigation
    if 'navigate_step' in actions:
        direction = actions['navigate_step']
        controller.navigate_solution_step(direction)


if __name__ == "__main__":
    main()