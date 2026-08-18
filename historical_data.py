# -*- coding: utf-8 -*-
# omniscient_radar/historical_data.py
# PROJECT: OMEGA_SPECTRE_GODFALL
# STATUS: HISTORICAL_DATA — HISTORICAL RECORDS

import os
import sys
import time
import json
import random
import threading
import hashlib
import base64
from collections import defaultdict

class HistoricalData:
    """
    Historical Data Engine
    Stores and retrieves historical radar data
    """
    
    def __init__(self, radar_core):
        self.radar = radar_core
        self.history = []
        self.historical_objects = {}
        self.active_recording = False
        self.recording_threads = []
        self.history_stats = {
            'total_records': 0,
            'history_size_gb': 0,
            'record_frequency': 0.1
        }
        
        print("📚 Historical Data Initialized")

    def start_recording(self):
        """Start recording historical data"""
        print("📚 Starting historical data recording...")
        self.active_recording = True
        
        thread = threading.Thread(
            target=self._recording_loop,
            daemon=True
        )
        thread.start()
        self.recording_threads.append(thread)
        
        print("✅ Historical data recording started")
        return True

    def _recording_loop(self):
        """Main recording loop"""
        while self.active_recording:
            targets = self.radar.get_targets()
            
            record = {
                'timestamp': time.time(),
                'targets': targets,
                'total_objects': len(targets)
            }
            self.history.append(record)
            self.history_stats['total_records'] += 1
            
            # Keep last 10000 records
            if len(self.history) > 10000:
                self.history = self.history[-10000:]
            
            # Update historical objects
            for target in targets:
                obj_id = target['id']
                if obj_id not in self.historical_objects:
                    self.historical_objects[obj_id] = []
                self.historical_objects[obj_id].append({
                    'timestamp': time.time(),
                    'data': target
                })
                
                # Keep last 1000 records per object
                if len(self.historical_objects[obj_id]) > 1000:
                    self.historical_objects[obj_id] = self.historical_objects[obj_id][-1000:]
            
            self.history_stats['history_size_gb'] = len(json.dumps(self.history)) / (1024**3)
            
            time.sleep(self.history_stats['record_frequency'])

    def get_history(self, time_range=None):
        """Get historical data"""
        if time_range is None:
            return self.history
        
        current_time = time.time()
        return [r for r in self.history if current_time - r['timestamp'] <= time_range]

    def get_object_history(self, object_id):
        """Get history of a specific object"""
        return self.historical_objects.get(object_id, [])

    def stop_recording(self):
        """Stop historical data recording"""
        print("📚 Stopping historical data recording...")
        self.active_recording = False
        self.recording_threads = []
        print("✅ Historical data recording stopped")
        return True

    def get_statistics(self):
        """Get history statistics"""
        return {
            'total_records': self.history_stats['total_records'],
            'history_size_gb': self.history_stats['history_size_gb']
        }

# Singleton
_historical_data_instance = None

def get_historical_data(radar_core=None):
    global _historical_data_instance
    if _historical_data_instance is None:
        if radar_core is None:
            radar_core = get_omniscient_radar_core()
        _historical_data_instance = HistoricalData(radar_core)
    return _historical_data_instance

# Test
if __name__ == "__main__":
    hd = get_historical_data()
    print(f"Statistics: {json.dumps(hd.get_statistics(), indent=2)}")