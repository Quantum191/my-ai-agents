import requests
import os
import json
import logging
import re
from memory.memory_manager import AgentMemory
from tools.file_manager import read_project_file, list_project_files, write_project_file, run_project_code
from tools.web_search import search_web
from tools.git_manager import run_git_command, git_sync
from tools.docker_manager import run_docker_command

# --- Setup Logging ---
LOG_LEVEL = os.getenv("AGENT_LOG_LEVEL", "INFO").upper()
AGENT_LOG_FILE = os.getenv("AGENT_LOG_FILE", "/home/sean/my-ai-agents/memory/agent.log")

logging.basicConfig(
    filename=AGENT_LOG_FILE,
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("CoderAgent")

class CoderAgent:
    def __init__(self, name):
        self.name = name
        self.model = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
        self.url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
        self.status_file = os.getenv("AGENT_STATUS_FILE", "/home/sean/my-ai-agents/memory/status.txt")
        self.max_steps = int(os.getenv("AGENT_MAX_STEPS", "20"))
        self.memory = AgentMemory()
        self.set_status("Idle")

    def set_status(self, text):
        try:
            with open(self.status_file, "w", encoding='utf-8') as f: 
                f.write(text)
        except Exception as e:
            logger.error("Failed to write to status file: %s", e)

    def clean_code(self, code_string):
        """Removes markdown code blocks if the LLM accidentally includes them."""
        if not code_string: return ""
        # Removes ```python ... ``` or just ``` ... ```
        return re.sub(r"```[a-zA-Z]*\n?|```", "", code_string).strip()

    def ask_ai(self, prompt):
        step = 1
        self.task_history = []
        # We start with the goal as the initial context
        current_observation = "System initialized. Waiting for first action."
        
        while step <= self.max_steps:
            self.set_status(f"Step {step}/{self.max_steps}")
            
            # Build a clear history of what was done
            history_summary = ""
            for i, h in enumerate(self.task_history):
                history_summary += f"\nStep {i+1}: You ran '{h['action']}' on '{h['param']}' -> Result: {h['result'][:100]}"

            files = list_project_files()
            
            system_prompt = (
                f"You are {self.name}, an expert DevOps agent on Arch Linux. You speak ONLY JSON.\n"
                f"OBJECTIVE: {prompt}\n"
                f"FILES IN DIRECTORY: {files}\n"
                f"COMPLETED WORK: {history_summary if history_summary else 'None'}\n\n"
                "TOOLS:\n"
                "- 'write': { \"action\": \"write\", \"filename\": \"<name>\", \"code\": \"<content>\" }\n"
                "- 'run': { \"action\": \"run\", \"command\": \"<filename_or_cmd>\" }\n"
                "- 'read', 'search', 'git', 'docker', 'sync'\n"
                "- 'answer': { \"action\": \"answer\", \"text\": \"<final_summary>\" }\n\n"
                "CRITICAL RULES:\n"
                "1. DO NOT use the example values (like 'test.py'). Use the values requested in the OBJECTIVE.\n"
                "2. You MUST execute 'write' before you can 'run' a new file.\n"
                "3. ALWAYS output valid JSON. No conversational filler."
            )
            
            payload = {
                "model": self.model,
                "prompt": f"{system_prompt}\n\nLast Observation: {current_observation}\n\nNext Action (JSON):",
                "format": "json",
                "stream": False,
                "options": {"temperature": 0.0} # Set to 0 for maximum reliability
            }

            try:
                res = requests.post(self.url, json=payload, timeout=90)
                res.raise_for_status()
                data = json.loads(res.json().get("response", "{}"))
                
                action = str(data.get("action", "")).lower()
                
                # --- TERMINATION ---
                if action == "answer":
                    final_msg = data.get("text") or data.get("command") or "Task complete."
                    self.set_status("Idle")
                    return final_msg

                # --- ROUTING ---
                result = ""
                param_label = ""

                if action == "write":
                    filename = data.get("filename")
                    raw_code = data.get("code") or data.get("command")
                    clean_code = self.clean_code(raw_code)
                    result = write_project_file(filename, clean_code)
                    param_label = filename
                
                elif action == "run":
                    cmd = data.get("command") or data.get("filename")
                    result = run_project_code(cmd)
                    param_label = cmd
                
                elif action == "read":
                    fname = data.get("filename") or data.get("command")
                    result = read_project_file(fname)
                    param_label = fname

                elif action == "sync":
                    result = git_sync()
                    param_label = "GitHub"
                
                elif action in ["git", "docker", "search"]:
                    cmd = data.get("command") or data.get("query")
                    # Dynamically call based on name match
                    funcs = {"git": run_git_command, "docker": run_docker_command, "search": search_web}
                    result = funcs[action](cmd)
                    param_label = cmd
                else:
                    result = f"Error: '{action}' is not a valid tool name."
                    param_label = "None"

                # Update state for next loop
                self.task_history.append({"action": action, "param": param_label, "result": str(result)})
                current_observation = f"Result of {action}: {result}"
                logger.info(f"Step {step}: {action} -> {result}")

            except Exception as e:
                logger.error(f"Error at step {step}: {e}")
                current_observation = f"System Error: {str(e)}. Correct your JSON format or action."
            
            step += 1

        self.set_status("Idle")
        return f"Error: {self.max_steps} step limit reached."

my_agent = CoderAgent("Dev-01")
