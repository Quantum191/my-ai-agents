import curses
import time
import os
from agents.base_agent import my_agent

def run_dashboard(stdscr):
    # Setup curses
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(1000)

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        # Header
        stdscr.addstr(1, 2, "=== DEV-01 TERMINAL DASHBOARD ===", curses.A_BOLD)
        
        # Read Status
        status = "Unknown"
        if os.path.exists(my_agent.status_path):
            with open(my_agent.status_path, "r") as f:
                status = f.read().strip()
        
        stdscr.addstr(3, 2, f"SYSTEM STATUS: {status}")

        # RECENT CONTEXT (Fixed line for the error)
        stdscr.addstr(5, 2, "--- RECENT MEMORY ---", curses.A_DIM)
        try:
            # Changed from get_recent_context to recall_recent_interactions
            recent = my_agent.memory.recall_recent_interactions(limit=1)
            stdscr.addstr(6, 2, f"{str(recent)[:w-10]}")
        except:
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
        print("Dashboard closed.")