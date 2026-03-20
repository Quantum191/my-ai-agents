#!/usr/bin/env python3
import subprocess
import psutil
import json

def get_gpu_temperature():
    try:
        result = subprocess.check_output(['nvidia-smi', '--query-gpu=temperature.gpu', '--format=csv,noheader,nounits'], text=True)
        return int(result.strip())
    except Exception as e:
        print(f"Error getting GPU temperature: {e}")
        return None

def get_cpu_usage():
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        return cpu_percent
    except Exception as e:
        print(f"Error getting CPU usage: {e}")
        return None

if __name__ == '__main__':
    gpu_temp = get_gpu_temperature()
    cpu_usage = get_cpu_usage()
    health_data = {
        'gpu_temperature': gpu_temp,
        'cpu_usage': cpu_usage
    }
    print(json.dumps(health_data, indent=4))