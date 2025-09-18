import importlib
import importlib.util
import inspect
from pathlib import Path
from typing import Dict, Type, List
import sys
import os

from sudoku_core import SudokuSolver

class PluginManager:
    """Manages dynamic loading of solver plugins"""
    
    def __init__(self):
        self.solvers = {}
        self.load_builtin_solvers()
        self.load_plugins()
    
    def load_builtin_solvers(self):
        """Load built-in solvers from the solvers directory"""
        solvers_dir = Path("solvers")
        if not solvers_dir.exists():
            return
        
        for solver_file in solvers_dir.glob("*.py"):
            if solver_file.name.startswith("__"):
                continue
            
            try:
                self._load_solver_from_file(solver_file)
            except Exception as e:
                print(f"Failed to load built-in solver {solver_file}: {e}")
    
    def load_plugins(self):
        """Load custom solver plugins from the plugins directory"""
        plugins_dir = Path("plugins")
        if not plugins_dir.exists():
            plugins_dir.mkdir(parents=True, exist_ok=True)
            return
        
        for plugin_file in plugins_dir.glob("*.py"):
            if plugin_file.name.startswith("__"):
                continue
            
            try:
                self._load_solver_from_file(plugin_file)
            except Exception as e:
                print(f"Failed to load plugin {plugin_file}: {e}")
    
    def _load_solver_from_file(self, file_path: Path):
        """Load a solver class from a Python file"""
        module_name = file_path.stem
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load spec from {file_path}")
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find all SudokuSolver subclasses in the module
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, SudokuSolver) and 
                obj != SudokuSolver):
                
                # Create an instance to get metadata
                instance = obj()
                solver_name = getattr(instance, 'name', name)
                self.solvers[solver_name] = obj
                print(f"Loaded solver: {solver_name}")
    
    def get_available_solvers(self) -> Dict[str, Type[SudokuSolver]]:
        """Get dictionary of available solver classes"""
        return self.solvers.copy()
    
    def get_solver(self, name: str) -> Type[SudokuSolver]:
        """Get a specific solver class by name"""
        return self.solvers.get(name)
    
    def list_solvers(self) -> List[str]:
        """Get list of available solver names"""
        return list(self.solvers.keys())
    
    def reload_plugins(self):
        """Reload all plugins (useful for development)"""
        self.solvers.clear()
        
        # Clear module cache for plugins
        modules_to_remove = []
        for module_name in sys.modules:
            if 'plugins.' in module_name or 'solvers.' in module_name:
                modules_to_remove.append(module_name)
        
        for module_name in modules_to_remove:
            del sys.modules[module_name]
        
        # Reload everything
        self.load_builtin_solvers()
        self.load_plugins()
    
    def install_plugin(self, plugin_code: str, filename: str) -> bool:
        """Install a new plugin from code string"""
        try:
            plugins_dir = Path("plugins")
            plugins_dir.mkdir(exist_ok=True)
            
            plugin_path = plugins_dir / filename
            with open(plugin_path, 'w') as f:
                f.write(plugin_code)
            
            # Try to load the new plugin
            self._load_solver_from_file(plugin_path)
            return True
            
        except Exception as e:
            print(f"Failed to install plugin {filename}: {e}")
            return False
