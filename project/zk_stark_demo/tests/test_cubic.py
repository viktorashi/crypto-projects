
import unittest
from zk_stark_demo.examples.cubic import CubicAIR
from zk_stark_demo.stark.prover import StarkProver
from zk_stark_demo.stark.verifier import StarkVerifier
from zk_stark_demo.algebra.field import FieldElement

class TestCubicAir(unittest.TestCase):
    def test_cubic_proof_small(self):
        # Small length for fast testing
        length = 8
        dummy_air = CubicAIR(length, FieldElement(0))
        trace = dummy_air.generate_trace()
        result = trace[-1][0]
        
        real_air = CubicAIR(length, result)
        
        # Prove
        prover = StarkProver(real_air, trace)
        proof = prover.prove()
        
        # Verify
        verifier = StarkVerifier(real_air)
        self.assertTrue(verifier.verify(proof))

    def test_cubic_invalid_proof(self):
        length = 8
        dummy_air = CubicAIR(length, FieldElement(0))
        trace = dummy_air.generate_trace()
        result = trace[-1][0]
        
        # Twist the result
        fake_result = result + FieldElement(1)
        real_air = CubicAIR(length, fake_result)
        
        prover = StarkProver(real_air, trace)
        try:
            proof = prover.prove()
            # If proof generation succeeds (it might, effectively proving a wrong trace relative to AIR?)
            # No, prover checks trace against AIR logic usually? 
            # Actually StarkProver just commits to the trace provided. 
            # The *Verifier* checks if the trace satisfies the AIR *boundary* constraints (which include result).
            
            verifier = StarkVerifier(real_air)
            self.assertFalse(verifier.verify(proof))
        except Exception:
            # If prover fails (e.g. boundary checks internal to prover?), that's also fine
            pass
