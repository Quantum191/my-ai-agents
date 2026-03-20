import os
import subprocess

# --- HARDCODED ABSOLUTE PATH ---
PROJECT_ROOT = "/home/sean/my-ai-agents"

def get_abs_path(filename):
    """Ensures the AI is always looking in the exact right folder."""
    safe_path = os.path.abspath(os.path.join(PROJECT_ROOT, filename))
    # Security check so the AI can't read your personal Arch Linux system files
    if not safe_path.startswith(PROJECT_ROOT):
        return PROJECT_ROOT
    return safe_path

def list_project_files():
    """Returns a list of all files so the AI knows what exists."""
    files_list = []
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Ignore the sandbox and hidden git folders
        if '.git' in root or '__pycache__' in root or 'venv' in root:
            continue
        for file in files:
            if file.endswith('.py') or file.endswith('.txt') or file.endswith('.log'):
                rel_path = os.path.relpath(os.path.join(root, file), PROJECT_ROOT)
                files_list.append(rel_path)
    return "\n".join(files_list) if files_list else "No files found."

def read_project_file(filename):
    """Reads the exact file off the hard drive."""
    file_path = get_abs_path(filename)
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return f"System Error: The file {filename} does not exist in {PROJECT_ROOT}."
    except Exception as e:
        return f"System Error reading file: {str(e)}"

def write_project_file(filename, content):
    """Writes code to the exact folder."""
    file_path = get_abs_path(filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        return f"Success: Wrote to {filename}"
    except Exception as e:
        return f"System Error writing file: {str(e)}"

def run_project_code(filename):
    """Runs the code using your Virtual Environment."""
    file_path = get_abs_path(filename)
    if not os.path.exists(file_path):
        return f"System Error: Cannot run {filename} because it does not exist."
    
    try:
        # Forces the AI to use your safe sandbox to run code!
        python_exec = os.path.join(PROJECT_ROOT, "venv", "bin", "python")
        result = subprocess.run(
            [python_exec, file_path], 
            capture_output=True, 
            text=True, 
            timeout=15
        )
        output = result.stdout
        if result.stderr:
            output += f"\nErrors:\n{result.stderr}"
        return output.strip() if output.strip() else "Script ran successfully (no output)."
    except subprocess.TimeoutExpired:
        return "System Error: Script timed out after 15 seconds. It might be in an infinite loop."
    except Exception as e:
        return f"System Error running script: {str(e)}"
