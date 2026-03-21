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
        self.max_steps = 20
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

        while step <= self.max_steps:
            self.set_status(f"Step {step}/{self.max_steps}...")
            
            raw_files = str(list_project_files())
            safe_files = raw_files[:500] + "...(truncated)" if len(raw_files) > 500 else raw_files
            recent_history = "\n".join(action_history[-5:]) if action_history else "No actions taken yet."

            # --- FIX: Restored 'command' key and all available tools to the prompt ---
            system_msg = (
                f"You are {self.name}. You must output JSON.\n"
                f"Available tools: write, run, read, git, sync, docker, search, answer.\n"
                f"Files in directory: {safe_files}\n"
                "Format: {\"action\": \"tool_name\", \"command\": \"args\", \"filename\": \"name\", \"code\": \"content\", \"text\": \"msg\"}\n\n"
                "CRITICAL RULES:\n"
                "1. DO NOT repeat an action if it was already successful in the history.\n"
                "2. If the user's task is fully complete based on the LAST OBSERVATION, you MUST use the 'answer' tool to finish."
            )

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": f"TASK: {prompt}\n\nHISTORY OF PAST ACTIONS:\n{recent_history}\n\nLAST OBSERVATION: {last_obs}\n\nReply with your next JSON action."}
                ],
                "stream": False
            }

            try:
                res = requests.post(self.url, json=payload, timeout=90)
                res.raise_for_status()
                
                raw_content = res.json().get("message", {}).get("content", "")
                
                if not raw_content.strip():
                    last_obs = "Error: You returned a blank message. Please output a valid JSON object."
                    action_history.append(f"Step {step}: Error - Blank output")
                    step += 1
                    continue

                data = self.extract_json(raw_content)
                if not data:
                    last_obs = "Error: No JSON found in your response."
                    action_history.append(f"Step {step}: Error - No JSON parsed")
                    logger.warning(f"Failed to parse JSON on step {step}. Raw text: {raw_content}")
                    step += 1
                    continue

                action = str(data.get("action", "")).lower()

                if action == "answer":
                    final_text = data.get("text") or "Task completed."
                    self.set_status("Idle")
                    logger.info(f"Task completed successfully in {step} steps.")
                    return final_text

                if action == "write":
                    code = data.get("code") or data.get("command")
                    clean_code = re.sub(r"```[a-zA-Z]*\n?|```", "", str(code)).strip()
                    last_obs = write_project_file(data.get("filename"), clean_code)
                elif action == "run":
                    last_obs = run_project_code(data.get("command") or data.get("filename"))
                elif action in ["read", "sync", "git", "docker", "search"]:
                    tool_map = {
                        "read": read_project_file, 
                        "sync": git_sync, 
                        "git": run_git_command, 
                        "docker": run_docker_command, 
                        "search": search_web
                    }
                    param = data.get("command") or data.get("filename") or data.get("query")
                    last_obs = tool_map[action](param) if param else tool_map[action]()
                else:
                    last_obs = f"Unknown action: {action}"

                safe_result = str(last_obs)[:100].replace('\n', ' ')
                action_history.append(f"Step {step}: used '{action}' -> Result: {safe_result}")
                logger.info(f"Step {step} - Action: {action} - Result: {safe_result}")

            except Exception as e:
                last_obs = f"System Error: {str(e)}"
                action_history.append(f"Step {step}: CRITICAL ERROR")
                logger.error(f"Critical loop error on step {step}: {e}")
            
            step += 1
        
        self.set_status("Idle")
        err_msg = f"Error: {self.max_steps} step limit reached."
        logger.warning(err_msg)
        return err_msg

# Module interface instantiation
my_agent = CoderAgent("Dev-01")
