import subprocess
import shlex
import os

PROJECT_ROOT = "/home/sean/my-ai-agents"

def run_docker_command(command):
    """Executes a Docker command safely."""
    # SECURITY 1: Only allow docker commands
    if not (command.startswith("docker ") or command.startswith("docker-compose ")):
        return "Security Error: This tool can only run 'docker' or 'docker-compose'."
    
    # SECURITY 2: Block apocalyptic commands just in case it hallucinates
    blocked_patterns = ["system prune -a", "rm -f $(docker ps", "stop $(docker ps"]
    for pattern in blocked_patterns:
        if pattern in command:
            return f"Security Error: The command pattern '{pattern}' is blocked for your safety."
    
    try:
        cmd_list = shlex.split(command)
        
        # We give Docker 120 seconds because pulling new images from the web takes time
        result = subprocess.run(
            cmd_list,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=120
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
