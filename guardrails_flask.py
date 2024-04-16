import importlib.util
from flask import Flask, jsonify, send_from_directory
from flask import request

spec = importlib.util.spec_from_file_location("guardrails", "./guardrails.py")
guardrails = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guardrails)

app = Flask(__name__)
@app.route('/<path:path>')

def static_file(path):
    return send_from_directory('UI', path)

@app.route('/')
def index():
    return send_from_directory('UI', 'index.html')

@app.route('/chat', methods=['POST'])
def analyze():
    data = request.get_json()
    user_message = data['user_message']
    return jsonify(guardrails.start(user_message))

if __name__ == '__main__':
    app.run(debug=True)
