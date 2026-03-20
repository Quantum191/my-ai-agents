import subprocess
import os
import shlex

# Hardcoded safe path
PROJECT_ROOT = "/home/sean/my-ai-agents"

def run_git_command(command):
    """Executes a git command safely in the project root."""
    # SECURITY: Force the command to only be a git command
    if not command.startswith("git "):
        return "Security Error: This tool can only run 'git' commands."
    
    try:
        # THE FIX: Use shlex.split to keep quoted sentences together!
        cmd_list = shlex.split(command)
        
        result = subprocess.run(
            cmd_list,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        output = result.stdout.strip()
        error = result.stderr.strip()
        
        if result.returncode == 0:
            return output if output else "Command successful (no output)."
        else:
            return f"Git Error:\n{error}"
            
    except Exception as e:
        return f"System Error running git: {str(e)}"
