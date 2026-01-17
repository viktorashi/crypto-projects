
import argparse
import sys
import os

# Add src to path if running directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from zk_stark_demo.examples.fibonacci import FibonacciAIR
from zk_stark_demo.stark.verifier import StarkVerifier
from zk_stark_demo.algebra.field import FieldElement
from zk_stark_demo.utils.serialization import load_proof

def main():
    parser = argparse.ArgumentParser(description="zk-STARK Verifier for Fibonacci")
    parser.add_argument("--proof", type=str, required=True, help="Path to proof.json")
    parser.add_argument("--length", type=int, required=True, help="Length of computation confirmed")
    parser.add_argument("--result", type=int, required=True, help="Expected result of the computation")
    
    args = parser.parse_args()
    
    print(f"Verifying proof for Fib(len={args.length}) == {args.result}...")
    
    proof = load_proof(args.proof)
    
    air = FibonacciAIR(args.length, FieldElement(args.result))
    verifier = StarkVerifier(air)
    
    if verifier.verify(proof):
        print("✅ Proof Verified! Computation is valid.")
    else:
        print("❌ Verification Failed! Proof is invalid.")
        sys.exit(1)

if __name__ == '__main__':
    main()
