import subprocess
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool
from crewai_tools import FileWriterTool, FileReadTool, DirectoryReadTool

# --- 1. TOOLS & CONFIG ---
@tool("TestProject")
def test_tool(main_file: str):
    """Runs the python script to check for errors."""
    try:
        result = subprocess.run(['python', main_file], capture_output=True, text=True, timeout=10)
        return "SUCCESS" if result.returncode == 0 else f"ERROR: {result.stderr}"
    except Exception as e:
        return str(e)

llm_config = {"max_tokens": 4096, "temperature": 0.2}
base_llm = LLM(model="ollama/qwen2.5-coder:7b", base_url="http://localhost:11434", **llm_config)

# --- 2. DYNAMIC AGENTS ---
# Notice the {variables} in the goal and backstory
architect = Agent(
    role='System Architect',
    goal='Design the architecture for {project_idea} while strictly avoiding {avoid_list}.',
    backstory='You are an expert at modular design. You ensure the plan follows the user\'s constraints.',
    llm=base_llm,
    verbose=True
)

developer = Agent(
    role='Senior Developer',
    goal='Implement the {project_idea} following the architect\'s plan, ensuring you avoid {avoid_list}.',
    backstory='You write clean, tested code. You are careful to follow negative constraints (the "avoid" list).',
    llm=base_llm,
    tools=[FileWriterTool(), FileReadTool(), DirectoryReadTool(), test_tool],
    max_iter=10,
    verbose=True
)

# --- 3. DYNAMIC TASKS ---
planning_task = Task(
    description=(
        "1. Analyze the project idea: {project_idea}. "
        "2. Create a file structure blueprint. "
        "3. Explicitly list how you will avoid {avoid_list} in the design."
    ),
    agent=architect,
    expected_output="A modular project blueprint and avoidance strategy."
)

coding_task = Task(
    description=(
        "1. Write the code for {project_idea} based on the architect's blueprint. "
        "2. Ensure you do NOT use or do any of the following: {avoid_list}. "
        "3. Test the main entry point to ensure it works."
    ),
    agent=developer,
    context=[planning_task],
    expected_output="A working project folder that meets all user requirements."
)

# --- 4. THE INTERACTIVE LAUNCHER ---
def run_factory():
    print("\n--- 🚀 WELCOME TO YOUR AI SOFTWARE FACTORY ---")
    
    # This is where YOU talk to the agents
    user_idea = input("What do you want to build today? (e.g., 'A Recipe App')\n> ")
    user_avoid = input("What should I avoid? (e.g., 'complex libraries', 'OpenAI', 'long comments')\n> ")
    
    # We pack your answers into a dictionary
    user_inputs = {
        'project_idea': user_idea,
        'avoid_list': user_avoid
    }

    # The agents receive your inputs here
    crew = Crew(agents=[architect, developer], tasks=[planning_task, coding_task])
    crew.kickoff(inputs=user_inputs)

if __name__ == "__main__":
    run_factory()
