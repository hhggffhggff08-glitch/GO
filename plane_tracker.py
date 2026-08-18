# -*- coding: utf-8 -*-
# omniscient_radar/plane_tracker.py
# PROJECT: OMEGA_SPECTRE_GODFALL
# STATUS: PLANE_TRACKER — AIRCRAFT TRACKING

import os
import sys
import time
import json
import random
import threading
import hashlib
import base64
from collections import defaultdict

class PlaneTracker:
    """
    Plane Tracker Engine
    Tracks all aircraft worldwide
    """
    
    def __init__(self, radar_core):
        self.radar = radar_core
        self.planes = {}
        self.flight_paths = {}
        self.tracking_active = False
        self.tracking_threads = []
        self.tracker_stats = {
            'total_planes_tracked': 0,
            'active_planes': 0,
            'update_frequency': 0.1
        }
        
        print("✈️ Plane Tracker Initialized")

    def start_tracking(self):
        """Start plane tracking"""
        print("✈️ Starting plane tracking...")
        self.tracking_active = True
        
        thread = threading.Thread(
            target=self._tracking_loop,
            daemon=True
        )
        thread.start()
        self.tracking_threads.append(thread)
        
        print("✅ Plane tracking started")
        return True

    def _tracking_loop(self):
        """Main tracking loop"""
        while self.tracking_active:
            targets = self.radar.get_targets('plane')
            self.planes = {p['id']: p for p in targets}
            self.tracker_stats['total_planes_tracked'] = len(self.planes)
            self.tracker_stats['active_planes'] = len(self.planes)
            
            # Update flight paths
            for plane_id, plane in self.planes.items():
                if plane_id not in self.flight_paths:
                    self.flight_paths[plane_id] = []
                self.flight_paths[plane_id].append({
                    'timestamp': time.time(),
                    'lat': plane['latitude'],
                    'lon': plane['longitude'],
                    'alt': plane.get('altitude', 0),
                    'speed': plane.get('speed', 0)
                })
                
                if len(self.flight_paths[plane_id]) > 1000:
                    self.flight_paths[plane_id] = self.flight_paths[plane_id][-500:]
            
            time.sleep(self.tracker_stats['update_frequency'])

    def get_plane(self, plane_id):
        """Get plane by ID"""
        return self.planes.get(plane_id)

    def get_flight_path(self, plane_id):
        """Get flight path of a plane"""
        return self.flight_paths.get(plane_id, [])

    def get_all_planes(self):
        """Get all tracked planes"""
        return list(self.planes.values())

    def stop_tracking(self):
        """Stop plane tracking"""
        print("✈️ Stopping plane tracking...")
        self.tracking_active = False
        self.tracking_threads = []
        print("✅ Plane tracking stopped")
        return True

    def get_statistics(self):
        """Get tracker statistics"""
        return {
            'total_planes_tracked': self.tracker_stats['total_planes_tracked'],
            'active_planes': self.tracker_stats['active_planes']
        }

# Singleton
_plane_tracker_instance = None

def get_plane_tracker(radar_core=None):
    global _plane_tracker_instance
    if _plane_tracker_instance is None:
        if radar_core is None:
            radar_core = get_omniscient_radar_core()
        _plane_tracker_instance = PlaneTracker(radar_core)
    return _plane_tracker_instance

# Test
if __name__ == "__main__":
    pt = get_plane_tracker()
    print(f"Statistics: {json.dumps(pt.get_statistics(), indent=2)}")