# -*- coding: utf-8 -*-
# omniscient_radar/global_mapper.py
# PROJECT: OMEGA_SPECTRE_GODFALL
# STATUS: GLOBAL_MAPPER — INTERACTIVE WORLD MAP

import os
import sys
import time
import json
import random
import threading
import numpy as np
import hashlib
import base64
from collections import defaultdict

class GlobalMapper:
    """
    Global Mapper Engine
    Interactive world map showing all detected objects
    """
    
    def __init__(self, radar_core):
        self.radar = radar_core
        self.map_objects = []
        self.map_layers = {}
        self.map_data = {}
        self.active_mapping = False
        self.mapping_threads = []
        self.mapper_stats = {
            'total_objects_mapped': 0,
            'map_layers': 0,
            'update_frequency': 0.1
        }
        
        # Initialize map layers
        self._initialize_map_layers()
        print("🌍 Global Mapper Initialized")

    def _initialize_map_layers(self):
        """Initialize map layers"""
        self.map_layers = {
            'vehicles': {'color': 'blue', 'icon': '🚗'},
            'routers': {'color': 'orange', 'icon': '📡'},
            'satellites': {'color': 'silver', 'icon': '🛰️'},
            'drones': {'color': 'purple', 'icon': '🛸'},
            'planes': {'color': 'white', 'icon': '✈️'},
            'ships': {'color': 'navy', 'icon': '🚢'},
            'devices': {'color': 'green', 'icon': '💻'},
            'networks': {'color': 'cyan', 'icon': '🌐'},
            'underground': {'color': 'brown', 'icon': '⛰️'},
            'underwater': {'color': 'aqua', 'icon': '🌊'},
            'space': {'color': 'black', 'icon': '🌌'}
        }
        self.mapper_stats['map_layers'] = len(self.map_layers)

    def start_mapping(self):
        """Start real-time mapping"""
        print("🌍 Starting global mapping...")
        self.active_mapping = True
        
        # Start mapping thread
        thread = threading.Thread(
            target=self._mapping_loop,
            daemon=True
        )
        thread.start()
        self.mapping_threads.append(thread)
        
        print("✅ Global mapping started")
        return True

    def _mapping_loop(self):
        """Main mapping loop"""
        while self.active_mapping:
            targets = self.radar.get_targets()
            self.map_objects = targets
            self.mapper_stats['total_objects_mapped'] = len(targets)
            
            # Update map data
            self._update_map_data(targets)
            
            time.sleep(self.mapper_stats['update_frequency'])

    def _update_map_data(self, targets):
        """Update map data with current targets"""
        for target in targets:
            obj_type = target['type']
            if obj_type in self.map_layers:
                layer_info = self.map_layers[obj_type]
                
                if obj_type not in self.map_data:
                    self.map_data[obj_type] = []
                
                self.map_data[obj_type].append({
                    'id': target['id'],
                    'lat': target['latitude'],
                    'lon': target['longitude'],
                    'alt': target.get('altitude', 0),
                    'color': layer_info['color'],
                    'icon': layer_info['icon'],
                    'speed': target.get('speed', 0),
                    'heading': target.get('heading', 0)
                })

    def get_map_data(self, layer_type=None):
        """Get map data for a specific layer or all layers"""
        if layer_type is None:
            return self.map_data
        return self.map_data.get(layer_type, [])

    def stop_mapping(self):
        """Stop global mapping"""
        print("🌍 Stopping global mapping...")
        self.active_mapping = False
        self.mapping_threads = []
        print("✅ Global mapping stopped")
        return True

    def get_statistics(self):
        """Get mapper statistics"""
        return {
            'total_objects_mapped': self.mapper_stats['total_objects_mapped'],
            'map_layers': self.mapper_stats['map_layers'],
            'update_frequency': self.mapper_stats['update_frequency']
        }

# Singleton
_global_mapper_instance = None

def get_global_mapper(radar_core=None):
    global _global_mapper_instance
    if _global_mapper_instance is None:
        if radar_core is None:
            radar_core = get_omniscient_radar_core()
        _global_mapper_instance = GlobalMapper(radar_core)
    return _global_mapper_instance

# Test
if __name__ == "__main__":
    from radar_core import get_omniscient_radar_core
    radar = get_omniscient_radar_core()
    gm = get_global_mapper(radar)
    print(f"Statistics: {json.dumps(gm.get_statistics(), indent=2)}")