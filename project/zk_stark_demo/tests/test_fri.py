
import unittest
import sys
import os
import random

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from zk_stark_demo.algebra.field import FieldElement
from zk_stark_demo.algebra.polynomial import Polynomial
from zk_stark_demo.stark.fri import FriProver
from zk_stark_demo.stark.fri_verifier import FriVerifier
from zk_stark_demo.stark.channel import Channel

class TestFRI(unittest.TestCase):
    def test_fri_integration(self):
        # 1. Setup
        # Create a polynomial of degree < N/2
        degree = 15
        N = 64 # Domain size (must be power of 2)
        coeffs = [random.randint(0, 1000) for _ in range(degree)]
        poly = Polynomial(coeffs)
        
        # Domain: roots of unity of order N
        g = FieldElement.generator_of_order(N)
        domain = [g.pow(i) for i in range(N)]
        
        # 2. Prover
        prover = FriProver(poly, domain)
        
        # Simulate interaction
        prover_channel = Channel()
        
        # Generate Proof (Commit Phase)
        commitments, final_const = prover.generate_proof(prover_channel)
        
        # Query Phase
        # Verifier asks for some random indices
        indices = [random.randint(0, N-1) for _ in range(5)]
        layer_proofs = prover.query_phase(indices)
        
        proof = {
            'commitments': commitments,
            'final_constant': final_const,
            'layer_proofs': layer_proofs
        }
        
        # 3. Verifier
        verifier_channel = Channel() # New channel, replay
        verifier = FriVerifier(proof, verifier_channel)
        
        result = verifier.verify(domain_length=N)
        self.assertTrue(result, "FRI Verification failed")

if __name__ == '__main__':
    unittest.main()
