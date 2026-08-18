# -*- coding: utf-8 -*-
# omniscient_radar/heatmap_generator.py
# PROJECT: OMEGA_SPECTRE_GODFALL
# STATUS: HEATMAP_GENERATOR — GLOBAL HEATMAP

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

class HeatmapGenerator:
    """
    Heatmap Generator Engine
    Generates heatmaps of global activity
    """
    
    def __init__(self, radar_core):
        self.radar = radar_core
        self.heatmaps = {}
        self.active_generation = False
        self.generation_threads = []
        self.generator_stats = {
            'total_heatmaps_generated': 0,
            'update_frequency': 0.1
        }
        
        print("🔥 Heatmap Generator Initialized")

    def start_generation(self):
        """Start heatmap generation"""
        print("🔥 Starting heatmap generation...")
        self.active_generation = True
        
        thread = threading.Thread(
            target=self._generation_loop,
            daemon=True
        )
        thread.start()
        self.generation_threads.append(thread)
        
        print("✅ Heatmap generation started")
        return True

    def _generation_loop(self):
        """Main generation loop"""
        while self.active_generation:
            targets = self.radar.get_targets()
            self._generate_heatmaps(targets)
            self.generator_stats['total_heatmaps_generated'] += 1
            time.sleep(0.1)

    def _generate_heatmaps(self, targets):
        """Generate heatmaps from target data"""
        # Create grid for heatmap
        grid_size = 360  # 1 degree resolution
        heatmap_data = np.zeros((grid_size, grid_size))
        
        for target in targets:
            lat = target.get('latitude', 0)
            lon = target.get('longitude', 0)
            
            # Convert to grid coordinates
            lat_idx = int((lat + 90) * grid_size / 180)
            lon_idx = int((lon + 180) * grid_size / 360)
            
            if 0 <= lat_idx < grid_size and 0 <= lon_idx < grid_size:
                heatmap_data[lat_idx][lon_idx] += 1
        
        # Apply smoothing
        heatmap_data = self._apply_smoothing(heatmap_data)
        
        # Store heatmap
        self.heatmaps = {
            'data': heatmap_data.tolist(),
            'timestamp': time.time(),
            'resolution': grid_size
        }

    def _apply_smoothing(self, data):
        """Apply Gaussian smoothing to heatmap data"""
        # Simple smoothing using convolution
        smoothed = data.copy()
        for i in range(1, data.shape[0] - 1):
            for j in range(1, data.shape[1] - 1):
                smoothed[i][j] = (data[i-1][j-1] + data[i-1][j] + data[i-1][j+1] +
                                 data[i][j-1] + data[i][j] + data[i][j+1] +
                                 data[i+1][j-1] + data[i+1][j] + data[i+1][j+1]) / 9
        return smoothed

    def get_heatmap(self):
        """Get current heatmap"""
        return self.heatmaps

    def stop_generation(self):
        """Stop heatmap generation"""
        print("🔥 Stopping heatmap generation...")
        self.active_generation = False
        self.generation_threads = []
        print("✅ Heatmap generation stopped")
        return True

    def get_statistics(self):
        """Get generator statistics"""
        return {
            'total_heatmaps_generated': self.generator_stats['total_heatmaps_generated']
        }

# Singleton
_heatmap_generator_instance = None

def get_heatmap_generator(radar_core=None):
    global _heatmap_generator_instance
    if _heatmap_generator_instance is None:
        if radar_core is None:
            radar_core = get_omniscient_radar_core()
        _heatmap_generator_instance = HeatmapGenerator(radar_core)
    return _heatmap_generator_instance

# Test
if __name__ == "__main__":
    hg = get_heatmap_generator()
    print(f"Statistics: {json.dumps(hg.get_statistics(), indent=2)}")