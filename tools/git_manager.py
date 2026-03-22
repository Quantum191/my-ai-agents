import subprocess
import os

def run_git_command(command_string):
    """Executes a git command and returns the output or error."""
    try:
        # Split the command string into a list for subprocess
        # e.g., "add ." -> ["git", "add", "."]
        cmd = ["git"] + command_string.split()
        
        # We set an environment variable to prevent git from 
        # hanging on password/credential prompts.
        env = os.environ.copy()
        env["GIT_TERMINAL_PROMPT"] = "0"

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False, # We handle the error ourselves
            env=env
        )

        if result.returncode == 0:
            return f"SUCCESS: {result.stdout.strip() if result.stdout else 'Command executed.'}"
        else:
            # If it fails, we return the specific error message from git
            return f"GIT ERROR: {result.stderr.strip()}"

    except Exception as e:
        return f"SYSTEM ERROR: Could not run git: {str(e)}"

def git_sync():
    """A helper to add, commit, and push in one go."""
    add_res = run_git_command("add .")
    if "ERROR" in add_res: return add_res
    
    commit_res = run_git_command("commit -m 'Automated update from DEV-01 Dashboard'")
    if "nothing to commit" in commit_res.lower():
        return "SUCCESS: No changes to commit."
    if "ERROR" in commit_res: return commit_res
    
    push_res = run_git_command("push")
    return push_res
