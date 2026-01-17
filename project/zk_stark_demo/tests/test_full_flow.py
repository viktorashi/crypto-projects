
import unittest
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from zk_stark_demo.air_examples.fibonacci import FibonacciAIR
from zk_stark_demo.stark.prover import StarkProver
from zk_stark_demo.stark.verifier import StarkVerifier
from zk_stark_demo.algebra.field import FieldElement

class TestFullFlow(unittest.TestCase):
    def test_fibonacci_proof(self):
        # 1. Setup computation
        # Length 8 (power of 2)
        # Sequence: 1, 1, 2, 3, 5, 8, 13, 21
        # Trace rows: [1, 1], [1, 2], [2, 3], [3, 5], [5, 8], [8, 13], [13, 21]... 
        # Wait, my generate_trace logic:
        # State: [a, b]. Next: [b, a+b].
        # Length 8 means 8 STEPS.
        # Step 0: [1, 1]
        # Step 1: [1, 2]
        # Step 2: [2, 3]
        # ...
        # Step 7: [13, 21]
        
        length = 8
        air = FibonacciAIR(length, FieldElement(34)) 
        # Note: Result value is the last element of the last step's register 1.
        
        trace = air.generate_trace([1, 1])
        self.assertEqual(len(trace), length, "Trace length incorrect")
        self.assertEqual(trace[-1][1], FieldElement(34), "Result incorrect")
        
        # 2. Prove
        prover = StarkProver(air, trace)
        proof = prover.prove()
        
        # 3. Verify
        verifier = StarkVerifier(air)
        result = verifier.verify(proof)
        
        self.assertTrue(result, "STARK Verification Failed")

if __name__ == '__main__':
    unittest.main()
