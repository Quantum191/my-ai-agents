import os
import subprocess

# Set the absolute path for your Arch Linux environment
PROJECT_ROOT = "/home/sean/my-ai-agents"

def get_safe_path(filename):
    """Ensures all file operations stay within the project directory."""
    if not filename or not isinstance(filename, str):
        # Return a dummy path that doesn't exist instead of crashing
        return os.path.join(PROJECT_ROOT, "MISSING_FILENAME_ERROR")
    
    if filename.startswith(PROJECT_ROOT):
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
    file_list = []
    # Only show these extensions to keep the agent focused
    valid_extensions = ('.py', '.md', '.txt', '.json', '.sql')
    # Folders to completely ignore
    ignore_dirs = {'.git', 'venv', '__pycache__', '.pytest_cache', 'node_modules'}

    try:
        for root, dirs, filenames in os.walk(PROJECT_ROOT):
            # Modify dirs in-place to skip ignored folders
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for f in filenames:
                if f.endswith(valid_extensions):
                    full_path = os.path.join(root, f)
                    file_list.append(os.path.relpath(full_path, PROJECT_ROOT))
        return file_list
    except Exception as e:
        return [f"List Error: {str(e)}"]

def run_project_code(filename):
    """Runs a Python script using the project's virtual environment."""
    path = get_safe_path(filename)
    if not path.endswith(".py"):
        return "Error: Can only execute .py files."
    
    # Use the venv python to ensure dependencies are found
    python_exe = os.path.join(PROJECT_ROOT, "venv/bin/python")
    if not os.path.exists(python_exe):
        python_exe = "python3" # Fallback if venv is missing

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
