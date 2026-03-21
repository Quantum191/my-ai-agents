import requests
import os
import json
import logging
from memory.memory_manager import AgentMemory
from tools.file_manager import read_project_file, list_project_files, write_project_file, run_project_code
from tools.web_search import search_web
from tools.git_manager import run_git_command, git_sync
from tools.docker_manager import run_docker_command

# --- Configuration & Logging ---
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
        
        # Configuration from environment
        self.model = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
        self.url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
        self.status_file = os.getenv("AGENT_STATUS_FILE", "/home/sean/my-ai-agents/memory/status.txt")
        self.max_steps = int(os.getenv("AGENT_MAX_STEPS", "20"))
        
        self.memory = AgentMemory()
        self.task_history = []
        self.set_status("Idle")

    def set_status(self, text):
        """Updates the dashboard status file."""
        try:
            with open(self.status_file, "w", encoding='utf-8') as f: 
                f.write(text)
        except Exception as e:
            logger.error("Failed to write to status file: %s", e)

    def ask_ai(self, prompt):
        """Main execution loop for the agent."""
        step = 1
        current_context = "Start"
        self.task_history = []
        
        # Tool mapping for easier routing
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
            
            # Format history for context
            history_text = "\n".join(
                [f"Step {i+1}: Action='{h['action']}', Result='{h['result'][:100]}...'" for i, h in enumerate(self.task_history)]
            ) if self.task_history else "None"
            
            files = list_project_files()
            
            # IMPROVED: Explicitly list 'answer' as a tool and clarify its use
            system = (
                f"You are {self.name}, a DevOps automation specialist on Arch Linux.\n"
                f"GOAL: {prompt}\n"
                f"FILES: {files}\n\n"
                "CRITICAL INSTRUCTIONS:\n"
                "1. You MUST execute all steps requested by the user. Do not skip to the end.\n"
                "2. If the user asks to write and run a file, you must use 'write', then 'run', THEN 'answer'.\n"
                "3. Use 'answer' ONLY when the task is fully complete and you have the final output to report.\n\n"
                "AVAILABLE TOOLS:\n"
                "- 'sync', 'git', 'docker', 'read', 'write', 'run', 'search'.\n"
                "- 'answer': Use this ONLY to deliver the final result of the work performed.\n\n"
                "FORMAT: You must return ONLY valid JSON."
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
                res.raise_for_status()
                
                res_data = res.json()
                data = json.loads(res_data.get("response", "{}"))
                
                # Normalize action to lowercase to prevent case-sensitive mismatches
                action = str(data.get("action", "")).lower()
                
                # --- EXIT CONDITION: The 'answer' action ---
                if action == "answer":
                    final_text = data.get("text") or data.get("command") or "Task completed."
                    self.memory.save_interaction(prompt, final_text)
                    self.set_status("Idle")
                    return final_text
                
                # --- ACTION ROUTING ---
                out = ""
                param_log = ""
                
                if action == "sync":
                    self.set_status("Syncing...")
                    out = git_sync()
                    param_log = "GitHub Sync"
                    
                elif action in cmd_map:
                    self.set_status(f"Running {action}...")
                    
                    # Logic for different parameter keys
                    if action == "write":
                        filename = data.get("filename")
                        code = data.get("code") or data.get("command")
                        out = write_project_file(filename, code)
                        param_log = f"file: {filename}"
                    else:
                        # Fallback for search, run, read, git, docker
                        param = data.get("command") or data.get("filename") or data.get("query")
                        out = cmd_map[action](param)
                        param_log = str(param)
                else:
                    out = f"Error: Unknown action '{action}'. Please use valid tools or 'answer'."
                    param_log = "N/A"
                    logger.warning("AI requested unknown action: %s", action)

                # Update history and context for the next iteration
                self.task_history.append({"action": action, "parameter": param_log, "result": str(out)})
                current_context = f"Result of {action}: {out}"
                
            except requests.exceptions.RequestException as e:
                logger.error("Ollama API Error: %s", e)
                current_context = f"Error: LLM backend unreachable. {str(e)}"
            except json.JSONDecodeError as e:
                logger.error("JSON Error: %s", e)
                current_context = "Error: Invalid JSON. Please retry using the correct format."
            except Exception as e:
                logger.exception("Unexpected error in execution loop.")
                current_context = f"System Error: {str(e)}"
                
            step += 1
            
        self.set_status("Idle")
        return f"Error: {self.max_steps} step limit reached without an 'answer'."

# Instantiate agent
my_agent = CoderAgent("Dev-01")