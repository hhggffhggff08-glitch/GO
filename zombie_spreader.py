# -*- coding: utf-8 -*-
# mesh_network/zombie_spreader.py
# PROJECT: OMEGA_SPECTRE_GODFALL
# STATUS: ZOMBIE_SPREADER — NODE PROPAGATION

import os
import sys
import time
import json
import socket
import threading
import random
import hashlib
import base64
import subprocess
import requests
import queue
from datetime import datetime
from collections import defaultdict
import numpy as np

class ZombieSpreader:
    """
    Zombie Spreader Engine
    Spreads infected nodes across the network
    """
    
    def __init__(self):
        self.zombie_nodes = []
        self.infected_nodes = []
        self.pending_infections = queue.Queue()
        self.active_zombies = {}
        self.infection_history = []
        self.spread_rate = 0.1
        self.max_zombies = 10000
        self.infection_counter = 0
        self.is_spreading = False
        self.target_networks = []
        self.spread_stats = {
            'total_infections': 0,
            'successful_infections': 0,
            'failed_infections': 0,
            'active_zombies': 0
        }
        
        # Initialize zombie spreader
        self._initialize_targets()
        print("🧟 Zombie Spreader Initialized")

    def _initialize_targets(self):
        """Initialize target networks"""
        print("🧟 Initializing target networks...")
        
        # Common target networks
        self.target_networks = [
            '192.168.0.0/24',
            '192.168.1.0/24',
            '10.0.0.0/24',
            '172.16.0.0/24',
            '192.168.100.0/24'
        ]
        
        print(f"✅ Initialized {len(self.target_networks)} target networks")

    def spread_infection(self, target_network=None):
        """Spread infection to a target network"""
        if target_network is None:
            target_network = random.choice(self.target_networks)
        
        print(f"🧟 Spreading infection to {target_network}...")
        
        # Scan network for targets
        targets = self._scan_network(target_network)
        
        # Infect targets
        for target in targets:
            success = self._infect_target(target)
            if success:
                self.infection_counter += 1
                self.spread_stats['successful_infections'] += 1
                self.zombie_nodes.append({
                    'id': target['id'],
                    'ip': target['ip'],
                    'infected_at': time.time(),
                    'status': 'active'
                })
            else:
                self.spread_stats['failed_infections'] += 1
        
        self.spread_stats['total_infections'] += len(targets)
        self.spread_stats['active_zombies'] = len(self.zombie_nodes)
        
        print(f"✅ Infection spread: {len(targets)} targets, {self.spread_stats['successful_infections']} infected")
        return len(targets)

    def _scan_network(self, network):
        """Scan a network for targets"""
        print(f"🧟 Scanning network: {network}")
        
        # Parse network range
        network_parts = network.split('/')
        base_ip = network_parts[0]
        subnet = int(network_parts[1])
        
        # Generate IP range
        targets = []
        base_parts = base_ip.split('.')
        base_int = int(base_parts[0]) * 256**3 + int(base_parts[1]) * 256**2 + int(base_parts[2]) * 256 + int(base_parts[3])
        
        # Calculate range
        hosts = 2 ** (32 - subnet)
        for i in range(1, min(hosts, 256)):  # Limit to 256 hosts
            ip_int = base_int + i
            ip = f"{(ip_int >> 24) & 0xFF}.{(ip_int >> 16) & 0xFF}.{(ip_int >> 8) & 0xFF}.{ip_int & 0xFF}"
            
            # Check if host is alive
            if self._check_host(ip):
                targets.append({
                    'id': hashlib.md5(ip.encode()).hexdigest()[:16],
                    'ip': ip,
                    'port': random.randint(1024, 65535),
                    'os': self._detect_os(ip)
                })
        
        print(f"✅ Found {len(targets)} targets")
        return targets

    def _check_host(self, ip):
        """Check if host is alive"""
        try:
            # Ping the host
            if sys.platform == 'win32':
                response = subprocess.run(
                    ['ping', '-n', '1', '-w', '100', ip],
                    capture_output=True,
                    timeout=1
                )
            else:
                response = subprocess.run(
                    ['ping', '-c', '1', '-W', '1', ip],
                    capture_output=True,
                    timeout=1
                )
            return response.returncode == 0
        except:
            return False

    def _detect_os(self, ip):
        """Detect operating system"""
        # Simple OS detection
        try:
            # Try different common ports
            common_ports = {
                'windows': 445,  # SMB
                'linux': 22,     # SSH
                'mac': 548       # AFP
            }
            
            for os_name, port in common_ports.items():
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((ip, port))
                sock.close()
                if result == 0:
                    return os_name
            
            return 'unknown'
        except:
            return 'unknown'

    def _infect_target(self, target):
        """Infect a target host"""
        print(f"🧟 Infecting target: {target['ip']}")
        
        try:
            # Simulate infection process
            time.sleep(random.uniform(0.1, 0.5))
            
            # Random success rate
            success = random.random() < self.spread_rate
            
            if success:
                print(f"✅ Target infected: {target['ip']}")
                return True
            else:
                print(f"❌ Infection failed: {target['ip']}")
                return False
                
        except Exception as e:
            print(f"❌ Infection error: {e}")
            return False

    def spread_massive(self, networks=None):
        """Massive infection spread"""
        if networks is None:
            networks = self.target_networks
        
        print(f"🧟 Starting massive infection spread...")
        
        # Spread to all networks
        for network in networks:
            self.spread_infection(network)
            time.sleep(random.uniform(0.1, 0.5))
        
        print(f"✅ Massive infection complete")
        return self.spread_stats

    def get_zombie_status(self):
        """Get status of zombie nodes"""
        return {
            'total_zombies': len(self.zombie_nodes),
            'active_zombies': self.spread_stats['active_zombies'],
            'total_infections': self.spread_stats['total_infections'],
            'successful_infections': self.spread_stats['successful_infections'],
            'failed_infections': self.spread_stats['failed_infections']
        }

    def get_statistics(self):
        """Get spreader statistics"""
        stats = {
            'total_zombies': len(self.zombie_nodes),
            'active_zombies': self.spread_stats['active_zombies'],
            'infection_counter': self.infection_counter,
            'spread_rate': self.spread_rate,
            'max_zombies': self.max_zombies,
            'total_infections': self.spread_stats['total_infections'],
            'successful_infections': self.spread_stats['successful_infections'],
            'failed_infections': self.spread_stats['failed_infections']
        }
        return stats

# Singleton instance
_zombie_spreader_instance = None

def get_zombie_spreader():
    """Get the singleton zombie spreader instance"""
    global _zombie_spreader_instance
    if _zombie_spreader_instance is None:
        _zombie_spreader_instance = ZombieSpreader()
    return _zombie_spreader_instance

# Test the zombie spreader
if __name__ == "__main__":
    zs = get_zombie_spreader()
    print("Spreading infection...")
    zs.spread_infection()
    stats = zs.get_statistics()
    print(f"Statistics: {json.dumps(stats, indent=2)}")