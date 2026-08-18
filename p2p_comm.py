# -*- coding: utf-8 -*-
# mesh_network/p2p_comm.py
# PROJECT: OMEGA_SPECTRE_GODFALL
# STATUS: P2P_COMM — DECENTRALIZED COMMUNICATION

import os
import sys
import time
import json
import socket
import threading
import hashlib
import base64
import random
import struct
import select
import queue
import datetime
from cryptography.fernet import Fernet
from collections import defaultdict
import numpy as np

class P2PNode:
    """
    P2P Communication Node
    Provides decentralized peer-to-peer communication
    """
    
    def __init__(self, node_id=None, port=8000):
        self.node_id = node_id or hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]
        self.port = port
        self.peers = {}
        self.known_nodes = {}
        self.message_queue = queue.Queue()
        self.is_running = False
        self.server_socket = None
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        self.routing_table = {}
        self.broadcast_history = set()
        self.connection_pool = {}
        self.stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'connections_established': 0,
            'connections_closed': 0
        }
        
        # Initialize node
        self._initialize_node()
        print(f"🌐 P2P Node Initialized: {self.node_id}")

    def _initialize_node(self):
        """Initialize the P2P node"""
        print("🌐 Initializing P2P Node...")
        
        # Create server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Bind to port
        try:
            self.server_socket.bind(('0.0.0.0', self.port))
            self.server_socket.listen(100)
            print(f"✅ Server listening on port {self.port}")
        except:
            print(f"⚠️ Could not bind to port {self.port}, using random port")
            self.server_socket.bind(('0.0.0.0', 0))
            self.port = self.server_socket.getsockname()[1]
            print(f"✅ Server listening on port {self.port}")

    def start(self):
        """Start the P2P node"""
        print("🌐 Starting P2P Node...")
        self.is_running = True
        
        # Start message handler thread
        threading.Thread(target=self._handle_messages, daemon=True).start()
        
        # Start peer discovery thread
        threading.Thread(target=self._discover_peers, daemon=True).start()
        
        # Start connection handler thread
        threading.Thread(target=self._handle_connections, daemon=True).start()
        
        print("✅ P2P Node Started")
        return True

    def stop(self):
        """Stop the P2P node"""
        print("🌐 Stopping P2P Node...")
        self.is_running = False
        if self.server_socket:
            self.server_socket.close()
        print("✅ P2P Node Stopped")
        return True

    def connect_to_peer(self, host, port):
        """Connect to a peer node"""
        print(f"🌐 Connecting to peer at {host}:{port}...")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((host, port))
            
            # Handshake
            handshake = {
                'type': 'handshake',
                'node_id': self.node_id,
                'port': self.port,
                'timestamp': time.time()
            }
            self._send_message(sock, handshake)
            
            # Wait for handshake response
            response = self._receive_message(sock)
            if response and response.get('type') == 'handshake_response':
                peer_id = response['node_id']
                self.peers[peer_id] = {
                    'socket': sock,
                    'host': host,
                    'port': port,
                    'connected_at': time.time(),
                    'last_seen': time.time()
                }
                self.known_nodes[peer_id] = {
                    'host': host,
                    'port': port,
                    'last_seen': time.time()
                }
                self.stats['connections_established'] += 1
                print(f"✅ Connected to peer: {peer_id}")
                return True
            else:
                sock.close()
                print("❌ Handshake failed")
                return False
                
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    def _handle_connections(self):
        """Handle incoming connections"""
        while self.is_running:
            try:
                # Accept connection
                client_sock, client_addr = self.server_socket.accept()
                client_sock.settimeout(5)
                
                # Receive handshake
                handshake = self._receive_message(client_sock)
                if handshake and handshake.get('type') == 'handshake':
                    peer_id = handshake['node_id']
                    peer_port = handshake.get('port', client_addr[1])
                    
                    # Send handshake response
                    response = {
                        'type': 'handshake_response',
                        'node_id': self.node_id,
                        'port': self.port,
                        'timestamp': time.time()
                    }
                    self._send_message(client_sock, response)
                    
                    # Add peer
                    self.peers[peer_id] = {
                        'socket': client_sock,
                        'host': client_addr[0],
                        'port': peer_port,
                        'connected_at': time.time(),
                        'last_seen': time.time()
                    }
                    self.known_nodes[peer_id] = {
                        'host': client_addr[0],
                        'port': peer_port,
                        'last_seen': time.time()
                    }
                    self.stats['connections_established'] += 1
                    print(f"✅ Peer connected: {peer_id}")
                    
                    # Start peer handler thread
                    threading.Thread(
                        target=self._handle_peer,
                        args=(peer_id, client_sock),
                        daemon=True
                    ).start()
                else:
                    client_sock.close()
                    
            except Exception as e:
                if self.is_running:
                    print(f"⚠️ Connection error: {e}")
                time.sleep(0.1)

    def _handle_peer(self, peer_id, sock):
        """Handle messages from a peer"""
        while self.is_running and peer_id in self.peers:
            try:
                # Receive message
                message = self._receive_message(sock)
                if message:
                    # Process message
                    self._process_message(peer_id, message)
                    self.stats['messages_received'] += 1
                    self.peers[peer_id]['last_seen'] = time.time()
                else:
                    break
            except:
                break
        
        # Close connection on disconnect
        self._disconnect_peer(peer_id)

    def _disconnect_peer(self, peer_id):
        """Disconnect from a peer"""
        if peer_id in self.peers:
            try:
                self.peers[peer_id]['socket'].close()
            except:
                pass
            del self.peers[peer_id]
            self.stats['connections_closed'] += 1
            print(f"🔌 Disconnected from peer: {peer_id}")

    def _send_message(self, sock, message):
        """Send a message over a socket"""
        try:
            # Encrypt message
            message_bytes = json.dumps(message).encode()
            encrypted = self.cipher.encrypt(message_bytes)
            
            # Send length + data
            length = len(encrypted)
            sock.send(struct.pack('!I', length))
            sock.send(encrypted)
            self.stats['messages_sent'] += 1
            return True
        except Exception as e:
            print(f"⚠️ Send error: {e}")
            return False

    def _receive_message(self, sock):
        """Receive a message from a socket"""
        try:
            # Receive length
            length_data = sock.recv(4)
            if not length_data:
                return None
            length = struct.unpack('!I', length_data)[0]
            
            # Receive data
            data = b''
            while len(data) < length:
                chunk = sock.recv(min(4096, length - len(data)))
                if not chunk:
                    return None
                data += chunk
            
            # Decrypt message
            decrypted = self.cipher.decrypt(data)
            message = json.loads(decrypted.decode())
            return message
        except Exception as e:
            return None

    def _process_message(self, sender_id, message):
        """Process a received message"""
        msg_type = message.get('type')
        
        if msg_type == 'broadcast':
            # Handle broadcast message
            content = message.get('content')
            sender = message.get('sender')
            msg_id = message.get('id')
            
            # Check if already seen
            if msg_id not in self.broadcast_history:
                self.broadcast_history.add(msg_id)
                
                # Forward to other peers
                self.broadcast_message(content, sender_id, msg_id)
                
                # Process locally
                print(f"📨 Broadcast from {sender}: {content[:50]}...")
        
        elif msg_type == 'data':
            # Handle data message
            data = message.get('data')
            print(f"📊 Data from {sender_id}: {data[:50]}...")
        
        elif msg_type == 'ping':
            # Handle ping
            self.send_message(sender_id, {'type': 'pong'})
        
        elif msg_type == 'pong':
            # Handle pong
            pass
        
        elif msg_type == 'discover':
            # Handle discovery
            self.send_message(sender_id, {
                'type': 'discover_response',
                'nodes': list(self.known_nodes.keys())
            })
        
        elif msg_type == 'discover_response':
            # Handle discovery response
            nodes = message.get('nodes', [])
            for node_id in nodes:
                if node_id not in self.known_nodes and node_id != self.node_id:
                    # Store discovered node
                    self.known_nodes[node_id] = {
                        'host': None,  # Unknown host
                        'port': None,  # Unknown port
                        'last_seen': time.time(),
                        'discovered': True
                    }

    def send_message(self, peer_id, message):
        """Send a message to a specific peer"""
        if peer_id not in self.peers:
            print(f"⚠️ Peer not connected: {peer_id}")
            return False
        
        sock = self.peers[peer_id]['socket']
        return self._send_message(sock, message)

    def broadcast_message(self, content, exclude=None, msg_id=None):
        """Broadcast a message to all peers"""
        if msg_id is None:
            msg_id = hashlib.md5(f"{content}{time.time()}".encode()).hexdigest()
        
        message = {
            'type': 'broadcast',
            'sender': self.node_id,
            'content': content,
            'id': msg_id,
            'timestamp': time.time()
        }
        
        # Send to all peers
        for peer_id in list(self.peers.keys()):
            if peer_id != exclude:
                self.send_message(peer_id, message)
        
        # Add to broadcast history
        self.broadcast_history.add(msg_id)
        
        print(f"📢 Broadcast sent: {content[:50]}...")
        return True

    def _discover_peers(self):
        """Discover new peers in the network"""
        while self.is_running:
            # Send discovery messages
            for peer_id in list(self.peers.keys()):
                self.send_message(peer_id, {
                    'type': 'discover',
                    'timestamp': time.time()
                })
            
            # Prune old peers
            current_time = time.time()
            for peer_id in list(self.peers.keys()):
                if current_time - self.peers[peer_id]['last_seen'] > 60:
                    self._disconnect_peer(peer_id)
            
            time.sleep(30)

    def _handle_messages(self):
        """Handle messages from message queue"""
        while self.is_running:
            try:
                message = self.message_queue.get(timeout=1)
                # Process message
                self._process_message(None, message)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"⚠️ Message handling error: {e}")

    def get_peer_info(self):
        """Get information about connected peers"""
        return {
            'node_id': self.node_id,
            'port': self.port,
            'peers': len(self.peers),
            'known_nodes': len(self.known_nodes),
            'connected_peers': [p for p in self.peers.keys()],
            'stats': self.stats,
            'uptime': time.time() - self.stats.get('start_time', time.time())
        }

    def get_network_status(self):
        """Get network status"""
        return {
            'node_id': self.node_id,
            'is_running': self.is_running,
            'peers': len(self.peers),
            'messages_sent': self.stats['messages_sent'],
            'messages_received': self.stats['messages_received'],
            'connections': self.stats['connections_established'],
            'broadcast_history_size': len(self.broadcast_history)
        }

# Singleton instance
_p2p_node_instance = None

def get_p2p_node(port=8000):
    """Get the singleton P2P node instance"""
    global _p2p_node_instance
    if _p2p_node_instance is None:
        _p2p_node_instance = P2PNode(port=port)
    return _p2p_node_instance

# Test the P2P node
if __name__ == "__main__":
    node = get_p2p_node()
    node.start()
    print(f"Node Info: {json.dumps(node.get_peer_info(), indent=2)}")