#!/home/sean/my-ai-agents/venv/bin/python
import sys
import os
from dotenv import load_dotenv

# 1. Load environment variables from .env
load_dotenv()

# 2. Import the agent after loading env vars
try:
    from agents.base_agent import my_agent
except ImportError as e:
    print(f"Error: Could not import agent. Is your venv set up? {e}")
    sys.exit(1)

def main():
    # Check if a prompt was provided via command line
    if len(sys.argv) < 2:
        print("Usage: ask 'your question here'")
        sys.exit(1)

    user_query = sys.argv[1]
    
    print(f"\n[DEV-01] Received Task: {user_query}")
    print(f"[DEV-01] Working... (Check your dashboard for progress)\n")
    
    try:
        # Call the new iterative ask_ai function
        response = my_agent.ask_ai(user_query)
        
        print("\n[DEV-01] Task Complete. Final Output:")
        print(response)
    except Exception as e:
        print(f"\n[CLI Error] Something went wrong: {e}")

if __name__ == "__main__":
    main()
