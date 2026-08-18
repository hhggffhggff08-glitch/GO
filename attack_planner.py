# -*- coding: utf-8 -*-
# ai_autopilot/attack_planner.py
# PROJECT: OMEGA_SPECTRE_GODFALL
# STATUS: AI_PLANNER — AUTONOMOUS ATTACK PLANNING

import os
import sys
import time
import json
import random
import threading
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib
import base64

class AttackPlanner:
    """
    Autonomous Attack Planner
    Uses AI to plan and coordinate attacks
    """
    
    def __init__(self):
        self.plans = []
        self.active_plans = []
        self.completed_plans = []
        self.failed_plans = []
        self.plan_templates = {}
        self.strategy_weights = defaultdict(float)
        self.threat_assessment = {}
        self.resource_allocation = {}
        self.timeline = {}
        self.current_phase = "planning"
        self.last_plan_time = 0
        
        # Initialize planning system
        self._initialize_plan_templates()
        self._load_strategy_weights()
        
        print("🧠 Attack Planner Initialized")

    def _initialize_plan_templates(self):
        """Initialize attack plan templates"""
        print("🧠 Initializing Attack Plan Templates...")
        
        self.plan_templates = {
            'direct_breach': {
                'phases': [
                    {'phase': 'reconnaissance', 'duration': 0.1},
                    {'phase': 'breach', 'duration': 0.1},
                    {'phase': 'control', 'duration': 0.2},
                    {'phase': 'exfiltration', 'duration': 0.1},
                    {'phase': 'cleanup', 'duration': 0.1},
                ],
                'risk_level': 0.3,
                'success_rate': 0.7
            },
            'indirect_breach': {
                'phases': [
                    {'phase': 'reconnaissance', 'duration': 0.3},
                    {'phase': 'social_engineering', 'duration': 0.4},
                    {'phase': 'breach', 'duration': 0.2},
                    {'phase': 'control', 'duration': 0.3},
                    {'phase': 'exfiltration', 'duration': 0.2},
                    {'phase': 'cleanup', 'duration': 0.1},
                ],
                'risk_level': 0.2,
                'success_rate': 0.85
            },
            'multi_phase_breach': {
                'phases': [
                    {'phase': 'reconnaissance', 'duration': 0.2},
                    {'phase': 'initial_breach', 'duration': 0.3},
                    {'phase': 'lateral_movement', 'duration': 0.4},
                    {'phase': 'privilege_escalation', 'duration': 0.3},
                    {'phase': 'final_breach', 'duration': 0.2},
                    {'phase': 'control', 'duration': 0.3},
                    {'phase': 'exfiltration', 'duration': 0.2},
                    {'phase': 'cleanup', 'duration': 0.1},
                ],
                'risk_level': 0.4,
                'success_rate': 0.6
            },
            'distributed_breach': {
                'phases': [
                    {'phase': 'reconnaissance', 'duration': 0.1},
                    {'phase': 'distributed_attack', 'duration': 0.5},
                    {'phase': 'coordination', 'duration': 0.3},
                    {'phase': 'control', 'duration': 0.2},
                    {'phase': 'exfiltration', 'duration': 0.2},
                    {'phase': 'cleanup', 'duration': 0.1},
                ],
                'risk_level': 0.5,
                'success_rate': 0.5
            },
            'stealth_breach': {
                'phases': [
                    {'phase': 'reconnaissance', 'duration': 0.4},
                    {'phase': 'stealth_breach', 'duration': 0.3},
                    {'phase': 'control', 'duration': 0.2},
                    {'phase': 'exfiltration', 'duration': 0.3},
                    {'phase': 'cleanup', 'duration': 0.4},
                ],
                'risk_level': 0.1,
                'success_rate': 0.9
            }
        }
        
        print(f"✅ Initialized {len(self.plan_templates)} plan templates")

    def _load_strategy_weights(self):
        """Load strategy weights from previous learning"""
        weight_path = "strategy_weights.json"
        if os.path.exists(weight_path):
            try:
                with open(weight_path, 'r') as f:
                    self.strategy_weights = defaultdict(float, json.load(f))
                print("✅ Strategy weights loaded")
            except:
                print("⚠️ Could not load strategy weights")
        else:
            # Initialize default weights
            self.strategy_weights = defaultdict(float, {
                'direct_breach': 0.3,
                'indirect_breach': 0.4,
                'multi_phase_breach': 0.2,
                'distributed_breach': 0.1,
                'stealth_breach': 0.5
            })
            print("ℹ️ Default strategy weights initialized")

    def create_plan(self, target, strategy=None):
        """Create an attack plan for a target"""
        print(f"🧠 Creating attack plan for target: {target.get('name', 'unknown')}")
        
        # Select strategy if not specified
        if strategy is None:
            strategy = self._select_strategy(target)
        
        # Get plan template
        template = self.plan_templates.get(strategy, self.plan_templates['stealth_breach'])
        
        # Create custom plan
        plan = {
            'id': f"plan_{int(time.time())}_{hashlib.md5(str(target).encode()).hexdigest()[:8]}",
            'target': target,
            'strategy': strategy,
            'phases': [],
            'status': 'planned',
            'created': time.time(),
            'risk_level': template['risk_level'],
            'success_rate': template['success_rate'],
            'current_phase': 0,
            'progress': 0.0,
            'resources_allocated': {},
            'tasks': [],
            'timeline': [],
            'contingency_plans': []
        }
        
        # Build phases
        current_time = time.time()
        for phase_info in template['phases']:
            phase = {
                'name': phase_info['phase'],
                'start': current_time,
                'duration': phase_info['duration'] * 60,  # Convert to minutes
                'status': 'pending',
                'actions': [],
                'subtasks': []
            }
            current_time += phase['duration']
            plan['phases'].append(phase)
        
        # Add tasks
        plan['tasks'] = self._generate_tasks(plan)
        
        # Add timeline
        plan['timeline'] = self._generate_timeline(plan)
        
        # Add contingency plans
        plan['contingency_plans'] = self._generate_contingency_plans(plan)
        
        # Store plan
        self.plans.append(plan)
        self.active_plans.append(plan)
        
        print(f"✅ Plan created: {plan['id']}")
        return plan

    def _select_strategy(self, target):
        """Select the best strategy for a target"""
        # Calculate strategy scores
        scores = {}
        
        for strategy, weight in self.strategy_weights.items():
            # Base score from weight
            base_score = weight
            
            # Adjust based on target features
            if target.get('security_level', 0.5) > 0.7:
                # High security targets require stealth
                scores['stealth_breach'] = scores.get('stealth_breach', 0) + 0.3
            if target.get('value', 0.5) > 0.8:
                # High value targets need multi-phase
                scores['multi_phase_breach'] = scores.get('multi_phase_breach', 0) + 0.2
            if target.get('network_size', 0.5) > 0.7:
                # Large networks need distributed
                scores['distributed_breach'] = scores.get('distributed_breach', 0) + 0.2
            if target.get('detection_risk', 0.5) < 0.3:
                # Low risk targets can use direct
                scores['direct_breach'] = scores.get('direct_breach', 0) + 0.1
            
            # Add random factor
            scores[strategy] = scores.get(strategy, 0) + random.uniform(-0.1, 0.1)
        
        # Select best strategy
        best_strategy = max(scores, key=scores.get)
        return best_strategy

    def _generate_tasks(self, plan):
        """Generate tasks for a plan"""
        tasks = []
        
        for i, phase in enumerate(plan['phases']):
            phase_tasks = self._generate_phase_tasks(phase, plan['target'])
            tasks.extend(phase_tasks)
        
        return tasks

    def _generate_phase_tasks(self, phase, target):
        """Generate tasks for a specific phase"""
        tasks = []
        
        phase_name = phase['name']
        
        if phase_name == 'reconnaissance':
            tasks = [
                {'id': f"recon_1", 'description': 'Scan network', 'priority': 'high'},
                {'id': f"recon_2", 'description': 'Identify vulnerabilities', 'priority': 'high'},
                {'id': f"recon_3", 'description': 'Map infrastructure', 'priority': 'medium'},
            ]
        elif phase_name == 'breach' or phase_name == 'initial_breach':
            tasks = [
                {'id': f"breach_1", 'description': 'Exploit vulnerability', 'priority': 'high'},
                {'id': f"breach_2", 'description': 'Gain initial access', 'priority': 'high'},
                {'id': f"breach_3", 'description': 'Establish foothold', 'priority': 'medium'},
            ]
        elif phase_name == 'control':
            tasks = [
                {'id': f"control_1", 'description': 'Take control of systems', 'priority': 'high'},
                {'id': f"control_2", 'description': 'Install persistence', 'priority': 'high'},
                {'id': f"control_3", 'description': 'Monitor activity', 'priority': 'medium'},
            ]
        elif phase_name == 'exfiltration':
            tasks = [
                {'id': f"exfil_1", 'description': 'Collect data', 'priority': 'high'},
                {'id': f"exfil_2", 'description': 'Exfiltrate data', 'priority': 'high'},
                {'id': f"exfil_3", 'description': 'Encrypt exfiltrated data', 'priority': 'medium'},
            ]
        elif phase_name == 'cleanup':
            tasks = [
                {'id': f"cleanup_1", 'description': 'Remove traces', 'priority': 'high'},
                {'id': f"cleanup_2", 'description': 'Close backdoors', 'priority': 'high'},
                {'id': f"cleanup_3", 'description': 'Verify no evidence', 'priority': 'medium'},
            ]
        elif phase_name == 'social_engineering':
            tasks = [
                {'id': f"social_1", 'description': 'Research targets', 'priority': 'high'},
                {'id': f"social_2", 'description': 'Craft phishing messages', 'priority': 'high'},
                {'id': f"social_3", 'description': 'Execute social engineering', 'priority': 'high'},
            ]
        elif phase_name == 'lateral_movement':
            tasks = [
                {'id': f"lateral_1", 'description': 'Move to other systems', 'priority': 'high'},
                {'id': f"lateral_2", 'description': 'Expand control', 'priority': 'high'},
                {'id': f"lateral_3", 'description': 'Set up backdoors', 'priority': 'medium'},
            ]
        elif phase_name == 'privilege_escalation':
            tasks = [
                {'id': f"priv_1", 'description': 'Escalate privileges', 'priority': 'high'},
                {'id': f"priv_2", 'description': 'Gain admin access', 'priority': 'high'},
                {'id': f"priv_3", 'description': 'Maintain access', 'priority': 'medium'},
            ]
        elif phase_name == 'distributed_attack':
            tasks = [
                {'id': f"dist_1", 'description': 'Coordinate nodes', 'priority': 'high'},
                {'id': f"dist_2", 'description': 'Execute distributed attack', 'priority': 'high'},
                {'id': f"dist_3", 'description': 'Synchronize results', 'priority': 'medium'},
            ]
        elif phase_name == 'coordination':
            tasks = [
                {'id': f"coord_1", 'description': 'Coordinate attack phases', 'priority': 'high'},
                {'id': f"coord_2", 'description': 'Adjust based on feedback', 'priority': 'high'},
                {'id': f"coord_3", 'description': 'Finalize attack', 'priority': 'medium'},
            ]
        elif phase_name == 'stealth_breach':
            tasks = [
                {'id': f"stealth_1", 'description': 'Use zero-click exploit', 'priority': 'high'},
                {'id': f"stealth_2", 'description': 'Avoid detection', 'priority': 'high'},
                {'id': f"stealth_3", 'description': 'Maintain stealth', 'priority': 'medium'},
            ]
        
        return tasks

    def _generate_timeline(self, plan):
        """Generate timeline for a plan"""
        timeline = []
        current_time = time.time()
        
        for phase in plan['phases']:
            timeline.append({
                'phase': phase['name'],
                'start': current_time,
                'end': current_time + phase['duration'],
                'duration': phase['duration']
            })
            current_time += phase['duration']
        
        return timeline

    def _generate_contingency_plans(self, plan):
        """Generate contingency plans"""
        contingency_plans = []
        
        # Plan A: Alternative breach method
        alt_strategies = [s for s in self.plan_templates.keys() if s != plan['strategy']]
        if alt_strategies:
            alt_strategy = random.choice(alt_strategies)
            contingency_plans.append({
                'id': f"cont_{int(time.time())}",
                'condition': 'primary_breach_fails',
                'strategy': alt_strategy,
                'actions': ['retreat', 'try_alternative', 'increase_stealth']
            })
        
        # Plan B: Emergency cleanup
        contingency_plans.append({
            'id': f"cont_{int(time.time()) + 1}",
            'condition': 'detection_risk_high',
            'strategy': 'emergency_cleanup',
            'actions': ['erase_traces', 'close_backdoors', 'abort_mission']
        })
        
        # Plan C: Change target
        contingency_plans.append({
            'id': f"cont_{int(time.time()) + 2}",
            'condition': 'target_compromised',
            'strategy': 'change_target',
            'actions': ['abort_current', 'select_new_target', 'replan']
        })
        
        return contingency_plans

    def execute_plan(self, plan_id):
        """Execute a specific plan"""
        print(f"🧠 Executing plan: {plan_id}")
        
        # Find the plan
        plan = None
        for p in self.active_plans:
            if p['id'] == plan_id:
                plan = p
                break
        
        if plan is None:
            print("⚠️ Plan not found")
            return False
        
        # Start executing plan
        plan['status'] = 'executing'
        plan['start_time'] = time.time()
        
        # Execute each phase
        for phase in plan['phases']:
            phase['status'] = 'executing'
            phase['start'] = time.time()
            
            # Execute tasks in phase
            success = self._execute_phase(phase, plan['target'])
            
            phase['status'] = 'completed' if success else 'failed'
            phase['end'] = time.time()
            phase['duration'] = phase['end'] - phase['start']
            
            if not success:
                # Execute contingency plan
                self._execute_contingency(plan)
                plan['status'] = 'failed'
                self.active_plans.remove(plan)
                self.failed_plans.append(plan)
                return False
            
            # Update progress
            plan['progress'] += 1 / len(plan['phases'])
            plan['current_phase'] += 1
        
        # Plan completed successfully
        plan['status'] = 'completed'
        plan['end_time'] = time.time()
        plan['progress'] = 1.0
        
        self.active_plans.remove(plan)
        self.completed_plans.append(plan)
        
        # Update strategy weights based on success
        self._update_strategy_weights(plan['strategy'], True)
        
        print(f"✅ Plan {plan_id} completed successfully")
        return True

    def _execute_phase(self, phase, target):
        """Execute a specific phase"""
        print(f"🧠 Executing phase: {phase['name']}")
        
        # Simulate phase execution
        time.sleep(0.1)  # Simulate work
        
        # Random success based on phase difficulty
        success_rate = 0.9  # 90% success rate
        success = random.random() < success_rate
        
        if success:
            print(f"✅ Phase {phase['name']} completed")
        else:
            print(f"❌ Phase {phase['name']} failed")
        
        return success

    def _execute_contingency(self, plan):
        """Execute contingency plan"""
        print(f"🧠 Executing contingency plan for {plan['id']}")
        
        contingency = plan.get('contingency_plans', [])
        if contingency:
            cont = contingency[0]
            print(f"🔄 Executing contingency: {cont['id']}")
            
            for action in cont['actions']:
                print(f"   🔄 Action: {action}")
                # Simulate action execution
                time.sleep(0.05)
        
        print("✅ Contingency plan executed")

    def _update_strategy_weights(self, strategy, success):
        """Update strategy weights based on success"""
        if success:
            self.strategy_weights[strategy] += 0.1
        else:
            self.strategy_weights[strategy] -= 0.05
        
        # Normalize weights
        total = sum(self.strategy_weights.values())
        if total > 0:
            for key in self.strategy_weights:
                self.strategy_weights[key] /= total
        
        # Save weights
        with open('strategy_weights.json', 'w') as f:
            json.dump(dict(self.strategy_weights), f)
        
        print(f"✅ Strategy weights updated")

    def get_plan_status(self, plan_id):
        """Get status of a plan"""
        for plan in self.plans:
            if plan['id'] == plan_id:
                return {
                    'id': plan['id'],
                    'status': plan['status'],
                    'progress': plan['progress'],
                    'current_phase': plan['current_phase'],
                    'total_phases': len(plan['phases']),
                    'start_time': plan.get('start_time'),
                    'end_time': plan.get('end_time'),
                    'risk_level': plan['risk_level'],
                    'success_rate': plan['success_rate']
                }
        return None

    def get_statistics(self):
        """Get planning statistics"""
        stats = {
            'total_plans': len(self.plans),
            'active_plans': len(self.active_plans),
            'completed_plans': len(self.completed_plans),
            'failed_plans': len(self.failed_plans),
            'success_rate': len(self.completed_plans) / max(1, len(self.completed_plans) + len(self.failed_plans)),
            'strategy_weights': dict(self.strategy_weights),
            'current_phase': self.current_phase,
            'last_plan_time': self.last_plan_time
        }
        return stats

# Singleton instance
_attack_planner_instance = None

def get_attack_planner():
    """Get the singleton attack planner instance"""
    global _attack_planner_instance
    if _attack_planner_instance is None:
        _attack_planner_instance = AttackPlanner()
    return _attack_planner_instance

# Test the attack planner
if __name__ == "__main__":
    ap = get_attack_planner()
    
    # Create a target
    target = {
        'name': 'Test Corporation',
        'security_level': 0.4,
        'value': 0.8,
        'network_size': 0.6,
        'detection_risk': 0.3
    }
    
    # Create a plan
    plan = ap.create_plan(target)
    print(f"Plan created: {plan['id']}")
    print(f"Strategy: {plan['strategy']}")
    print(f"Phases: {len(plan['phases'])}")
    print(f"Tasks: {len(plan['tasks'])}")
    
    # Execute the plan
    success = ap.execute_plan(plan['id'])
    print(f"Plan executed: {success}")
    
    # Get statistics
    stats = ap.get_statistics()
    print(f"Statistics: {json.dumps(stats, indent=2, default=str)}")