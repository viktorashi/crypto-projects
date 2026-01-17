
from typing import List
from ..algebra.field import FieldElement
from ..algebra.merkle import MerkleTree
from .channel import Channel
from .fri_verifier import FriVerifier
from .air import AIR

class StarkVerifier:
    def __init__(self, air: AIR):
        self.air = air
        self.channel = Channel()
        
    def verify(self, proof):
        # 1. Read Trace Root
        trace_root = proof['trace_root']
        self.channel.send(trace_root)
        
        # 2. Generate Alphas (Constraint Combination Coefficients)
        # Must match Prover logic
        dummy_step = [FieldElement(0)] * self.air.trace_width()
        constraints = self.air.evaluate_transition_constraints(dummy_step, dummy_step)
        num_constraints = len(constraints)
        
        alphas = [self.channel.receive_random_field_element() for _ in range(num_constraints)]
        
        # Boundary coefficients
        boundary_constraints = self.air.get_boundary_constraints()
        betas = [self.channel.receive_random_field_element() for _ in boundary_constraints]
        
        # 3. Verify FRI
        # Construct FRI Proof object from the big proof
        fri_proof = {
            'commitments': proof['fri_commitments'],
            'final_constant': proof['fri_final'],
            'layer_proofs': proof['fri_layer_proofs']
        }
        
        fri_verifier = FriVerifier(fri_proof, self.channel)
        
        # Domain Params
        # We need the lengths.
        # Original Trace Length N
        N = self.air.trace_length()
        # Blowup k=4 (hardcoded in Prover for now, essential consistency)
        blowup_factor = 4 
        lde_length = N * blowup_factor
        
        if not fri_verifier.verify(domain_length=lde_length, domain_offset=FieldElement(3)):
            print("FRI Verification Failed")
            return False
            
        # 4. Consistency Check (Deep ALI / Constraint Check)
        
        num_queries = 10
        indices = []
        for _ in range(num_queries):
            idx = self.channel.receive_random_int(0, lde_length)
            indices.append(idx)
            
        trace_queries = proof['trace_queries']
        if len(trace_queries) != num_queries:
             print("Incorrect number of trace queries")
             return False
             
        # Re-derive domains
        g = FieldElement.generator_of_order(N)
        # LDE domain generator h s.t. h^k = g?
        shift = FieldElement(3)
        h = FieldElement.generator_of_order(lde_length)
        
        # Check each query
        for i, q in enumerate(trace_queries):
            idx = indices[i] # Expected index
            if q['idx'] != idx:
                print(f"Index mismatch: {q['idx']} != {idx}")
                return False
                
            # Verify Trace Merkle Paths
            row_val = q['val']
            # Reconstruct leaf
            leaf_data = str(row_val).encode()
            if not MerkleTree.verify_claim(trace_root, leaf_data, q['path'], idx):
                 print(f"Trace Merkle verify failed at {idx}")
                 return False
                 
            # Verify Next Step
            next_idx = q['next_idx']
            expected_next = (idx + blowup_factor) % lde_length
            if next_idx != expected_next:
                return False
            next_row_val = q['next_val']
            next_leaf = str(next_row_val).encode()
            if not MerkleTree.verify_claim(trace_root, next_leaf, q['next_path'], next_idx):
                 print(f"Trace Next Merkle verify failed at {next_idx}")
                 return False
                 
            # Compute Q(x) from Trace Values
            x = shift * h.pow(idx)
            
            # --- Transition Constraints ---
            constraints_val = self.air.evaluate_transition_constraints(row_val, next_row_val)
            numerator = FieldElement(0)
            for k in range(num_constraints):
                numerator = numerator + alphas[k] * constraints_val[k]
                
            # Z(x) = (x^N - 1) / (x - g^{N-1})
            g_inv = g.inv()
            numerator_z = x.pow(N) - FieldElement(1)
            denominator_z = x - g_inv
            z_x = numerator_z / denominator_z
            
            expected_q = numerator / z_x
            
            # --- Boundary Constraints ---
            term_boundary = FieldElement(0)
            for k, (step, reg, val) in enumerate(boundary_constraints):
                 # Constraint: (Trace[reg] - val) / (x - g^step)
                 t_val = row_val[reg]
                 x_k = g.pow(step)
                 
                 num_b = t_val - val
                 den_b = x - x_k
                 term_boundary = term_boundary + betas[k] * (num_b / den_b)
            
            expected_q = expected_q + term_boundary
            
            # Check against FRI value
            layer_0_proofs = fri_proof['layer_proofs'][0]
            found_fri_val = None
            for p in layer_0_proofs:
                if p['idx'] == idx:
                    found_fri_val = p['val']
                    break
            
            if found_fri_val is None:
                print("FRI proof missing index")
                return False
                
            if expected_q != found_fri_val:
                print(f"Constraint consistency failed. Q(x) {expected_q} != FRI {found_fri_val}")
                return False
                
        return True
