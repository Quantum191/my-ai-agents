import subprocess
import os
import shlex

# Fix 2A: Dynamic Root Normalization
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def run_git_command(command):
    """Runs a raw git command safely within the project root."""
    if not command.startswith("git "):
        return "Security Error: Only 'git' commands are allowed."
    
    # Security enhancement: Prevent shell injection
    forbidden_chars = ['|', '>', '<', '&', ';']
    if any(char in command for char in forbidden_chars):
        return "Security Error: Shell operators are strictly forbidden."

    try:
        # Securely parse the command string into a list
        cmd_list = shlex.split(command)
        
        res = subprocess.run(
            cmd_list, 
            cwd=PROJECT_ROOT, 
            shell=False,  # Security: No shell execution
            capture_output=True, 
            text=True, 
            timeout=30
        )
        
        output = res.stdout.strip()
        error = res.stderr.strip()
        
        if res.returncode == 0:
            return output if output else f"Successfully executed: {command}"
        else:
            return f"Git Error:\n{error}"
            
    except ValueError as e:
        return f"Parse Error: Could not parse command string properly: {e}"
    except subprocess.TimeoutExpired:
        return "Git Error: Command timed out after 30 seconds."
    except Exception as e:
        return f"Execution Error: {str(e)}"

def git_sync():
    """Performs a fetch and pull to stay in sync with remote changes robustly."""
    try:
        # 1. Fetch the latest metadata from GitHub
        fetch_res = run_git_command("git fetch origin")
        if "Git Error:" in fetch_res:
            return f"Failed to fetch from origin:\n{fetch_res}"
        
        # Fix 2D: Robust Git Sync using rev-list instead of fragile string matching
        # This returns the exact number of commits we are behind origin/main
        rev_check = run_git_command("git rev-list HEAD..origin/main --count")
        
        if "Git Error:" in rev_check:
            return f"Failed to check revision history:\n{rev_check}"
            
        # Parse the integer safely
        behind_count = int(rev_check.strip()) if rev_check.strip().isdigit() else 0
        
        if behind_count > 0:
            # 3. Pull the changes down
            pull = run_git_command("git pull origin main")
            return f"Sync Complete: Pulled {behind_count} new commit(s) from cloud.\n{pull}"
        else:
            return "Sync Check: Local version is already up to date."
            
    except Exception as e:
        return f"Sync Error: {str(e)}"