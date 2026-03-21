import requests
import os
import json
import re
import logging
from memory.memory_manager import AgentMemory
from tools.file_manager import read_project_file, list_project_files, write_project_file, run_project_code
from tools.web_search import search_web
from tools.git_manager import run_git_command, git_sync
from tools.docker_manager import run_docker_command

# Setup logging to a file so we don't lose track of errors
logging.basicConfig(
    filename='agent_debug.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class CoderAgent:
    def __init__(self, name, model=None):
        self.name = name
        # Extract hardcoded config to Environment Variables (Antigravity's suggestion)
        self.model = model or os.getenv("AGENT_MODEL", "qwen2.5-coder:7b")
        self.url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
        self.status_file = os.getenv("STATUS_FILE", "/home/sean/my-ai-agents/memory/status.txt")
        
        self.memory = AgentMemory()
        self.task_history = []
        self.set_status("Idle")

    def set_status(self, text):
        try:
            with open(self.status_file, "w") as f:
                f.write(text)
        except Exception as e:
            logging.error(f"Failed to write status: {e}")

    def extract_json(self, text):
        try:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            return json.loads(match.group()) if match else None
        except Exception as e:
            logging.error(f"JSON Parsing Error: {e} | Raw text: {text[:100]}")
            return None

    def ask_ai(self, user_goal):
        """Now using an Iterative Loop instead of Recursion."""
        step = 1
        max_steps = 20
        context_override = "Begin."
        
        while step <= max_steps:
            self.set_status(f"Step {step}/{max_steps}")
            
            history = "\n".join(self.task_history[-3:]) if self.task_history else "None"
            files = list_project_files()
            
            system_instructions = (
                f"You are {self.name}, a JSON-ONLY Arch Linux Engineer.\n"
                f"FILES: {files}\n"
                f"HISTORY: {history}\n\n"
                "RESPONSE: ONLY JSON. NO CHAT.\n"
                "{'action': 'read'|'write'|'answer'|'sync'|'run'|'git'|'docker'|'search', ...}"
            )
            
            payload = {
                "model": self.model,
                "prompt": f"{system_instructions}\n\nGOAL: {user_goal}\n\nDATA: {context_override}\n\nResponse:",
                "format": "json",
                "stream": False,
                "options": {"temperature": 0.1, "stop": ["Goal:", "Data:"]}
            }

            try:
                response = requests.post(self.url, json=payload, timeout=60).json()
                raw_text = response.get("response", "")
                data = self.extract_json(raw_text)

                if not data:
                    context_override = "System: Invalid JSON. Use {'action': 'answer', 'text': '...'}"
                    step += 1
                    continue

                action = data.get("action")
                
                # BREAK CONDITION: The agent provides the final answer
                if action == "answer":
                    final_text = data.get("text", "Done.")
                    self.memory.save_interaction(user_goal, final_text)
                    self.set_status("Idle")
                    return final_text
                
                # TOOL EXECUTION
                logging.info(f"Step {step}: Executing {action}")
                if action == "read": res = read_project_file(data.get("filename"))
                elif action == "write": res = write_project_file(data.get("filename"), data.get("code"))
                elif action == "run": res = run_project_code(data.get("filename"))
                elif action == "git": res = run_git_command(data.get("command"))
                elif action == "docker": res = run_docker_command(data.get("command"))
                elif action == "sync": res = git_sync()
                elif action == "search": res = search_web(data.get("query"))
                else: res = f"Unknown action: {action}"

                self.task_history.append(f"Step {step}: {action}")
                context_override = f"Result: {res}"
                step += 1

            except requests.exceptions.RequestException as e:
                logging.error(f"Network Error: {e}")
                return f"Error: Ollama connection failed. Check if it's running."
            except Exception as e:
                logging.error(f"Critical Loop Error: {e}")
                return f"Crash: {str(e)}"

        self.set_status("Idle")
        return "Error: 20 step limit reached."

my_agent = CoderAgent("Dev-01")
