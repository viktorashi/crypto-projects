import sys
import os
import time

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from zk_stark_demo.examples.cubic import CubicAIR
from zk_stark_demo.stark.prover import StarkProver
from zk_stark_demo.stark.verifier import StarkVerifier
from zk_stark_demo.algebra.field import FieldElement


def main():
    print("=== Running Harder Example: Cubic Air ===")
    print("Computation: x_{k+1} = x_k^3 + x_k + 5")
    print("Constraint Degree: 3 (Higher than Fibonacci's 1)")

    # Use a longer trace to show it takes time
    # Power of 2 required.
    # length = 64 # Small for speed, but demonstrative.
    # Try 1024 for "longer"
    length = 128

    print(f"\n1. Generating Trace (Length {length})...")
    start_time = time.time()

    # Bootstrapping to find valid result
    dummy_air = CubicAIR(length, FieldElement(0))
    trace = dummy_air.generate_trace()
    result = trace[-1][0]

    print(f"   Result: {result}")
    print(f"   Time: {time.time() - start_time:.4f}s")

    real_air = CubicAIR(length, result)

    print("\n2. Generating Proof (Prover)...")
    start_time = time.time()
    prover = StarkProver(real_air, trace)
    proof = prover.prove()
    print(f"   Proof Generated!")
    print(f"   Time: {time.time() - start_time:.4f}s")
    print(f"   Proof size: ~{len(str(proof))} chars JSON representation")

    print("\n3. Verifying Proof (Verifier)...")
    start_time = time.time()
    verifier = StarkVerifier(real_air)
    is_valid = verifier.verify(proof)
    print(f"   Time: {time.time() - start_time:.4f}s")

    if is_valid:
        print("\n✅ SUCCESS: Cubic Computation Verified!")
    else:
        print("\n❌ FAILURE: Proof invalid.")


if __name__ == "__main__":
    main()
