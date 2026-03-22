import psutil
import json
import os

def get_system_stats():
    ROOT = "/home/sean/my-ai-agents"
    STATUS_FILE = os.path.join(ROOT, "memory", "status.txt")
    LOG_FILE = os.path.join(ROOT, "memory", "agent.log")
    TARGET_JSON = os.path.join(ROOT, "Website", "stats.json")

    try:
        # Hardware
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        storage = psutil.disk_usage('/').percent
        
        # Status
        current_status = "Idle"
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    current_status = content

        # Logs
        logs = []
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "r") as f:
                    all_lines = f.readlines()
                    # Keep the last 15 lines, ignore empty lines
                    logs = [line.strip() for line in all_lines[-15:] if line.strip()]
            except Exception as e:
                logs = [f"Error reading logs: {str(e)}"]
        else:
            logs = ["LOG_SYSTEM_OFFLINE: agent.log file not found."]

        if not logs:
            logs = ["LOG_SYSTEM_EMPTY: Waiting for agent activity..."]

        # Final Payload
        data = {
            "cpu": cpu,
            "ram": ram,
            "status": current_status,
            "gpu": "N/A",
            "storage": storage,
            "logs": logs
        }

        with open(TARGET_JSON, "w") as f:
            json.dump(data, f)
            
        return f"SUCCESS: Status updated to '{current_status}'"

    except Exception as e:
        return f"STATS ERROR: {str(e)}"