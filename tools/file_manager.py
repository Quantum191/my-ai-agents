import os
import sys
import subprocess
from pathlib import Path

# Fix 2A: Dynamic Root Normalization
# Assuming this file is in tools/, the project root is one directory up
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Use env variables for external dependencies to keep it portable
ANTIGRAVITY_PATH = os.getenv("ANTIGRAVITY_PATH", os.path.expanduser("~/.gemini/antigravity"))

def get_safe_path(filename):
    """Ensures all file operations stay within the project directory."""
    if not filename or not isinstance(filename, str):
        # Return a dummy path that doesn't exist instead of crashing
        return os.path.join(PROJECT_ROOT, "MISSING_FILENAME_ERROR")
    
    # Allow DEV-01 to read plans from Antigravity memory dynamically
    if filename.startswith(PROJECT_ROOT) or filename.startswith(ANTIGRAVITY_PATH):
        return filename
        
    clean_name = filename.lstrip("/")
    return os.path.join(PROJECT_ROOT, clean_name)

def read_project_file(filename):
    """Reads file content safely."""
    path = get_safe_path(filename)
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        return f"Error: File '{filename}' not found at {path}."
    except Exception as e:
        return f"Read Error: {str(e)}"

def write_project_file(filename, content):
    """Writes content to a file, creating directories if needed."""
    path = get_safe_path(filename)
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {filename}"
    except Exception as e:
        return f"Write Error: {str(e)}"

def list_project_files():
    """Returns a filtered list of project files to keep the AI's context clean."""
    try:
        root_path = Path(PROJECT_ROOT)
        valid_extensions = {'.py', '.md', '.txt', '.json', '.sql'}
        ignore_dirs = {'.git', 'venv', '__pycache__', '.pytest_cache', 'node_modules'}
        
        file_list = []
        
        # Fix 2B: Using Pathlib.rglob for robust file discovery
        for file_path in root_path.rglob('*'):
            # Skip if any part of the file's path contains an ignored directory
            if any(ignored in file_path.parts for ignored in ignore_dirs):
                continue
                
            if file_path.is_file() and file_path.suffix in valid_extensions:
                # Store the relative path to keep the context short for the LLM
                file_list.append(str(file_path.relative_to(root_path)))
                
        return file_list
    except Exception as e:
        return [f"List Error: {str(e)}"]

def run_project_code(filename):
    """Runs a Python script using the project's virtual environment."""
    path = get_safe_path(filename)
    if not path.endswith(".py"):
        return "Error: Can only execute .py files."
    
    # Fix 2B: Use sys.executable to run code with the exact same binary that launched the agent
    python_exe = sys.executable

    try:
        result = subprocess.run(
            [python_exe, path],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=PROJECT_ROOT
        )
        output = result.stdout if result.stdout else "No output."
        errors = result.stderr if result.stderr else "No errors."
        return f"STDOUT: {output}\nSTDERR: {errors}"
    except subprocess.TimeoutExpired:
        return "Error: Execution timed out (15s)."
    except Exception as e:
        return f"Execution Error: {str(e)}"