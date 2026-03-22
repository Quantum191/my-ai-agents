import subprocess
import os

def get_system_stats():
    """Gathers the metrics for the 4070 and CPU."""
    gpu_util, gpu_temp = 0, 0
    try:
        cmd = ["nvidia-smi", "--query-gpu=utilization.gpu,temperature.gpu", "--format=csv,noheader,nounits"]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        parts = res.stdout.strip().split(',')
        gpu_util = int(parts[0].strip())
        gpu_temp = int(parts[1].strip())
    except:
        pass

    cpu_util = 0
    try:
        cpu_util = float(os.popen("top -bn1 | grep 'Cpu(s)' | awk '{print $2 + $4}'").read().strip())
    except:
        cpu_util = 0

    return {
        "cpu": cpu_util,
        "ram": 45, # Placeholder
        "gpu": gpu_util,
        "gpu_temp": gpu_temp,
        "status": "SYSTEM_OPERATIONAL",
        "logs": [f"NVIDIA_4070: {gpu_util}%", f"CORE_TEMP: {gpu_temp}C"]
    }