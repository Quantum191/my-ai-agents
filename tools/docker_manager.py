import subprocess
import shlex
import os

# Fix 2A: Dynamic Root Normalization
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def run_docker_command(command):
    """Executes a Docker command safely using a strict whitelist."""
    
    # Fix 2C (Part 1): Block shell operators that break shlex.split or bypass security
    forbidden_chars = ['|', '>', '<', '&', ';']
    if any(char in command for char in forbidden_chars):
        return (
            "Security Error: Shell operators (|, >, <, &, ;) are strictly forbidden. "
            "Please run standard, single Docker commands without piping."
        )

    # SECURITY 1: Only allow docker commands
    if not (command.startswith("docker ") or command.startswith("docker-compose ")):
        return "Security Error: This tool can only run 'docker' or 'docker-compose'."
    
    try:
        cmd_list = shlex.split(command)
    except ValueError as e:
        return f"Parse Error: Could not parse command string properly: {e}"

    if len(cmd_list) < 2:
        return "Error: Incomplete Docker command."

    # Fix 2C (Part 2): Implement a Strict Whitelist instead of a weak blacklist
    # Find the main subcommand (the first argument that isn't a flag like -f or -d)
    subcommand = None
    for arg in cmd_list[1:]:
        if not arg.startswith('-'):
            subcommand = arg
            break

    allowed_subcommands = {
        # Standard Docker
        "ps", "build", "run", "logs", "inspect", "stop", "start", 
        "rm", "rmi", "pull", "images", "network", "volume",
        # Docker Compose (can be invoked as 'docker compose' or 'docker-compose')
        "compose", "up", "down"
    }

    if subcommand and subcommand not in allowed_subcommands:
         return (
             f"Security Error: The Docker subcommand '{subcommand}' is not in the whitelist. "
             "Dangerous commands like 'system prune' or arbitrary 'exec' are blocked."
         )

    try:
        # We give Docker 120 seconds because pulling new images from the web takes time
        result = subprocess.run(
            cmd_list,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=120,
            shell=False # Explicitly enforce no-shell execution for safety
        )
        
        output = result.stdout.strip()
        error = result.stderr.strip()
        
        if result.returncode == 0:
            return output if output else f"Successfully executed: {command}"
        else:
            return f"Docker Error:\n{error}"
            
    except subprocess.TimeoutExpired:
        return "Docker Error: Command timed out after 120 seconds. (Was it downloading a massive image?)"
    except Exception as e:
        return f"System Error running Docker: {str(e)}"