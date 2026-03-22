import requests
import os
import json
import re
from datetime import datetime
from memory.memory_manager import AgentMemory
from tools.file_manager import read_project_file, list_project_files, write_project_file, run_project_code, make_directory
from tools.git_manager import run_git_command
from tools.system_stats import get_system_stats

class CoderAgent:
    def __init__(self, name):
        self.name = name
        self.model = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
        self.url = "http://localhost:11434/api/chat"
        self.status_path = "/home/sean/my-ai-agents/memory/status.txt"
        
        # Ensure memory is initialized
        self.memory = AgentMemory()
        self.http_session = requests.Session()

    def set_status(self, text):
        try:
            with open(self.status_path, "w") as f:
                f.write(text)
                f.flush()
                os.fsync(f.fileno())
        except: pass

    def extract_json(self, text):
        try:
            match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
            return json.loads(match.group(1)) if match else json.loads(text)
        except: return None

    def ask_ai(self, prompt):
        step = 1
        last_obs = "None."
        self.set_status(f"Step 1/10: Thinking...")
        
        while step <= 10:
            past_memories = self.memory.recall_recent_interactions(limit=3)
            files = str(list_project_files())[:400]

            system_msg = (
                f"You are {self.name}. You MUST output JSON.\n"
                "Tools: mkdir, write, read, run, answer, git.\n"
                "Format: {\"action\": \"mkdir\", \"filename\": \"folder_name\"}"
            )

            try:
                res = self.http_session.post(self.url, json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": f"TASK: {prompt}\nOBS: {last_obs}"}
                    ],
                    "stream": False
                }, timeout=60)
                
                data = self.extract_json(res.json().get("message", {}).get("content", ""))
                if not data:
                    step += 1
                    continue

                action = data.get("action", "").lower()
                self.set_status(f"Step {step}/10: {action}...")

                if action == "answer":
                    self.memory.save_interaction(prompt, data.get("text", ""))
                    self.set_status("Idle")
                    return data.get("text", "Done.")

                # Tool Routing
                if action == "mkdir": last_obs = make_directory(data.get("filename"))
                elif action == "write": last_obs = write_project_file(data.get("filename"), data.get("code"))
                elif action == "git": last_obs = run_git_command(data.get("command"))
                elif action == "run": last_obs = run_project_code(data.get("filename"))
                
            except Exception as e:
                last_obs = f"Error: {e}"
            
            step += 1
        
        self.set_status("Idle")
        return "Task limit reached."

# Create the instance for both Terminal and Web use
my_agent = CoderAgent("Dev-01")