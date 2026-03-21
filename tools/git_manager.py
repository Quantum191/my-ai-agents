import subprocess
import logging

logger = logging.getLogger("GitManager")

def run_git_command(command_string):
    """Executes a git command in the shell and returns the output."""
    if not command_string:
        return "Error: No git command provided by the AI."
        
    # Prevent the AI from accidentally running 'git git init'
    if command_string.startswith("git "):
        command_string = command_string[4:]
        
    full_command = f"git {command_string}"
    
    try:
        # shell=True allows us to handle complex quotes in commit messages safely
        result = subprocess.run(
            full_command, 
            shell=True, 
            capture_output=True, 
            text=True
        )
        
        output = result.stdout.strip()
        error = result.stderr.strip()
        
        # If the command succeeded (return code 0)
        if result.returncode == 0:
            return output if output else "Command executed successfully (no output)."
        else:
            # If git threw an error (like 'not a git repository')
            return f"Git Error (Code {result.returncode}): {error}\n{output}"
            
    except Exception as e:
        logger.error(f"Failed to execute git command: {e}")
        return f"System Execution Error: {str(e)}"

def git_sync():
    """Helper function to pull and push updates to the cloud."""
    try:
        pull = subprocess.run("git pull", shell=True, capture_output=True, text=True)
        push = subprocess.run("git push", shell=True, capture_output=True, text=True)
        
        out = ""
        if pull.stdout: out += f"Pull: {pull.stdout.strip()}\n"
        if push.stdout: out += f"Push: {push.stdout.strip()}\n"
        
        return out if out else "Sync completed successfully."
    except Exception as e:
        return f"Sync Error: {str(e)}"
