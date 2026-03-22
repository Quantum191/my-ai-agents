import psutil
import json
import os

def get_system_stats():
    ROOT = "/home/sean/my-ai-agents"
    STATUS_FILE = os.path.join(ROOT, "memory", "status.txt")
    LOG_FILE = os.path.join(ROOT, "memory", "agent.log")
    TARGET_JSON = os.path.join(ROOT, "Website", "stats.json")

    try:
        # Hardware Use
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        storage = psutil.disk_usage('/').percent
        
        # --- NEW: THERMAL SENSORS ---
        cpu_temp = "N/A"
        gpu_temp = "N/A"
        
        # Fetch CPU Temp
        if hasattr(psutil, "sensors_temperatures"):
            temps = psutil.sensors_temperatures()
            if temps:
                # Look for common Linux CPU thermal labels
                for name in ['coretemp', 'k10temp', 'cpu_thermal', 'acpitz']:
                    if name in temps and len(temps[name]) > 0:
                        cpu_temp = round(temps[name][0].current)
                        break
                # Fallback if specific name isn't found
                if cpu_temp == "N/A":
                    first_key = list(temps.keys())[0]
                    cpu_temp = round(temps[first_key][0].current)

        # Fetch GPU Temp (Try NVIDIA first, fallback to AMD)
        try:
            import subprocess
            nv_output = subprocess.check_output(['nvidia-smi', '--query-gpu=temperature.gpu', '--format=csv,noheader'], timeout=2)
            gpu_temp = int(nv_output.decode('utf-8').strip())
        except:
            if hasattr(psutil, "sensors_temperatures") and 'amdgpu' in temps and len(temps['amdgpu']) > 0:
                gpu_temp = round(temps['amdgpu'][0].current)

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
                    clean_lines = []
                    
                    for line in all_lines:
                        if not line.strip(): continue
                        if "HTTP/1.1" in line or "127.0.0.1" in line: continue
                        clean_lines.append(line.strip())
                        
                    logs = clean_lines[-15:]
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
            "logs": logs,
            "cpu_temp": cpu_temp, # Added Thermal Data
            "gpu_temp": gpu_temp  # Added Thermal Data
        }

        with open(TARGET_JSON, "w") as f:
            json.dump(data, f)
            
        return f"SUCCESS: Status updated to '{current_status}'"

    except Exception as e:
        return f"STATS ERROR: {str(e)}"