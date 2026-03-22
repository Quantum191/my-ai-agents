import subprocess
import os

def run_bash_command(command, cwd="/home/sean/my-ai-agents"):
    """Runs a bash command and returns the output safely."""
    
    # Block interactive commands that would freeze the background agent
    blocked_commands = ['nano ', 'vim ', 'top', 'htop', 'less ', 'more ']
    if any(blocked in command for blocked in blocked_commands):
        return "ERROR: Interactive commands (like nano or top) are not allowed. Use 'write' or 'read' tools for files."

    try:
        # Run the command with a strict 30-second timeout
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout.strip()
        error = result.stderr.strip()
        
        # Combine output and error, and truncate to 1000 characters so it doesn't overwhelm the AI
        if result.returncode == 0:
            final_res = output if output else "Command executed silently with no output."
            return f"SUCCESS:\n{final_res}"[:1000]
        else:
            final_err = error if error else "Unknown error occurred."
            return f"FAILED (Exit {result.returncode}):\n{final_err}"[:1000]
            
    except subprocess.TimeoutExpired:
        return "ERROR: Command timed out after 30 seconds."
    except Exception as e:
        return f"CRITICAL ERROR: {str(e)}"
