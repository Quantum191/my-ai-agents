import time
import os
from tools.system_stats import get_system_stats

print("🚀 DEV-01 Live Stats Daemon Started...")
print(f"Current Working Directory: {os.getcwd()}")
print("Checking for Website/stats.json...")

try:
    while True:
        # Call the tool and capture the return message
        status_msg = get_system_stats()
        
        # Print the timestamp and the result so we can see it working
        timestamp = time.strftime('%H:%M:%S')
        print(f"[{timestamp}] {status_msg}")
        
        # Wait 2 seconds before the next update
        time.sleep(2)
except KeyboardInterrupt:
    print("\nStopping Daemon...")
except Exception as e:
    print(f"DAEMON CRASHED: {e}")