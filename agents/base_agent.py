import requests
import os
import json
import re
import logging
from datetime import datetime
from memory.memory_manager import AgentMemory
from tools.file_manager import read_project_file, list_project_files, write_project_file, run_project_code, make_directory
from tools.git_manager import run_git_command

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
        action_history = [] # THE SCRATCHPAD: Tracks what the AI has done so far
        
        self.set_status("Step 1/15: Thinking...")
        logger.info(f"--- NEW TASK RECEIVED: {prompt} ---")
        
        while step <= 15:
            logger.info(f"Step {step}: Analyzing environment...")
            files = str(list_project_files())[:400]
            
            # Format the scratchpad for the AI to read
            history_text = "\n".join(action_history) if action_history else "No actions taken yet."

            system_msg = (
                f"You are {self.name}, an expert DevOps AI.\n"
                "You MUST respond ONLY in valid JSON.\n\n"
                f"Current Project Files: {files}\n\n"
                "--- AVAILABLE TOOLS & JSON FORMATS ---\n"
                "1. mkdir: {\"action\": \"mkdir\", \"filename\": \"folder_name\"}\n"
                "2. write: {\"action\": \"write\", \"filename\": \"path/to/file.ext\", \"code\": \"file content\"}\n"
                "3. read:  {\"action\": \"read\", \"filename\": \"path/to/file.ext\"}\n"
                "4. run:   {\"action\": \"run\", \"command\": \"command to run\"}\n"
                "5. git:   {\"action\": \"git\", \"command\": \"status\"}\n"
                "6. answer:{\"action\": \"answer\", \"text\": \"Task completed successfully.\"}\n\n"
                "--- CRITICAL RULES ---\n"
                "- Review the 'ACTION HISTORY' to see what you have already done.\n"
                "- To put a file inside a folder, use the format 'folder_name/file_name.ext'.\n"
                "- WHEN YOU HAVE FINISHED THE REQUESTED TASK, YOU MUST USE THE 'answer' TOOL TO STOP.\n"
                "- Output ONLY ONE action per step."
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
                
                data = self.extract_json(res.json().get("message", {}).get("content", ""))
                if not data:
                    logger.info(f"Step {step}: Error - AI failed to return valid JSON.")
                    last_obs = "Error: Invalid JSON format. Output valid JSON only."
                    step += 1
                    continue

                action = data.get("action", "").lower()
                self.set_status(f"Step {step}/15: {action}...")
                logger.info(f"Step {step}: AI selected tool [{action}]")

                if action == "answer":
                    final_text = data.get("text", "Done.")
                    self.memory.save_interaction(prompt, final_text)
                    self.set_status("Idle")
                    logger.info(f"TASK COMPLETE: {final_text}")
                    return final_text

                # Tool Routing
                if action == "mkdir": 
                    last_obs = make_directory(data.get("filename") or data.get("command"))
                elif action == "write": 
                    last_obs = write_project_file(data.get("filename"), data.get("code", ""))
                elif action == "git": 
                    last_obs = run_git_command(data.get("command"))
                elif action == "run": 
                    last_obs = run_project_code(data.get("filename") or data.get("command"))
                elif action == "read": 
                    last_obs = read_project_file(data.get("filename"))
                else: 
                    last_obs = f"Unknown tool: {action}"
                
                logger.info(f"Step {step} Result: {str(last_obs)[:100]}")
                
                # Record the action and result into the scratchpad so the AI remembers it next loop
                action_history.append(f"Used '{action}' -> Result: {str(last_obs)[:100]}")
                
            except Exception as e:
                last_obs = f"Error: {e}"
                logger.info(f"Step {step} Crashed: {str(e)}")
            
            step += 1
        
        self.set_status("Idle")
        logger.info("TASK FAILED: Step limit reached.")
        return "Task limit reached. The agent got stuck and timed out."

my_agent = CoderAgent("Dev-01")