from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import os

app = Flask(__name__, static_folder='Website', template_folder='Website')

# Ensure stats.json exists
STATS_FILE = "stats.json"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stats.json')
def get_stats():
    """Serves the latest hardware stats from disk."""
    try:
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r') as f:
                data = json.load(f)
            return jsonify(data)
        return jsonify({"error": "Stats file not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    user_prompt = data.get('prompt', '')
    
    # Here you would trigger your DEV-01 agent logic
    # For now, we return a mock response
    print(f"Agent received prompt: {user_prompt}")
    return jsonify({"response": f"DEV-01: Processing request for '{user_prompt}'..."})

@app.route('/<path:path>')
def send_static(path):
    return send_from_directory('Website', path)

if __name__ == '__main__':
    # Run on port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)