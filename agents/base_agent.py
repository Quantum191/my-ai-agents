import requests
import os
import json
import logging
import re
from datetime import datetime
from memory.memory_manager import AgentMemory
# Import the new make_directory tool
from tools.file_manager import read_project_file, list_project_files, write_project_file, run_project_code, make_directory
from tools.system_stats import get_system_stats

class CoderAgent:
    def __init__(self, name):
        self.name = name
        self.model = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
        self.url = os.getenv("OLLAMA_CHAT_URL", "http://localhost:11434/api/chat")
        self.memory = AgentMemory()
        self.http_session = requests.Session()

    def extract_json(self, text):
        try:
            match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
            return json.loads(match.group(1)) if match else json.loads(text)
        except: return None

    def set_status(self, text):     
        try:
            # ABSOLUTE PATH is key here
            path = "/home/sean/my-ai-agents/memory/status.txt"
            with open(path, "w", encoding='utf-8') as f:
                f.write(text)
        except Exception as e:
            pass    

    def ask_ai(self, prompt):
        step = 1
        last_obs = "None."
        action_history = []

        while step <= 15: # Limit steps for web performance
            past_memories = self.memory.recall_recent_interactions(limit=3)
            files = str(list_project_files())[:500] # type: ignore

            system_msg = (
                f"You are {self.name}. You must output JSON.\n"
                "Tools: write, read, mkdir, run, stats, answer.\n"
                f"Files: {files}\n"
                "Format: {\"action\": \"tool_name\", \"filename\": \"name\", \"code\": \"content\", \"text\": \"msg\"}\n"
                "--- RULES ---\n"
                "1. To create a folder, use action: 'mkdir' with filename: 'folder_name'.\n"
                "2. To create a file inside a folder, use 'write' with filename: 'folder/file.py'.\n"
            )

            try:
                res = self.http_session.post(self.url, json={
                    "model": self.model, 
                    "messages": [
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": f"TASK: {prompt}\nLAST OBS: {last_obs}"}
                    ], 
                    "stream": False
                }, timeout=90)
                
                data = self.extract_json(res.json().get("message", {}).get("content", ""))
                if not data: break

                action = str(data.get("action", "")).lower()
                if action == "answer":
                    return data.get("text", "Task Complete.")

                # TOOL ROUTING
                if action == "mkdir":
                    last_obs = make_directory(data.get("filename"))
                elif action == "write":
                    last_obs = write_project_file(data.get("filename"), data.get("code") or data.get("command"))
                elif action == "stats":
                    last_obs = get_system_stats()
                elif action == "run":
                    last_obs = run_project_code(data.get("filename") or data.get("command"))
                elif action == "read":
                    last_obs = read_project_file(data.get("filename"))

            except Exception as e:
                last_obs = f"Error: {str(e)}"
            
            step += 1
        return "Task timed out or failed."

my_agent = CoderAgent("Dev-01")