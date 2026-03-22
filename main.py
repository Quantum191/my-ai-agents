import curses
import time
import os
from agents.base_agent import my_agent

def run_dashboard(stdscr):
    # Setup curses
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(1000)

    last_mtime = 0
    status = "Unknown"

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        # Header
        stdscr.addstr(1, 2, "=== DEV-01 TERMINAL DASHBOARD ===", curses.A_BOLD)
        
        # Read Status (OPTIMIZED: Only read from disk if the file actually changed)
        if os.path.exists(my_agent.status_path):
            current_mtime = os.path.getmtime(my_agent.status_path)
            if current_mtime != last_mtime:
                with open(my_agent.status_path, "r") as f:
                    status = f.read().strip()
                last_mtime = current_mtime
        
        stdscr.addstr(3, 2, f"SYSTEM STATUS: {status}")

        # Recent Memory
        stdscr.addstr(5, 2, "--- RECENT MEMORY ---", curses.A_DIM)
        try:
            recent = my_agent.memory.recall_recent_interactions(limit=1)
            stdscr.addstr(6, 2, f"{str(recent)[:w-10]}")
        except Exception as e: # OPTIMIZED: Properly catch exceptions
            stdscr.addstr(6, 2, "No memory found.")

        stdscr.addstr(h-2, 2, "Press 'q' to quit")
        stdscr.refresh()

        # Input handling
        key = stdscr.getch()
        if key == ord('q'):
            break

if __name__ == "__main__":
    try:
        curses.wrapper(run_dashboard)
    except KeyboardInterrupt:
        print("Dashboard closed manually.")
    except Exception as e:
        print(f"Dashboard crashed safely: {e}")