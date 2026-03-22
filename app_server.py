import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Adjusted import to match your agents/base_agent.py path
try:
    from agents.base_agent import my_agent
except ImportError as e:
    print(f"❌ IMPORT ERROR: Could not find base_agent.py in the agents/ folder.")
    print(f"Details: {e}")
    exit(1)

app = Flask(__name__, static_folder='Website')
CORS(app)

# --- 1. Serve the Website files ---
@app.route('/')
def index():
    """Serves the main dashboard page."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    """Serves CSS, JS, and JSON files from the Website folder."""
    # This ensures files like stats.json are served correctly
    return send_from_directory(app.static_folder, path)

# --- 2. The AI Command Endpoint ---
@app.route('/ask', methods=['POST'])
def ask_bot():
    """Receives prompts from the web UI and sends them to DEV-01."""
    try:
        data = request.json
        user_prompt = data.get("prompt")
        
        if not user_prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        print(f"WEB_CMD: Received task -> {user_prompt}")
        
        # Calls the agent logic from agents/base_agent.py
        response = my_agent.ask_ai(user_prompt)
        
        return jsonify({"response": response})
    except Exception as e:
        print(f"SERVER_ERROR: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    print("\n" + "="*40)
    print("🚀 DEV-01 Web Interface is starting...")
    print("📍 URL: http://localhost:8080")
    print("="*40 + "\n")
    
    app.run(host='0.0.0.0', port=8080, debug=True)