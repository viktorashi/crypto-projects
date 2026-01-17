from __future__ import annotations
from typing import List, Tuple, Dict, Any
from ..algebra.field import FieldElement
from ..algebra.polynomial import Polynomial
from ..algebra.merkle import MerkleTree
from .channel import Channel

class FriLayer:
    def __init__(self, values: List[FieldElement], domain: List[FieldElement]) -> None:
        self.values: List[FieldElement] = values
        self.domain: List[FieldElement] = domain
        self.merkle_tree: MerkleTree = MerkleTree.commit(values)
        
    @property
    def root(self) -> bytes:
        return self.merkle_tree.root

class FriProver:
    """
    Implements the FRI Protocol (Prover side).
    Prove that a committed polynomial has low degree.
    """
    def __init__(self, polynomial: Polynomial, domain: List[FieldElement]) -> None:
        """
        polynomial: The polynomial to prove (usually composition polynomial).
        domain: The evaluation domain (must be power of 2 size).
        """
        self.polynomial: Polynomial = polynomial
        self.domain: List[FieldElement] = domain
        self.layers: List[FriLayer] = []
        
        # Initial evaluation
        values: List[FieldElement] = [polynomial.eval(x) for x in domain]
        self.layers.append(FriLayer(values, domain))

    def generate_proof(self, interaction_channel: Channel) -> Tuple[List[bytes], FieldElement]:
        """
        Run the FRI commit phase.
        interaction_channel: Simulated channel to get random challenges from verifier.
        Returns: list of layer roots, and final constant.
        """
        current_values = self.layers[0].values
        current_domain = self.layers[0].domain
        
        # Send initial root
        interaction_channel.send(self.layers[0].root)
        commitments: List[bytes] = [self.layers[0].root]
        
        # Folding
        while len(current_values) > 1: # Until we have a constant (degree 0)
            # 1. Get random beta from Verifier
            beta = interaction_channel.receive_random_field_element()
            
            # 2. Fold
            next_values: List[FieldElement] = []
            next_domain: List[FieldElement] = []
            
            length = len(current_values)
            assert length % 2 == 0
            half_len = length // 2
            
            inv_2 = FieldElement(2).inv()
            
            for i in range(half_len):
                x = current_domain[i]
                x_inv = x.inv()
                
                v_x = current_values[i]
                v_minus_x = current_values[i + half_len]
                
                even = (v_x + v_minus_x) * inv_2
                odd  = (v_x - v_minus_x) * inv_2 * x_inv
                
                next_val = even + beta * odd
                next_values.append(next_val)
                next_domain.append(x * x)
            
            # 3. Commit to new layer
            layer = FriLayer(next_values, next_domain)
            self.layers.append(layer)
            
            # Send new root
            interaction_channel.send(layer.root)
            commitments.append(layer.root)
            
            current_values = next_values
            current_domain = next_domain
            
        final_constant = current_values[0]
        return commitments, final_constant

    def query_phase(self, indices: List[int]) -> List[List[Dict[str, Any]]]:
        """
        Reveal values for specific indices to allow verification of folding.
        indices: indices in Layer 0 to query.
        Returns: 
           list of (value, path) for each layer corresponding to the indices.
        """
        all_layer_proofs: List[List[Dict[str, Any]]] = []
        
        current_indices: List[int] = indices
        for layer in self.layers[:-1]: # Don't need path for the constant (last layer)
            layer_proofs: List[Dict[str, Any]] = []
            for idx in current_indices:
                length = len(layer.values)
                half_len = length // 2
                
                idx_mod = idx % half_len
                partner_idx = (idx + half_len) % length
                
                val_idx = layer.values[idx]
                path_idx = layer.merkle_tree.get_authentication_path(idx)
                
                val_partner = layer.values[partner_idx]
                path_partner = layer.merkle_tree.get_authentication_path(partner_idx)
                
                layer_proofs.append({
                    'idx': idx,
                    'val': val_idx,
                    'path': path_idx,
                    'partner_idx': partner_idx,
                    'partner_val': val_partner,
                    'partner_path': path_partner
                })
            
            all_layer_proofs.append(layer_proofs)
            
            # Next layer indices
            current_indices = [idx % (len(layer.values)//2) for idx in current_indices]
        
        return all_layer_proofs 
