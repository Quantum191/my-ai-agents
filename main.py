import curses
import time
import psutil
import subprocess
import os
from agents.base_agent import my_agent

# --- THE NUCLEAR OPTION: HARDCODED PATH ---
STATUS_FILE = "/home/sean/my-ai-agents/memory/status.txt"

def get_gpu_temperature():
    try:
        result = subprocess.check_output(
            ['nvidia-smi', '--query-gpu=temperature.gpu', '--format=csv,noheader,nounits'], 
            text=True, stderr=subprocess.DEVNULL
        )
        return f"{result.strip()}°C"
    except Exception:
        return "N/A"

def get_cpu_temperature():
    try:
        temps = psutil.sensors_temperatures()
        if 'coretemp' in temps:
            return f"{temps['coretemp'][0].current}°C"
        elif 'k10temp' in temps: 
            return f"{temps['k10temp'][0].current}°C"
        return "N/A"
    except Exception:
        return "N/A"

def run_dashboard(stdscr):
    curses.curs_set(0) 
    stdscr.nodelay(1)  
    stdscr.timeout(100) 

    os.makedirs("/home/sean/my-ai-agents/memory", exist_ok=True)
    if not os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "w") as f:
            f.write("Idle")

    while True:
        stdscr.clear()
        
        cpu_usage = f"{psutil.cpu_percent()}%"
        ram_usage = f"{psutil.virtual_memory().percent}%"
        cpu_temp = get_cpu_temperature()
        gpu_temp = get_gpu_temperature()

        try:
            memories_saved = my_agent.memory.get_count()
        except:
            memories_saved = 0
            
        # READ FROM EXACT HARDCODED PATH
        try:
            with open(STATUS_FILE, "r") as f:
                status = f.read().strip()
                if not status:
                    status = "Idle"
        except Exception:
            status = "Idle"
        
        try:
            stdscr.addstr(0, 0, "╔════════════════════════════════╗")
            stdscr.addstr(1, 0, "║   AI AGENT SYSTEM MONITOR      ║")
            stdscr.addstr(2, 0, "╠════════════════════════════════╣")
            stdscr.addstr(3, 0, f"║ CPU Usage:       {cpu_usage:>13} ║")
            stdscr.addstr(4, 0, f"║ CPU Temp:        {cpu_temp:>13} ║")
            stdscr.addstr(5, 0, f"║ RAM Usage:       {ram_usage:>13} ║")
            stdscr.addstr(6, 0, f"║ GPU Temp:        {gpu_temp:>13} ║")
            stdscr.addstr(7, 0, "╠════════════════════════════════╣")
            stdscr.addstr(8, 0, f"║ MEMORIES SAVED:  {memories_saved:>13} ║")
            
            display_status = status[:14] 
            stdscr.addstr(9, 0, f"║ AGENT STATUS: {display_status:<16} ║")

            if "Step" in status:
                try:
                    current_step = int(status.split()[2].split('/')[0])
                    progress = "█" * current_step + "░" * (10 - current_step)
                    stdscr.addstr(10, 0, f"╟─ Progress: [{progress}] ──╢")
                except:
                    stdscr.addstr(10, 0, "╟────────────────────────────────╢")
            else:
                stdscr.addstr(10, 0, "╟────────────────────────────────╢")

            stdscr.addstr(11, 0, "║ LAST RESPONSE:                 ║")
            
            recent_context = my_agent.memory.get_recent_context(limit=1)
            last_response = recent_context.split("AI: ")[-1].strip() if "AI: " in recent_context else "None"
            
            clean_response = last_response.replace('\n', ' ')[:30]
            stdscr.addstr(12, 0, f"║ {clean_response:<30} ║")
            stdscr.addstr(13, 0, "╚════════════════════════════════╝")
            
            stdscr.addstr(15, 0, " System Active (10 FPS Scroll) ")
            stdscr.addstr(16, 0, " Press Ctrl+C to exit. ")

        except curses.error:
            pass

        stdscr.refresh()

        c = stdscr.getch()
        if c == ord('q'):
            break

if __name__ == "__main__":
    try:
        curses.wrapper(run_dashboard)
    except KeyboardInterrupt:
        print("\n[!] Dashboard Offline.")
