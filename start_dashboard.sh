#!/bin/bash

# --- 1. Cleanup Function ---
# This kills background tasks when you press Ctrl+C
cleanup() {
    echo -e "\n\n🛑 Shutting down Dashboard..."
    kill $DAEMON_PID $SERVER_PID
    exit
}

trap cleanup SIGINT

echo "🚀 Launching DEV-01 Dashboard Environment..."

# --- 2. Start the Stats Daemon ---
python stats_daemon.py &
DAEMON_PID=$!
echo "✅ Stats Daemon started (PID: $DAEMON_PID)"

# --- 3. Start the Web Server ---
# We use 'python app_server.py' to host the UI
python app_server.py &
SERVER_PID=$!
echo "✅ Web Server started (PID: $SERVER_PID)"

echo "------------------------------------------------"
echo "🌐 Dashboard live at: http://localhost:5000"
echo "🛠️  Press Ctrl+C to stop everything."
echo "------------------------------------------------"

# Keep the script running to catch the Ctrl+C
wait