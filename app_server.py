import os
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# --- MUTE FLASK SPAM ---
# This prevents the "GET /stats.json 200" lines from flooding your terminal and logs
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

try:
    from agents.base_agent import my_agent
except ImportError as e:
    print(f"❌ CRITICAL ERROR: Could not find agents/base_agent.py\n{e}")
    exit(1)

app = Flask(__name__, static_folder='Website')
CORS(app)

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(app.static_folder, path)

@app.route('/ask', methods=['POST'])
def ask_bot():
    try:
        data = request.json
        prompt = data.get("prompt")
        
        if not prompt:
            return jsonify({"error": "No prompt"}), 400
        
        print(f"\n[WEB] --> Task: {prompt}")
        response = my_agent.ask_ai(prompt)
        print(f"[WEB] <-- Agent Finished.")
        
        return jsonify({"response": response})
        
    except Exception as e:
        print(f"❌ SERVER ERROR: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*40)
    print("🚀 DEV-01 Web Interface is starting...")
    print("📍 URL: http://localhost:8080")
    print("="*40 + "\n")
    
    app.run(host='0.0.0.0', port=8080, debug=False) # Turned debug to False to help reduce noise