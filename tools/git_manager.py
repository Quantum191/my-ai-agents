import subprocess
import os

PROJECT_ROOT = "/home/sean/my-ai-agents"

def run_git_command(command):
    """Runs a raw git command safely within the project root."""
    try:
        # Ensure we are in the right directory
        res = subprocess.run(
            command, 
            cwd=PROJECT_ROOT, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        return res.stdout + res.stderr
    except Exception as e:
        return str(e)

def git_sync():
    """Performs a fetch and pull to stay in sync with remote changes."""
    try:
        # 1. Fetch the latest metadata from GitHub
        fetch = run_git_command("git fetch origin")
        
        # 2. Check if we are behind the remote branch
        status = run_git_command("git status -uno")
        
        if "is behind" in status or "can be fast-forwarded" in status:
            # 3. Pull the changes down
            pull = run_git_command("git pull origin main")
            return f"Sync Complete: Changes pulled from cloud.\n{pull}"
        else:
            return "Sync Check: Local version is already up to date."
            
    except Exception as e:
        return f"Sync Error: {str(e)}"
