import sys
from agents.base_agent import my_agent

def main():
    # Check if the user provided a prompt
    if len(sys.argv) < 2:
        print("Usage: python cli.py \"Your prompt here\"")
        sys.exit(1)

    # Get the prompt from the command line arguments
    prompt = sys.argv[1]
    
    print(f"\n[DEV-01] Received Task: {prompt}")
    print("[DEV-01] Working... (Check your dashboard for progress)\n")
    
    # Send it directly to our newly updated agent
    final_result = my_agent.ask_ai(prompt)
    
    print(f"\n[DEV-01] Task Complete. Final Output:\n{final_result}\n")

if __name__ == "__main__":
    main()
