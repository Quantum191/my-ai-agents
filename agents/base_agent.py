import requests
import os
import json
import logging
import re
from datetime import datetime
from memory.memory_manager import AgentMemory
from tools.file_manager import read_project_file, list_project_files, write_project_file, run_project_code
from tools.web_search import search_web
from tools.git_manager import run_git_command, git_sync
from tools.docker_manager import run_docker_command
from tools.web_scraper import scrape_url

# --- Logging Setup ---
AGENT_LOG_FILE = os.getenv("AGENT_LOG_FILE", "/home/sean/my-ai-agents/memory/agent.log")
logging.basicConfig(filename=AGENT_LOG_FILE, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("CoderAgent")

class CoderAgent:
    def __init__(self, name):
        self.name = name
        self.model = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
        self.url = os.getenv("OLLAMA_CHAT_URL", "http://localhost:11434/api/chat")
        self.status_file = os.getenv("AGENT_STATUS_FILE", "/home/sean/my-ai-agents/memory/status.txt")
        self.max_steps = 30  # Increased for complex autonomous tasks
        self.memory = AgentMemory()

    def set_status(self, text):
        try:
            with open(self.status_file, "w", encoding='utf-8') as f: 
                f.write(text)
        except Exception as e:
            logger.error(f"Failed to write to status file: {e}")

    def extract_json(self, text):
        if not text:
            return None
        try:
            match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            return json.loads(text)
        except:
            return None

    def ask_ai(self, prompt):
        step = 1
        last_obs = "None."
        action_history = [] 
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        past_memories = self.memory.recall_recent_interactions(limit=3)
        if not past_memories:
            past_memories = "No prior tasks recorded in long-term memory."

        while step <= self.max_steps:
            self.set_status(f"Step {step}/{self.max_steps}...")
            
            raw_files = str(list_project_files())
            safe_files = raw_files[:500] + "...(truncated)" if len(raw_files) > 500 else raw_files
            recent_history = "\n".join(action_history[-5:]) if action_history else "No actions taken yet."

            # --- UPDATED SYSTEM MESSAGE WITH ANTI-LAZY RULES ---
            system_msg = (
                f"You are {self.name}. You must output JSON.\n"
                f"Available tools: write, run, read, git, sync, docker, search, scrape, reset, answer.\n"
                f"Files in directory: {safe_files}\n"
                "Format: {\"action\": \"tool_name\", \"command\": \"args\", \"filename\": \"name\", \"code\": \"content\", \"text\": \"msg\"}\n\n"
                "--- EXECUTION RULES ---\n"
                "1. When using 'write', you MUST provide the FULL, COMPLETE content of the file. NEVER output snippets.\n"
                "2. If updating a file, use 'read' first to ensure you keep existing boilerplate.\n"
                "3. NEVER use the 'answer' tool until you have seen a 'SUCCESS' observation from a 'write' or 'run' action.\n"
                "4. If you repeat an action twice and fail, use the 'reset' tool to clear your loop history and try a new approach.\n"
                "5. Do not apologize. Just execute JSON.\n\n"
                "--- PAST RECOLLECTIONS ---\n"
                f"{past_memories}\n\n"
                "Reply with your next JSON action."
            )

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": f"TASK: {prompt}\n\nCURRENT LOOP HISTORY:\n{recent_history}\n\nLAST OBSERVATION: {last_obs}\n\nNext action:"}
                ],
                "stream": False
            }

            try:
                res = requests.post(self.url, json=payload, timeout=90)
                res.raise_for_status()
                raw_content = res.json().get("message", {}).get("content", "")
                
                data = self.extract_json(raw_content)
                if not data:
                    last_obs = "Error: No JSON found. Please output a valid JSON object."
                    action_history.append(f"Step {step}: Error - JSON parse failed")
                    step += 1
                    continue

                action = str(data.get("action", "")).lower()

                if action == "answer":
                    final_text = data.get("text") or "Task completed."
                    self.memory.save_interaction(prompt, final_text)
                    self.set_status("Idle")
                    logger.info(f"Task complete in {step} steps.")
                    return final_text

                # --- TOOL ROUTING ---
                param_used = "None"
                
                if action == "reset":
                    action_history = []
                    last_obs = "Short-term history cleared. Starting fresh loop."
                    param_used = "Memory Reset"
                
                elif action == "write":
                    code = data.get("code") or data.get("command")
                    clean_code = re.sub(r"```[a-zA-Z]*\n?|```", "", str(code)).strip()
                    last_obs = write_project_file(data.get("filename"), clean_code)
                    param_used = data.get("filename")
                
                elif action == "run":
                    param_used = data.get("command") or data.get("filename")
                    last_obs = run_project_code(param_used)
                
                elif action in ["read", "sync", "git", "docker", "search", "scrape"]:
                    tool_map = {
                        "read": read_project_file, 
                        "sync": git_sync, 
                        "git": run_git_command, 
                        "docker": run_docker_command, 
                        "search": search_web,
                        "scrape": scrape_url
                    }
                    param = data.get("command") or data.get("filename") or data.get("query")
                    param_used = str(param)
                    last_obs = tool_map[action](param) if param else tool_map[action]()
                else:
                    last_obs = f"Unknown action: {action}"

                # Update Context
                safe_result = str(last_obs)[:100].replace('\n', ' ')
                action_history.append(f"Step {step}: used '{action}' -> Result: {safe_result}")
                logger.info(f"Step {step} - Action: {action} - Result: {safe_result}")
                self.memory.save_tool_action(session_id, action, param_used, str(last_obs))

            except Exception as e:
                last_obs = f"System Error: {str(e)}"
                logger.error(f"Loop error on step {step}: {e}")
            
            step += 1
        
        self.set_status("Idle")
        return f"Error: {self.max_steps} step limit reached."

my_agent = CoderAgent("Dev-01")