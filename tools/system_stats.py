import psutil
import json
import os

def get_system_stats():
    """
    Bridges Agent telemetry and Hardware stats to the Web Dashboard.
    Uses absolute paths to ensure reliability on Arch Linux.
    """
    # 1. PATH CONFIGURATION
    ROOT = "/home/sean/my-ai-agents"
    STATUS_FILE = os.path.join(ROOT, "memory", "status.txt")
    LOG_FILE = os.path.join(ROOT, "memory", "agent.log")
    TARGET_JSON = os.path.join(ROOT, "Website", "stats.json")

    try:
        # 2. FETCH HARDWARE DATA
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        storage = psutil.disk_usage('/').percent
        
        # 3. FETCH AGENT STATUS (Idle vs. Step X/10)
        current_status = "Idle"
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    current_status = content

        # 4. FETCH AGENT LOGS (The "Thought Stream")
        # We grab the last 10 lines to keep the box populated but fast
        logs = []
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "r") as f:
                    # Read all lines and take the final 10
                    all_lines = f.readlines()
                    logs = [line.strip() for line in all_lines[-10:]]
            except Exception as log_error:
                logs = [f"Error reading logs: {str(log_error)}"]
        else:
            logs = ["Waiting for agent activity..."]

        # 5. CONSTRUCT DATA PAYLOAD
        # This dictionary must match the keys expected by Website/app.js
        data = {
            "cpu": cpu,
            "ram": ram,
            "status": current_status,
            "gpu": "N/A",
            "storage": storage,
            "logs": logs  # The "New Addition"
        }

        # 6. WRITE TO DISK (Atomic update for the Web Server)
        with open(TARGET_JSON, "w") as f:
            json.dump(data, f)
            
        return f"SUCCESS: Status updated to '{current_status}'"

    except Exception as e:
        return f"STATS ERROR: {str(e)}"