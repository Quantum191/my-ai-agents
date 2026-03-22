import os
import subprocess

BASE_DIR = "/home/sean/my-ai-agents"

def list_project_files():
    files_list = []
    for root, dirs, files in os.walk(BASE_DIR):
        # Skip hidden folders like .git
        if '.git' in root: continue
        for file in files:
            full_path = os.path.relpath(os.path.join(root, file), BASE_DIR)
            files_list.append(full_path)
    return files_list

def read_project_file(filename):
    try:
        path = os.path.join(BASE_DIR, filename)
        with open(path, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def write_project_file(filename, code):
    try:
        path = os.path.join(BASE_DIR, filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(code)
        return f"SUCCESS: File {filename} written."
    except Exception as e:
        return f"Error writing file: {e}"

def make_directory(filename):
    try:
        path = os.path.join(BASE_DIR, filename)
        os.makedirs(path, exist_ok=True)
        return f"SUCCESS: Directory {filename} created."
    except Exception as e:
        return f"Error creating directory: {e}"

def run_project_code(filename):
    """ONLY for executing python scripts."""
    if not filename:
        return "Error: No filename provided for execution."
        
    if not filename.endswith(".py"):
        return f"Error: '{filename}' is not a .py file. If you are trying to run a terminal command (like ls or npm), you MUST use the 'bash' tool instead."

    try:
        path = os.path.join(BASE_DIR, filename)
        result = subprocess.run(["python3", path], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return f"SUCCESS:\n{result.stdout}"
        else:
            return f"FAILED:\n{result.stderr}"
    except Exception as e:
        return f"Error running code: {e}"