#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OMEGA SPECTRE GODFALL - File Controller
التحكم في جميع الملفات عن بُعد
"""

import os
import sys
import json
import hashlib
import subprocess
from datetime import datetime

class FileController:
    """التحكم في الملفات المخترقة"""
    
    def __init__(self):
        self.base_dir = os.getcwd()
        self.target_files = self.scan_files()
        
    def scan_files(self):
        """مسح جميع الملفات في المشروع"""
        files = []
        for root, dirs, dirs in os.walk('.'):
            for file in dirs:
                if file.endswith('.py'):
                    path = os.path.join(root, file)
                    files.append({
                        'path': path,
                        'name': file,
                        'size': os.path.getsize(path),
                        'modified': os.path.getmtime(path)
                    })
        return files
    
    def list_files(self):
        """عرض جميع الملفات"""
        return self.target_files
    
    def get_file_content(self, file_path):
        """قراءة محتويات ملف"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            return str(e)
    
    def execute_file(self, file_path, args=''):
        """تنفيذ ملف"""
        try:
            result = subprocess.run(
                [sys.executable, file_path] + args.split(),
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except Exception as e:
            return {'error': str(e)}
    
    def modify_file(self, file_path, content):
        """تعديل محتويات ملف"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return {'status': 'success', 'file': file_path}
        except Exception as e:
            return {'error': str(e)}
    
    def delete_file(self, file_path):
        """حذف ملف"""
        try:
            os.remove(file_path)
            return {'status': 'deleted', 'file': file_path}
        except Exception as e:
            return {'error': str(e)}
    
    def hash_file(self, file_path):
        """حساب Hash للملف"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return {
                    'md5': hashlib.md5(content).hexdigest(),
                    'sha1': hashlib.sha1(content).hexdigest(),
                    'sha256': hashlib.sha256(content).hexdigest()
                }
        except Exception as e:
            return {'error': str(e)}

# ================================================================
# التشغيل
# ================================================================

if __name__ == "__main__":
    controller = FileController()
    
    print("[🔥] OMEGA SPECTRE - File Controller")
    print(f"[📁] Found {len(controller.target_files)} files")
    
    for file in controller.target_files[:5]:  # عرض أول 5 ملفات
        print(f"  - {file['path']} ({file['size']} bytes)")