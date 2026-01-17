
from typing import List
from ..algebra.field import FieldElement
from ..algebra.polynomial import Polynomial
from .trace import Trace
from .lde import LowDegreeExtension
from .air import AIR
from .fri import FriProver
from .channel import Channel

class StarkProver:
    def __init__(self, air: AIR, trace_data: List[List[FieldElement]]):
        self.air = air
        self.trace = Trace(trace_data, air.trace_width())
        self.channel = Channel()
        
    def prove(self):
        # 1. Low Degree Extension
        blowup_factor = 4 # Security parameter
        lde = LowDegreeExtension(self.trace, blowup_factor)
        
        # 2. Commit to Trace
        # LDE has 'lde_evaluations' (cols). We treat rows as leaves.
        # Tree commits to [ row0, row1, ... ]
        # We need to flatten rows to bytes?
        # Creating Merkle Tree of LDE domain values.
        # lde_evaluations is list of columns. Transpose to rows.
        lde_rows = []
        for i in range(lde.lde_length):
            row = [lde.lde_evaluations[c][i] for c in range(self.trace.width)]
            lde_rows.append(row)
            
        # Simplification: Commit directly to the objects? 
        # MerkleTree expects bytes.
        # We'll use a helper to serialize.
        # But wait, FRI expects polynomial commitments.
        # Here we commit to the Evaluated Trace.
        
        # For this demo, let's skip explicit Trace Merkle Tree interaction with user?
        # No, Channel needs the root.
        
        # We commit to the Trace.
        trace_tree = self.generate_merkle_tree(lde_rows)
        self.channel.send(trace_tree.root)
        
        # 3. Get Constraint Coefficients (Alpha)
        # We have N constraints (from AIR).
        # We want to form H(x) = sum( alpha_i * C_i(x) )
        # Verifier sends random alphas.
        
        # For simplicity, let's assume 2 transition constraints.
        # In general, we ask AIR.
        # Check step 0 to see number of constraints?
        dummy_step = [FieldElement(0)] * self.air.trace_width()
        constraints = self.air.evaluate_transition_constraints(dummy_step, dummy_step)
        num_constraints = len(constraints)
        
        alphas = [self.channel.receive_random_field_element() for _ in range(num_constraints)]
        
        # Boundary coefficients
        boundary_constraints = self.air.get_boundary_constraints()
        betas = [self.channel.receive_random_field_element() for _ in boundary_constraints]
        
        # 4. Compute Composition Polynomial Evaluations on LDE Domain
        # Q(x) = sum(alpha * Tr(x)/Z_tr(x)) + sum(beta * Bound(x)/Z_b(x))
        
        composition_evals = []
        domain_lde = lde.domain_lde
        trace_length_fe = FieldElement(self.air.trace_length())
        
        g_trace = FieldElement.generator_of_order(self.air.trace_length())
        g_inv = g_trace.inv() # g^{N-1}
        
        lde_length = lde.lde_length
        for i in range(lde_length):
            x = domain_lde[i]
            current_state = lde_rows[i]
            
            next_idx = (i + blowup_factor) % lde_length
            next_state = lde_rows[next_idx]
            
            # --- Transition Constraints ---
            constraints_val = self.air.evaluate_transition_constraints(current_state, next_state)
            
            # Z_trans(x) = (x^N - 1) / (x - g^{N-1})
            numerator_z = x.pow(self.air.trace_length()) - FieldElement(1)
            denominator_z = x - g_inv
            z_trans_x = numerator_z / denominator_z
            
            if z_trans_x == FieldElement(0):
                 # Should not happen on shifted domain
                 z_trans_x = FieldElement(1) 
            
            term_transition = FieldElement(0)
            for k in range(num_constraints):
                term_transition = term_transition + alphas[k] * constraints_val[k]
            
            term_transition = term_transition / z_trans_x
            
            # --- Boundary Constraints ---
            term_boundary = FieldElement(0)
            for k, (step, reg, val) in enumerate(boundary_constraints):
                # Constraint: (Trace[reg] - val) / (x - g^step)
                # T_reg(x) comes from current_state
                t_val = current_state[reg]
                
                # target point x_k = g^step
                x_k = g_trace.pow(step)
                
                num_b = t_val - val
                den_b = x - x_k
                
                term_boundary = term_boundary + betas[k] * (num_b / den_b)
                
            q_x = term_transition + term_boundary
            composition_evals.append(q_x)
            
        # 5. Run FRI on this Composition Polynomial
        subset_domain = domain_lde[:self.air.trace_length()]
        subset_vals = composition_evals[:self.air.trace_length()]
        q_poly = Polynomial.lagrange_interpolate(subset_domain, subset_vals)
        
        # 6. FRI
        fri_prover = FriProver(q_poly, domain_lde) # Use full domain for FRI
        fri_commitments, final_const = fri_prover.generate_proof(self.channel)
        
        # 7. Construct Proof
        
        # Query Phase
        num_queries = 10
        indices = []
        for _ in range(num_queries):
            idx = self.channel.receive_random_int(0, lde.lde_length)
            indices.append(idx)
            
        fri_layer_proofs = fri_prover.query_phase(indices)
        
        trace_queries = []
        for idx in indices:
             row_val = lde_rows[idx]
             path = trace_tree.get_authentication_path(idx)
             
             next_idx = (idx + blowup_factor) % lde.lde_length
             next_row_val = lde_rows[next_idx]
             next_path = trace_tree.get_authentication_path(next_idx)
             
             trace_queries.append({
                 'idx': idx,
                 'val': row_val,
                 'path': path,
                 'next_idx': next_idx,
                 'next_val': next_row_val,
                 'next_path': next_path
             })

        proof = {
            'trace_root': trace_tree.root,
            'fri_commitments': fri_commitments,
            'fri_final': final_const,
            'fri_layer_proofs': fri_layer_proofs,
            'trace_queries': trace_queries
        }
        
        return proof

    def generate_merkle_tree(self, rows):
        # Helper to commit to list of lists
        from ..algebra.merkle import MerkleTree
        # Serialize rows
        data = [str(r).encode() for r in rows]
        return MerkleTree(data)
