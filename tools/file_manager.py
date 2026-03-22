import os
import subprocess

# Adjust this if your project is in a different directory
BASE_DIR = "/home/sean/my-ai-agents"

def read_project_file(filename):
    """Reads a file from the project directory."""
    try:
        path = os.path.join(BASE_DIR, filename)
        if not os.path.exists(path):
            return f"Error: File {filename} not found."
        with open(path, "r", encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def write_project_file(filename, content):
    """Writes/Overwrites a file in the project directory."""
    try:
        path = os.path.join(BASE_DIR, filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding='utf-8') as f:
            f.write(content)
        return f"SUCCESS: {filename} written to disk."
    except Exception as e:
        return f"Error writing file: {str(e)}"

def list_project_files():
    """Lists all files in the project, excluding hidden ones and venv."""
    files_list = []
    for root, dirs, files in os.walk(BASE_DIR):
        # Skip the virtual environment and git folders to save tokens
        dirs[:] = [d for d in dirs if d not in ['venv', '.git', '__pycache__', 'node_modules']] # type: ignore
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), BASE_DIR)
            files_list.append(rel_path)
    return files_list

def run_project_code(filename):
    """Runs a python file using the virtual environment if available."""
    try:
        path = os.path.join(BASE_DIR, filename)
        if not path.endswith(".py"):
            return "Error: Only .py files can be executed."
        
        if not os.path.exists(path):
            return f"Error: {filename} not found."

        # CHECK FOR VIRTUAL ENVIRONMENT
        venv_python = os.path.join(BASE_DIR, "venv", "bin", "python")
        python_executable = venv_python if os.path.exists(venv_python) else "python3"

        # Execute the code
        result = subprocess.run(
            [python_executable, path],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            return f"OUTPUT:\n{result.stdout}"
        else:
            return f"EXECUTION ERROR:\n{result.stderr}"

    except subprocess.TimeoutExpired:
        return "Error: Execution timed out after 30 seconds."
    except Exception as e:
        return f"System Error: {str(e)}"

def make_directory(folder_name):
    """Creates a new directory in the project root."""
    try:
        path = os.path.join(BASE_DIR, folder_name)
        os.makedirs(path, exist_ok=True)
        return f"SUCCESS: Directory '{folder_name}' created at {path}"
    except Exception as e:
        return f"Error creating directory: {str(e)}"

def write_project_file(filename, content):
    """Writes/Overwrites a file. Now ensures the subfolder exists first."""
    try:
        path = os.path.join(BASE_DIR, filename)
        # Automatically create the parent folders if they don't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding='utf-8') as f:
            f.write(content)
        return f"SUCCESS: {filename} written."
    except Exception as e:
        return f"Error writing file: {str(e)}"