import psutil
import json
import os
import subprocess

def get_system_stats():
    """Fetches hardware stats AND the agent's current status."""
    try:
        # 1. Hardware
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        
        # 2. Read Agent Status (The 'Step 1/15' part)
        status_path = "/home/sean/my-ai-agents/memory/status.txt"
        agent_status = "Idle" # Default
        if os.path.exists(status_path):
            with open(status_path, "r") as f:
                agent_status = f.read().strip()

        # 3. Read Logs
        log_path = "/home/sean/my-ai-agents/memory/agent.log"
        logs = []
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                logs = f.readlines()[-5:] # type: ignore

        stats_data = {
            "cpu": cpu,
            "ram": ram,
            "gpu": "N/A",
            "storage": psutil.disk_usage('/').percent,
            "status": agent_status, # <-- NEW: Sending status to the web
            "logs": [line.strip() for line in logs]
        }

        # 4. Save to Website
        target_path = "/home/sean/my-ai-agents/Website/stats.json"
        with open(target_path, "w") as f:
            json.dump(stats_data, f)
            
        return f"SUCCESS: Status is {agent_status}"

    except Exception as e:
        return f"ERROR: {str(e)}"