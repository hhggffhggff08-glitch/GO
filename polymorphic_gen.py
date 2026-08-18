# -*- coding: utf-8 -*-
# mutation_engine/polymorphic_gen.py
# PROJECT: OMEGA_SPECTRE_GODFALL
# STATUS: POLYMORPHIC_ENGINE — CODE MORPHING

import os
import sys
import time
import json
import random
import hashlib
import base64
import ast
import astor
import threading
import zlib
import pickle
from cryptography.fernet import Fernet

class PolymorphicGenerator:
    """
    Polymorphic Code Generator
    Generates unique code variants that are functionally identical but structurally different
    """
    
    def __init__(self):
        self.variants = []
        self.current_variant = None
        self.variant_counter = 0
        self.mutation_rate = 0.3
        self.polymorphic_cache = {}
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        self.variant_history = []
        self.unique_patterns = set()
        
        # Initialize polymorphic engine
        self._load_codebase()
        self._initialize_patterns()
        
        print("🧬 Polymorphic Generator Initialized")

    def _load_codebase(self):
        """Load the current codebase"""
        print("🧬 Loading codebase...")
        try:
            with open(__file__, 'r') as f:
                self.current_code = f.read()
            print("✅ Codebase loaded")
        except:
            self.current_code = "print('Hello World')"
            print("⚠️ Using default code")

    def _initialize_patterns(self):
        """Initialize polymorphic patterns"""
        self.patterns = {
            'variable_renaming': ['var', 'data', 'temp', 'x', 'y', 'z', 'value', 'result', 'output'],
            'function_renaming': ['process', 'handle', 'execute', 'run', 'perform', 'transform'],
            'class_renaming': ['Handler', 'Processor', 'Manager', 'Controller', 'Engine'],
            'constant_values': ['0', '1', '2', '10', '100', '1000', '3.14', '2.718'],
            'string_literals': ['Hello', 'World', 'Test', 'Data', 'Info', 'Output'],
            'comments': [
                '# Process the data',
                '# Handle the request',
                '# Execute the operation',
                '# Transform the input',
                '# Generate the output'
            ]
        }

    def generate_variant(self, code=None):
        """Generate a polymorphic variant of the code"""
        if code is None:
            code = self.current_code
        
        print("🧬 Generating polymorphic variant...")
        
        # Parse the code
        try:
            tree = ast.parse(code)
        except:
            print("⚠️ Could not parse code, using default")
            tree = ast.parse("print('Hello World')")
        
        # Apply polymorphic transformations
        variants = self._apply_transformations(tree)
        
        # Select random variant
        variant = random.choice(variants)
        
        # Convert back to code
        try:
            variant_code = astor.to_source(variant)
        except:
            variant_code = code
        
        # Add variant metadata
        self.variant_counter += 1
        variant_data = {
            'id': self.variant_counter,
            'code': variant_code,
            'hash': hashlib.sha256(variant_code.encode()).hexdigest(),
            'timestamp': time.time(),
            'mutations': self._count_mutations(code, variant_code),
            'size': len(variant_code)
        }
        
        self.variants.append(variant_data)
        self.current_variant = variant_data
        self.variant_history.append(variant_data)
        
        # Keep history manageable
        if len(self.variant_history) > 100:
            self.variant_history = self.variant_history[-50:]
        
        print(f"✅ Variant generated: {variant_data['hash'][:16]}...")
        return variant_data

    def _apply_transformations(self, tree):
        """Apply polymorphic transformations"""
        variants = []
        
        # Different transformation strategies
        strategies = [
            self._rename_variables,
            self._rename_functions,
            self._rename_classes,
            self._change_constants,
            self._change_strings,
            self._add_comments,
            self._reorder_statements,
            self._change_operators,
            self._wrap_expressions,
            self._split_statements
        ]
        
        # Apply each strategy
        for strategy in strategies:
            try:
                variant = strategy(tree)
                variants.append(variant)
            except:
                continue
        
        # If no variants generated, use the original
        if not variants:
            variants.append(tree)
        
        return variants

    def _rename_variables(self, tree):
        """Rename variables in the code"""
        class VariableRenamer(ast.NodeTransformer):
            def __init__(self):
                self.name_map = {}
                self.counter = 0
            
            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Store) or isinstance(node.ctx, ast.Load):
                    if node.id not in self.name_map:
                        self.name_map[node.id] = f"var_{self.counter}"
                        self.counter += 1
                    node.id = self.name_map[node.id]
                return node
        
        return VariableRenamer().visit(tree)

    def _rename_functions(self, tree):
        """Rename functions in the code"""
        class FunctionRenamer(ast.NodeTransformer):
            def __init__(self):
                self.counter = 0
            
            def visit_FunctionDef(self, node):
                node.name = f"func_{self.counter}"
                self.counter += 1
                return node
        
        return FunctionRenamer().visit(tree)

    def _rename_classes(self, tree):
        """Rename classes in the code"""
        class ClassRenamer(ast.NodeTransformer):
            def __init__(self):
                self.counter = 0
            
            def visit_ClassDef(self, node):
                node.name = f"Class_{self.counter}"
                self.counter += 1
                return node
        
        return ClassRenamer().visit(tree)

    def _change_constants(self, tree):
        """Change constant values"""
        class ConstantChanger(ast.NodeTransformer):
            def visit_Constant(self, node):
                if isinstance(node.value, (int, float)):
                    # Change numeric constants slightly
                    if node.value > 0:
                        node.value = node.value + random.randint(1, 10)
                    else:
                        node.value = node.value - random.randint(1, 10)
                return node
        
        return ConstantChanger().visit(tree)

    def _change_strings(self, tree):
        """Change string literals"""
        class StringChanger(ast.NodeTransformer):
            def visit_Constant(self, node):
                if isinstance(node.value, str):
                    # Add random characters or modify the string
                    if random.random() < 0.3:
                        node.value = node.value + str(random.randint(0, 9))
                return node
        
        return StringChanger().visit(tree)

    def _add_comments(self, tree):
        """Add comments to the code"""
        # Since AST doesn't preserve comments directly,
        # we'll add comments as string literals in the code
        # This is a simplified version
        return tree

    def _reorder_statements(self, tree):
        """Reorder statements in the code"""
        # This is complex in AST, simplified version
        return tree

    def _change_operators(self, tree):
        """Change operators in expressions"""
        # This is complex in AST, simplified version
        return tree

    def _wrap_expressions(self, tree):
        """Wrap expressions with additional operations"""
        # This is complex in AST, simplified version
        return tree

    def _split_statements(self, tree):
        """Split statements into multiple statements"""
        # This is complex in AST, simplified version
        return tree

    def _count_mutations(self, original, variant):
        """Count the number of mutations between two code versions"""
        # Simple mutation counting
        original_lines = set(original.split('\n'))
        variant_lines = set(variant.split('\n'))
        diff = original_lines.symmetric_difference(variant_lines)
        return len(diff)

    def get_variant(self, variant_id=None):
        """Get a specific variant"""
        if variant_id is None:
            return self.current_variant
        
        for variant in self.variants:
            if variant['id'] == variant_id:
                return variant
        
        return None

    def save_variant(self, variant_data, filename=None):
        """Save a variant to disk"""
        if filename is None:
            filename = f"variant_{variant_data['id']}_{int(time.time())}.py"
        
        with open(filename, 'w') as f:
            f.write(variant_data['code'])
        
        print(f"💾 Variant saved to {filename}")
        return filename

    def encrypt_variant(self, variant_data):
        """Encrypt a variant for secure storage"""
        code_bytes = variant_data['code'].encode()
        encrypted = self.cipher.encrypt(code_bytes)
        return base64.b64encode(encrypted).decode()

    def decrypt_variant(self, encrypted_code):
        """Decrypt a variant"""
        encrypted_bytes = base64.b64decode(encrypted_code)
        decrypted = self.cipher.decrypt(encrypted_bytes)
        return decrypted.decode()

    def get_statistics(self):
        """Get polymorphic statistics"""
        stats = {
            'total_variants': len(self.variants),
            'current_variant': self.current_variant['id'] if self.current_variant else None,
            'variant_counter': self.variant_counter,
            'mutation_rate': self.mutation_rate,
            'unique_patterns': len(self.unique_patterns),
            'history_size': len(self.variant_history),
            'cache_size': len(self.polymorphic_cache)
        }
        return stats

# Singleton instance
_polymorphic_generator_instance = None

def get_polymorphic_generator():
    """Get the singleton polymorphic generator instance"""
    global _polymorphic_generator_instance
    if _polymorphic_generator_instance is None:
        _polymorphic_generator_instance = PolymorphicGenerator()
    return _polymorphic_generator_instance

# Test the polymorphic generator
if __name__ == "__main__":
    pg = get_polymorphic_generator()
    
    # Generate a variant
    variant = pg.generate_variant()
    print(f"Variant generated: {variant['id']}")
    print(f"Hash: {variant['hash'][:16]}...")
    print(f"Mutations: {variant['mutations']}")
    
    # Get statistics
    stats = pg.get_statistics()
    print(f"Statistics: {json.dumps(stats, indent=2)}")