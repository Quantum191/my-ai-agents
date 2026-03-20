from tools.file_manager import list_project_files, read_project_file

print("--- FILE LIST ---")
files = list_project_files().split('\n')
print(files)

print("\n--- CONTENT TEST (main.py) ---")
print(read_project_file("main.py")[:100]) # Print first 100 chars
