#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OMEGA SPECTRE GODFALL - Payload Uploader
رفع الحمولة إلى خوادم عامة
"""

import os
import sys
import json
import time
import requests
import subprocess
from datetime import datetime

class PayloadUploader:
    """رفع ملف OMEGA_SPECTRE_GODFALL.zip"""
    
    def __init__(self):
        self.payload = "OMEGA_SPECTRE_GODFALL.zip"
        self.services = {
            'fileio': {
                'url': 'https://file.io',
                'method': 'post',
                'file_field': 'file'
            },
            'anonfiles': {
                'url': 'https://api.anonfiles.com/upload',
                'method': 'post',
                'file_field': 'file'
            },
            'pixeldrain': {
                'url': 'https://pixeldrain.com/api/file/',
                'method': 'put',
                'file_field': 'file'
            },
            'gofile': {
                'url': 'https://api.gofile.io/uploadFile',
                'method': 'post',
                'file_field': 'file'
            }
        }
        self.uploaded_links = []
        
    def upload_to_service(self, service_name, service_config):
        """رفع الملف إلى خدمة معينة"""
        try:
            url = service_config['url']
            method = service_config['method']
            file_field = service_config['file_field']
            
            with open(self.payload, 'rb') as f:
                files = {file_field: f}
                
                if method == 'post':
                    response = requests.post(url, files=files, timeout=30)
                else:
                    response = requests.put(url, files=files, timeout=30)
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    link = data.get('link') or data.get('url') or data.get('data', {}).get('url')
                    if link:
                        self.uploaded_links.append({
                            'service': service_name,
                            'link': link,
                            'response': data
                        })
                        return link
        except Exception as e:
            print(f"[⚠️] {service_name} failed: {e}")
        return None
    
    def upload_all(self):
        """رفع إلى جميع الخدمات"""
        print("[🔥] Uploading payload to all services...")
        
        for name, config in self.services.items():
            print(f"[📤] Uploading to {name}...")
            link = self.upload_to_service(name, config)
            if link:
                print(f"[✅] Uploaded: {link}")
            else:
                print(f"[❌] Failed: {name}")
            time.sleep(1)  # تجنب الحظر
        
        # حفظ النتائج
        self.save_results()
        
        return self.uploaded_links
    
    def save_results(self):
        """حفظ نتائج الرفع"""
        with open('upload_results.txt', 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("PAYLOAD UPLOAD RESULTS\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"File: {self.payload}\n")
            f.write(f"Time: {datetime.now().isoformat()}\n\n")
            
            for item in self.uploaded_links:
                f.write(f"[{item['service']}]\n")
                f.write(f"  Link: {item['link']}\n\n")
    
    def generate_sharing_links(self):
        """توليد روابط مشاركة"""
        links = []
        for item in self.uploaded_links:
            links.append(item['link'])
        return links

# ================================================================
# التشغيل
# ================================================================

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║   🔥 OMEGA SPECTRE - Payload Uploader 🔥                ║
    ║                                                          ║
    ║   📤  Uploading OMEGA_SPECTRE_GODFALL.zip              ║
    ║   🌐  To multiple file hosting services                 ║
    ║                                                          ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    uploader = PayloadUploader()
    results = uploader.upload_all()
    
    print("\n[✅] Upload complete!")
    print(f"[📁] {len(results)} uploads successful")
    
    print("\n[🔗] Sharing links:")
    for item in results:
        print(f"  {item['service']}: {item['link']}")