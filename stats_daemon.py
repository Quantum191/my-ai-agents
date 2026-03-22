import time
import json
import os
from tools.system_stats import get_system_stats

STATS_FILE = "stats.json"

def run_daemon():
    print("🚀 Stats Daemon Started...")
    print(f"Updating {STATS_FILE} every 2 seconds. Press Ctrl+C to stop.")
    
    while True:
        try:
            # 1. Collect latest data
            data = get_system_stats()
            
            # 2. Write to JSON file
            with open(STATS_FILE, 'w') as f:
                json.dump(data, f, indent=4)
            
            # 3. Small console heartbeat so you know it's working
            # Use \r to overwrite the same line in the terminal
            print(f"\r[HEARTBEAT] GPU: {data['gpu']}% | CPU: {data['cpu']}%", end="")
            
            time.sleep(2)
            
        except KeyboardInterrupt:
            print("\n👋 Daemon stopped by user.")
            break
        except Exception as e:
            print(f"\n❌ Error in daemon: {e}")
            time.sleep(5) # Wait a bit before retrying on error

if __name__ == "__main__":
    run_daemon()