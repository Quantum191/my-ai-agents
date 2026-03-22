import requests
import os
import json
import re
import logging
from datetime import datetime
from memory.memory_manager import AgentMemory
from tools.file_manager import read_project_file, list_project_files, write_project_file, make_directory
from tools.git_manager import run_git_command
from tools.bash_manager import run_bash_command

# --- 1. LOGGING SETUP ---
LOG_PATH = "/home/sean/my-ai-agents/memory/agent.log"
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format='> %(asctime)s: %(message)s',
    datefmt='%H:%M:%S',
    force=True
)
logger = logging.getLogger("Dev01")

class CoderAgent:
    def __init__(self, name):
        self.name = name
        self.model = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
        self.url = "http://localhost:11434/api/chat"
        self.status_path = "/home/sean/my-ai-agents/memory/status.txt"
        self.rules_path = "/home/sean/my-ai-agents/memory/instructions.md"
        self.memory = AgentMemory()
        self.http_session = requests.Session()
        self.abort_signal = False 

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
        action_history = [] 
        last_action_signature = "" 
        self.abort_signal = False 
        
        # NEW: Read Persistent Rules from Markdown file
        persistent_rules = ""
        if os.path.exists(self.rules_path):
            try:
                with open(self.rules_path, "r") as f:
                    persistent_rules = f.read()
            except: pass

        self.set_status("Step 1/15: Thinking...")
        logger.info(f"--- NEW TASK RECEIVED: {prompt} ---")
        
        while step <= 15:
            if self.abort_signal:
                logger.info("🛑 MISSION ABORTED BY SYSTEM OVERRIDE.")
                self.set_status("Idle")
                return "MISSION ABORTED BY USER."

            files = str(list_project_files()[:15])
            history_text = "\n".join(action_history) if action_history else "No actions taken yet."

            # UPDATED: System prompt now includes persistent rules
            system_msg = (
                f"You are {self.name}, an expert DevOps AI.\n"
                "You MUST respond ONLY in valid JSON.\n\n"
                f"--- PERSISTENT USER RULES ---\n{persistent_rules}\n\n"
                f"Current Project Files: {files}\n\n"
                "--- TOOLS ---\n"
                "1. mkdir: {\"action\": \"mkdir\", \"filename\": \"folder\"}\n"
                "2. write: {\"action\": \"write\", \"filename\": \"file.ext\", \"code\": \"content\"}\n"
                "3. read:  {\"action\": \"read\", \"filename\": \"file.ext\"}\n"
                "4. bash:  {\"action\": \"bash\", \"command\": \"terminal_command\"}\n"
                "5. git:   {\"action\": \"git\", \"command\": \"status\"}\n"
                "6. answer:{\"action\": \"answer\", \"text\": \"Final summary.\"}\n\n"
                "--- CRITICAL ---\n"
                "- Review ACTION HISTORY to ensure you aren't looping.\n"
                "- If the task is complete, use the 'answer' tool."
            )

            try:
                res = self.http_session.post(self.url, json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": f"TASK: {prompt}\n\nACTION HISTORY:\n{history_text}\n\nLAST OBSERVATION: {last_obs}"}
                    ],
                    "stream": False
                }, timeout=60)
                
                content = res.json().get("message", {}).get("content", "")
                data = self.extract_json(content)
                
                if not data:
                    last_obs = "Error: Output valid JSON only."
                    step += 1
                    continue

                action = data.get("action", "").lower()
                target = data.get("filename") or data.get("command") or ""
                
                # LOOP GUARD
                current_action_signature = f"{action}:{target}"
                if current_action_signature == last_action_signature:
                    last_obs = f"SYSTEM WARNING: Repeat detected on '{target}'. Move to next step or finish."
                    step += 1
                    continue
                
                last_action_signature = current_action_signature

                self.set_status(f"Step {step}/15: {action}...")
                logger.info(f"Step {step}: AI selected tool [{action}]")

                if action == "answer":
                    final_text = data.get("text", "Done.")
                    self.memory.save_interaction(prompt, final_text)
                    self.set_status("Idle")
                    return final_text

                # Tool Routing
                if action == "mkdir": last_obs = make_directory(target)
                elif action == "write": last_obs = write_project_file(target, data.get("code", ""))
                elif action == "git": last_obs = run_git_command(target)
                elif action == "read": last_obs = read_project_file(target)
                elif action == "bash": last_obs = run_bash_command(target)
                else: last_obs = f"Unknown tool: {action}"
                
                logger.info(f"Step {step} Result: {str(last_obs)[:100]}")
                action_history.append(f"Step {step}: {action} {target} -> {str(last_obs)[:50]}")
                
            except Exception as e:
                last_obs = f"Error: {e}"
                logger.info(f"Step {step} Crashed: {str(e)}")
            
            step += 1
        
        self.set_status("Idle")
        return "Task limit reached."

my_agent = CoderAgent("Dev-01")