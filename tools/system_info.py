import os

def get_system_info():
    return os.uname()

# Print the system info
print(get_system_info())