import requests
import os
import json
from memory.memory_manager import AgentMemory
from tools.file_manager import read_project_file, list_project_files, write_project_file, run_project_code
from tools.web_search import search_web
from tools.git_manager import run_git_command
from tools.docker_manager import run_docker_command

class CoderAgent:
    def __init__(self, name, model="qwen2.5-coder:7b"):
        self.name = name
        self.model = model
        self.url = "http://localhost:11434/api/generate"
        self.memory = AgentMemory()
        self.status_file = "/home/sean/my-ai-agents/memory/status.txt"
        os.makedirs("/home/sean/my-ai-agents/memory", exist_ok=True)
        self.task_history = []
        self.set_status("Idle")

    def set_status(self, text):
        try:
            with open(self.status_file, "w") as f:
                f.write(text)
        except: pass

    def ask_ai(self, prompt, context_override=None, step=1):
        if step > 10:
            self.set_status("Idle")
            return "Error: Reached 10 step limit."

        self.set_status(f"Step {step}/10")
        
        history_str = "\n".join(self.task_history) if self.task_history else "No actions taken yet."
        available_files = list_project_files()
        
        system = (
            "You are an elite AI DevOps and Systems Engineer. Use JSON format only.\n"
            f"GOAL: {prompt}\n"
            f"PAST ACTIONS:\n{history_str}\n"
            f"FILES IN PROJECT:\n{available_files}\n\n"
            "STRICT RULES:\n"
            "1. You MUST use tools to complete the goal BEFORE answering.\n"
            "2. If spinning up Docker containers, run them in detached mode (-d).\n"
            "3. You can execute code INSIDE a running container using 'docker exec'.\n"
            "4. CRITICAL: NEVER use '-it' with docker exec, as it will freeze the system waiting for terminal input. Use standard 'docker exec <container> <cmd>'.\n\n"
            "ACTIONS:\n"
            "- {\"action\": \"docker\", \"command\": \"docker run -d ...\"}\n"
            "- {\"action\": \"docker\", \"command\": \"docker exec ai-web-server sh -c 'echo \\\"Hello\\\" > /usr/share/nginx/html/index.html'\"}\n"
            "- {\"action\": \"git\", \"command\": \"git ...\"}\n"
            "- {\"action\": \"read\", \"filename\": \"...\"}\n"
            "- {\"action\": \"write\", \"filename\": \"...\", \"code\": \"...\"}\n"
            "- {\"action\": \"run\", \"filename\": \"...\"}\n"
            "- {\"action\": \"search\", \"query\": \"...\"}\n"
            "- {\"action\": \"answer\", \"text\": \"Final summary...\"}"
        )
        
        ctx = context_override if context_override else "Start the task."
        payload = {
            "model": self.model,
            "prompt": f"{system}\n\nContext: {ctx}\n\nResponse:",
            "format": "json", "stream": False, "options": {"temperature": 0.1}
        }

        try:
            r = requests.post(self.url, json=payload).json()
            data = json.loads(r.get("response", "{}"))
            action = data.get("action")
            
            if action == "answer":
                self.set_status("Idle")
                final_answer = data.get("text", "Task completed.")
                
                # ---> THE MISSING LINK <---
                self.memory.save_interaction(prompt, final_answer) 
                
                self.task_history = []
                return final_answer
                
            elif action == "docker":
                cmd = data.get("command")
                self.set_status(f"Running {cmd}...")
                output = run_docker_command(cmd)
                self.task_history.append(f"Ran {cmd}")
                return self.ask_ai(prompt, context_override=f"DOCKER OUTPUT FOR {cmd}:\n{output}", step=step+1)

            elif action == "read":
                fn = data.get("filename")
                self.set_status(f"Reading {fn}...")
                content = read_project_file(fn)
                self.task_history.append(f"Read {fn}")
                return self.ask_ai(prompt, context_override=f"CONTENT OF {fn}:\n{content}", step=step+1)
            
            elif action == "git":
                cmd = data.get("command")
                self.set_status(f"Running {cmd}...")
                output = run_git_command(cmd)
                self.task_history.append(f"Ran {cmd}")
                return self.ask_ai(prompt, context_override=f"GIT OUTPUT FOR {cmd}:\n{output}", step=step+1)

            elif action == "search":
                q = data.get("query")
                self.set_status(f"Searching...")
                clean_results = "\n".join([l for l in search_web(q).split('\n') if "Warning" not in l])
                self.task_history.append(f"Searched for {q}")
                return self.ask_ai(prompt, context_override=f"SEARCH RESULTS:\n{clean_results}", step=step+1)

            elif action == "write":
                fn = data.get("filename")
                write_project_file(fn, data.get("code", ""))
                self.task_history.append(f"Wrote {fn}")
                return self.ask_ai(prompt, context_override=f"Done writing {fn}", step=step+1)

            elif action == "run":
                fn = data.get("filename")
                out = run_project_code(fn)
                self.task_history.append(f"Ran {fn}")
                return self.ask_ai(prompt, context_override=f"Run Output: {out}", step=step+1)

            return f"Unknown action: {action}"
            
        except Exception as e:
            self.set_status("Idle")
            return f"Error: {str(e)}"

my_agent = CoderAgent("Dev-01")
