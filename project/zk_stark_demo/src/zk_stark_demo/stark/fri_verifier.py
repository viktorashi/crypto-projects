from __future__ import annotations
from typing import List, Dict, Any, Optional, TypedDict
from ..algebra.field import FieldElement
from ..algebra.merkle import MerkleTree
from .channel import Channel

class FriProof(TypedDict):
    commitments: List[bytes]
    final_constant: FieldElement
    layer_proofs: List[List[Dict[str, Any]]]

class FriVerifier:
    def __init__(self, proof: FriProof, interaction_channel: Channel) -> None:
        """
        proof: {
            'commitments': [root0, root1, ...],
            'final_constant': FieldElement,
            'layer_proofs': [ [ {idx, val, path...} ], ... ]
        }
        """
        self.commitments: List[bytes] = proof['commitments']
        self.final_constant: FieldElement = proof['final_constant']
        self.layer_proofs: List[List[Dict[str, Any]]] = proof['layer_proofs']
        self.channel: Channel = interaction_channel

    def verify(self, domain_length: int, domain_offset: Optional[FieldElement] = None) -> bool:
        """
        1. Reconstruct the random betas using the channel (Fiat-Shamir).
        2. Verify paths and folding for each layer.
        """
        if domain_offset is None:
            domain_offset = FieldElement(1)
            
        # 1. Replay Commit Phase to get Betas
        betas: List[FieldElement] = []
        for root in self.commitments[:-1]:
            self.channel.send(root)
            beta = self.channel.receive_random_field_element()
            betas.append(beta)
            
        # Send the last root (final constant commitment) to update state, 
        # but don't draw a beta for it (nothing to fold)
        self.channel.send(self.commitments[-1])
            
        # 2. Verify Query Phase
        g = FieldElement.generator_of_order(domain_length)
        current_domain_gen: FieldElement = g
        current_offset: FieldElement = domain_offset
        current_length: int = domain_length
        
        for i in range(len(self.layer_proofs)):
            layer_data = self.layer_proofs[i] # List of queries for this layer
            root = self.commitments[i]
            beta = betas[i]
            
            next_layer_queries: Dict[int, FieldElement] = {} # Map index -> value for consistency check with next layer
            
            for query in layer_data:
                idx: int = query['idx']
                val: FieldElement = query['val']
                path: List[bytes] = query['path']
                partner_idx: int = query['partner_idx']
                partner_val: FieldElement = query['partner_val']
                partner_path: List[bytes] = query['partner_path']
                
                # 1. Verify Paths
                if not MerkleTree.verify_claim(root, str(val).encode(), path, idx):
                    return False
                if not MerkleTree.verify_claim(root, str(partner_val).encode(), partner_path, partner_idx):
                    return False
                    
                # 2. Verify Folding Relation
                x = current_offset * current_domain_gen.pow(idx)
                x_inv = x.inv()
                
                inv_2 = FieldElement(2).inv()
                even = (val + partner_val) * inv_2
                odd  = (val - partner_val) * inv_2 * x_inv
                next_val = even + beta * odd
                
                # The index in the next layer is idx % (current_length // 2)
                next_idx = idx % (current_length // 2)
                
                # Store expectation for next layer check
                if next_idx in next_layer_queries:
                    if next_layer_queries[next_idx] != next_val:
                        return False # Consistency error
                else:
                    next_layer_queries[next_idx] = next_val

            # Prepare for next layer
            current_domain_gen = current_domain_gen.pow(2)
            current_offset = current_offset * current_offset
            current_length //= 2
            
            # Check consistency with NEXT layer actual values
            if i < len(self.layer_proofs) - 1:
                next_proof_layer = self.layer_proofs[i+1]
                for n_idx, n_val in next_layer_queries.items():
                    found = False
                    for q in next_proof_layer:
                        if q['idx'] == n_idx:
                            if q['val'] != n_val:
                                return False
                            found = True
                            break
                        if q['partner_idx'] == n_idx:
                            if q['partner_val'] != n_val:
                                return False
                            found = True
                            break
                    if not found:
                         return False
            else:
                # This was the last Merkle layer. 
                for n_val in next_layer_queries.values():
                    if n_val != self.final_constant:
                        return False

        return True
