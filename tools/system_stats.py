import psutil
import json
import os

def get_system_stats():
    ROOT = "/home/sean/my-ai-agents"
    STATUS_FILE = os.path.join(ROOT, "memory", "status.txt")
    LOG_FILE = os.path.join(ROOT, "memory", "agent.log")
    TARGET_JSON = os.path.join(ROOT, "Website", "stats.json")

    try:
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        storage = psutil.disk_usage('/').percent
        
        cpu_temp = "N/A"
        gpu_temp = "N/A"
        
        if hasattr(psutil, "sensors_temperatures"):
            temps = psutil.sensors_temperatures()
            if temps:
                for name in ['coretemp', 'k10temp', 'cpu_thermal', 'acpitz']:
                    if name in temps and len(temps[name]) > 0:
                        cpu_temp = round(temps[name][0].current)
                        break

        try:
            import subprocess
            nv_output = subprocess.check_output(['nvidia-smi', '--query-gpu=temperature.gpu', '--format=csv,noheader'], timeout=2)
            gpu_temp = int(nv_output.decode('utf-8').strip())
        except:
            if hasattr(psutil, "sensors_temperatures") and 'amdgpu' in temps and len(temps['amdgpu']) > 0:
                gpu_temp = round(temps['amdgpu'][0].current)

        current_status = "Idle"
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE, "r") as f:
                current_status = f.read().strip() or "Idle"

        logs = []
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f:
                all_lines = f.readlines()
                clean_lines = [line.strip() for line in all_lines if line.strip() and "HTTP/1.1" not in line]
                # UPDATED: Now pulling the last 100 lines for deep scrolling
                logs = clean_lines[-100:] 
        
        data = {
            "cpu": cpu, "ram": ram, "status": current_status, "gpu": "N/A",
            "storage": storage, "logs": logs, "cpu_temp": cpu_temp, "gpu_temp": gpu_temp
        }

        with open(TARGET_JSON, "w") as f:
            json.dump(data, f)
            
        return f"SUCCESS: Log history expanded to 100 lines."

    except Exception as e:
        return f"STATS ERROR: {str(e)}"