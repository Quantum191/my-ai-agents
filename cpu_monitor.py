import time
import os
from dashboard.utils.gpu_monitor import get_gpu_temperature
from dashboard.utils.cpu_monitor import get_cpu_stats

def run_dashboard():
    try:
        while True:
            # Clear the terminal screen
            os.system('clear')
            
            # Fetch data
            gpu_temp = get_gpu_temperature()
            cpu_usage, cpu_temp = get_cpu_stats()
            
            # Print Header
            print("="*30)
            print(" AI AGENT SYSTEM MONITOR ")
            print("="*30)
            
            # Print Stats
            print(f"CPU Usage: {cpu_usage:>6}%")
            print(f"CPU Temp:  {cpu_temp:>6}°C")
            print("-" * 30)
            print(f"GPU Temp:  {gpu_temp:>6}°C")
            print("="*30)
            print("\nPress Ctrl+C to exit")
            
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

if __name__ == "__main__":
    run_dashboard()import psutil

def get_cpu_stats():
    return f"{psutil.cpu_percent()}%"
