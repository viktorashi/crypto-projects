from __future__ import annotations
from typing import List, Dict, Any
from ..algebra.field import FieldElement
from ..algebra.polynomial import Polynomial
from ..algebra.merkle import MerkleTree
from .trace import Trace
from .lde import LowDegreeExtension
from .air import AIR
from .fri import FriProver
from .channel import Channel
from ..algebra.fft import ifft

class StarkProver:
    def __init__(self, air: AIR, trace_data: List[List[FieldElement]]) -> None:
        self.air: AIR = air
        self.trace: Trace = Trace(trace_data, air.trace_width())
        self.channel: Channel = Channel()
        
    def prove(self) -> Dict[str, Any]:
        # 1. Low Degree Extension
        blowup_factor = 4 # Security parameter
        lde = LowDegreeExtension(self.trace, blowup_factor)
        
        # 2. Commit to Trace
        lde_rows: List[List[FieldElement]] = []
        for i in range(lde.lde_length):
            row = [lde.lde_evaluations[c][i] for c in range(self.trace.width)]
            lde_rows.append(row)
            
        trace_tree = self.generate_merkle_tree(lde_rows)
        self.channel.send(trace_tree.root)
        
        # 3. Get Constraint Coefficients (Alpha)
        dummy_step: List[FieldElement] = [FieldElement(0)] * self.air.trace_width()
        constraints = self.air.evaluate_transition_constraints(dummy_step, dummy_step)
        num_constraints = len(constraints)
        
        alphas: List[FieldElement] = [self.channel.receive_random_field_element() for _ in range(num_constraints)]
        
        # Boundary coefficients
        boundary_constraints = self.air.get_boundary_constraints()
        betas: List[FieldElement] = [self.channel.receive_random_field_element() for _ in boundary_constraints]
        
        # 4. Compute Composition Polynomial Evaluations on LDE Domain
        composition_evals: List[FieldElement] = []
        domain_lde = lde.domain_lde
        
        g_trace = FieldElement.generator_of_order(self.trace.length)
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
            numerator_z = x.pow(self.trace.length) - FieldElement(1)
            denominator_z = x - g_inv
            z_trans_x = numerator_z / denominator_z
            
            if z_trans_x == FieldElement(0):
                 z_trans_x = FieldElement(1) 
            
            term_transition = FieldElement(0)
            for k in range(num_constraints):
                term_transition = term_transition + alphas[k] * constraints_val[k]
            
            term_transition = term_transition / z_trans_x
            
            # --- Boundary Constraints ---
            term_boundary = FieldElement(0)
            for k, (step, reg, val) in enumerate(boundary_constraints):
                t_val = current_state[reg]
                x_k = g_trace.pow(step)
                
                num_b = t_val - val
                den_b = x - x_k
                
                term_boundary = term_boundary + betas[k] * (num_b / den_b)
                
            q_x = term_transition + term_boundary
            composition_evals.append(q_x)
            
        # 5. Run FRI on this Composition Polynomial
        # 5. Interpolate Q(x)
        # The degree of Q(x) is approximately (constraint_degree - 1) * trace_length.
        # For linear constraints (deg=1), Q(x) is roughly trace_length (due to Z(x) division).
        # For deg=2, Q(x) is ~ 2N - N = N.
        # Generally we need enough points to uniquely determine Q(x).
        
        c_degree = self.air.constraint_degree()
        # Q(x) = C(T) / Z(x). Deg(C) = deg_c * (N-1). Deg(Z) = N-1.
        # Deg(Q) = (deg_c - 1) * (N-1).
        # We need at least Deg(Q) + 1 points.
        # If deg_c = 1, we need 0+1 = 1 point? (Constant). 
        # But effectively we use trace_length to be safe and cover Z(x) quirks.
        
        target_degree = max(self.trace.length, (c_degree - 1) * self.trace.length)
        # Ensure we don't exceed LDE domain
        if target_degree > lde_length:
            raise ValueError(f"Constraint degree {c_degree} too high for blowup factor")
            

        # 5. Interpolate Q(x)
        # We need to recover the coefficients of Q(x) from its evaluations.
        # domain_lde is a coset: shift * <h>, size = blowup * N
        # We want to pick a subset of points that forms a coset of a smaller subgroup to use IFFT.
        
        # Determine strict degree bound
        expected_degree = (c_degree - 1) * self.trace.length + (self.trace.length - 1)
        # Actually Q * Z = C. Deg(Q) = Deg(C) - Deg(Z) = c_deg * (N-1) - (N-1) = (c_deg-1)*(N-1).
        # For c_deg=1, Deg(Q) = 0 (Constant??). 
        # Wait, strictly speaking for AIR constraints:
        # C(x) has degree roughly deg * N.
        # Z(x) has degree N.
        # Q(x) has degree (deg-1) * N.
        
        # We need a domain size usually >= degree + 1.
        # We'll use the smallest power of 2 that covers the degree, derived from our available blowup.
        
        # For this demo, let's assume we can use N evaluations if degree <= N-1 (deg=1 or 2 constraints typically fine).
        # If we need more, we decrease stride.
        
        needed_len = self.trace.length
        while needed_len <= expected_degree:
             needed_len *= 2
             
        stride = lde_length // needed_len
        
        subset_vals = composition_evals[::stride]
        
        # These evaluations are on the domain: shift * h^{0}, shift * h^{stride}, ...
        # Let H = h^stride. This is a generator of order `needed_len`.
        # Points are s, sH, sH^2... (Coset)
        
        subgroup_generator = lde.h.pow(stride)
        
        # 1. Coset IFFT:
        # P(z) = Q(s * z). We have evaluations of P at 1, H, H^2...
        # coeffs_P = ifft(vals, H)
        coeffs_p = ifft(subset_vals, subgroup_generator)
        
        # 2. Recover Q(x)
        # Q(x) = P(x/s). If P(z) = sum a_i z^i, Q(x) = sum a_i s^{-i} x^i
        # Scale coefficients by s^{-i}
        s_inv = lde.shift.inv()
        current_s_inv = FieldElement(1)
        coeffs_q = []
        for c in coeffs_p:
            coeffs_q.append(c * current_s_inv)
            current_s_inv = current_s_inv * s_inv
            
        q_poly = Polynomial(coeffs_q)
        
        # 6. FRI
        fri_prover = FriProver(q_poly, domain_lde, composition_evals) # Use full domain for FRI
        fri_commitments, final_const = fri_prover.generate_proof(self.channel)
        
        # 7. Construct Proof
        num_queries = 10
        indices: List[int] = []
        for _ in range(num_queries):
            idx = self.channel.receive_random_int(0, lde.lde_length)
            indices.append(idx)
            
        fri_layer_proofs = fri_prover.query_phase(indices)
        
        trace_queries: List[Dict[str, Any]] = []
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

        proof: Dict[str, Any] = {
            'trace_root': trace_tree.root,
            'fri_commitments': fri_commitments,
            'fri_final': final_const,
            'fri_layer_proofs': fri_layer_proofs,
            'trace_queries': trace_queries,
            'public_inputs': self.air.get_public_inputs()
        }
        
        return proof

    def generate_merkle_tree(self, rows: List[List[FieldElement]]) -> MerkleTree:
        # Helper to commit to list of lists
        data: List[bytes] = [str(r).encode() for r in rows]
        return MerkleTree(data)
