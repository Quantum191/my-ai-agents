import requests
import os
import json
import logging
from memory.memory_manager import AgentMemory
from tools.file_manager import read_project_file, list_project_files, write_project_file, run_project_code
from tools.web_search import search_web
from tools.git_manager import run_git_command, git_sync
from tools.docker_manager import run_docker_command

# Setup basic logging
LOG_LEVEL = os.getenv("AGENT_LOG_LEVEL", "INFO").upper()
# Set up a central agent log file
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
        
        # Section 1B: Extract Hardcoded Configuration
        self.model = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
        self.url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
        self.status_file = os.getenv("AGENT_STATUS_FILE", "/home/sean/my-ai-agents/memory/status.txt")
        self.max_steps = int(os.getenv("AGENT_MAX_STEPS", "20"))
        
        self.memory = AgentMemory()
        self.task_history = []
        self.set_status("Idle")

    def set_status(self, text):
        try:
            with open(self.status_file, "w", encoding='utf-8') as f: 
                f.write(text)
        except Exception as e:
            logger.error("Failed to write to status file: %s", e)

    def ask_ai(self, prompt):
        # Section 1A: Remove Deep Recursion
        # Replaced the recursive `return self.ask_ai(...)` calls with a proper while loop.
        step = 1
        current_context = "Start"
        self.task_history = []
        
        cmd_map = {
            "docker": run_docker_command, 
            "git": run_git_command, 
            "read": read_project_file, 
            "write": lambda f, c: write_project_file(f, c), 
            "run": run_project_code, 
            "search": search_web
        }
        
        while step <= self.max_steps:
            self.set_status(f"Step {step}/{self.max_steps}")
            logger.info("Executing step %d/%d for objective.", step, self.max_steps)
            
            # Format history robustly to prevent prompt context bloat
            history_text = "\n".join(
                [f"Step {i+1}: Action='{h['action']}', Target='{h['parameter']}'" for i, h in enumerate(self.task_history)]
            ) if self.task_history else "None"
            
            files = list_project_files()
            
            system = (
                "You are Dev-01, a JSON-only DevOps agent on Arch Linux.\n"
                f"GOAL: {prompt}\nPAST: {history_text}\nFILES: {files}\n"
                "TOOLS:\n"
                "- 'sync': Checks for and pulls updates from GitHub (Antigravity cloud).\n"
                "- 'git': Runs standard git commands (commit, push, etc.).\n"
                "- 'docker', 'read', 'write', 'run', 'search'.\n"
                "RULES: Always sync before starting work if the user mentions cloud updates.\n"
                "FORMAT: You MUST return ONLY valid JSON using this exact schema: {\"action\": \"<tool_name_or_answer>\", \"command\": \"<tool_args>\", \"filename\": \"<optional_file>\", \"text\": \"<message_to_user>\"}"
            )
            
            payload = {
                "model": self.model,
                "prompt": f"{system}\n\nContext: {current_context}\n\nResponse:",
                "format": "json", 
                "stream": False, 
                "options": {"temperature": 0.1}
            }

            try:
                res = requests.post(self.url, json=payload, timeout=90)
                res.raise_for_status() # Raise warning on bad HTTP codes
                
                res_data = res.json()
                data = json.loads(res_data.get("response", "{}"))
                action = data.get("action")
                
                if action == "answer":
                    text = data.get("text", "Done.")
                    self.memory.save_interaction(prompt, text)
                    self.set_status("Idle")
                    return text
                
                # Action Routing
                out = ""
                param_log = ""
                
                if action == "sync":
                    self.set_status("Syncing with Cloud...")
                    out = git_sync()
                    param_log = "GitHub Push/Pull"
                    
                elif action in cmd_map:
                    param = data.get("command") or data.get("filename") or data.get("query")
                    self.set_status(f"Running {action}...")
                    
                    if action == "write":
                        out = cmd_map[action](data.get("filename"), data.get("code"))
                        param_log = data.get("filename", "unknown_file")
                    else:
                        out = cmd_map[action](param)
                        param_log = str(param)
                else:
                    out = f"Error: Unknown action '{action}' requested by AI."
                    param_log = "Unknown"
                    logger.warning(out + f" Full LLM JSON data: {data}")

                # Record history cleanly
                self.task_history.append({"action": action, "parameter": param_log, "result": str(out)})
                
                # Keep current context strictly to the immediate last output so the LLM context size doesn't explode
                current_context = f"Result of {action}: {out}"
                
            except requests.exceptions.RequestException as e:
                # Improved Section 1C: Specific Catching and logging
                logger.error("Network or API Error with Ollama: %s", e)
                current_context = f"Error communicating with local LLM Backend: {str(e)}"
            except json.JSONDecodeError as e:
                logger.error("JSON Parsing Error from LLM Output: %s", e)
                current_context = "Error: Invalid JSON format returned. You must return strictly valid JSON."
            except Exception as e:
                # Catch-all backup
                logger.exception("Catastrophic error during the agent execution loop.")
                current_context = f"System Architecture Error: {str(e)}"
                
            step += 1
            
        self.set_status("Idle")
        err_msg = f"Error: {self.max_steps} step limit reached before reaching an 'answer' state."
        logger.error(err_msg)
        return err_msg

# Module interface instantiation
my_agent = CoderAgent("Dev-01")
