
import argparse
import sys
import os

# Add src to path if running directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from zk_stark_demo.examples.fibonacci import FibonacciAIR
from zk_stark_demo.stark.prover import StarkProver
from zk_stark_demo.algebra.field import FieldElement
from zk_stark_demo.utils.serialization import save_proof

def main():
    parser = argparse.ArgumentParser(description="zk-STARK Prover for Fibonacci")
    parser.add_argument("--length", type=int, default=8, help="Length of Fibonacci sequence (must be power of 2)")
    parser.add_argument("--output", type=str, default="proof.json", help="Output file for the proof")
    
    args = parser.parse_args()
    
    length = args.length
    print(f"Generating proof for Fibonacci sequence of length {length}...")
    
    # 1. Setup AIR & Trace
    # Result is unknown initially, so we just run trace first?
    # Actually, we can just instantiate AIR with dummy result to generate trace, 
    # then instantiate real AIR.
    
    dummy_air = FibonacciAIR(length, FieldElement(0))
    trace_data = dummy_air.generate_trace([1, 1])
    result = trace_data[-1][1]
    
    print(f"Computed Result: {result.val}")
    
    real_air = FibonacciAIR(length, result)
    
    # 2. Prove
    prover = StarkProver(real_air, trace_data)
    proof = prover.prove()
    
    # 3. Save
    save_proof(proof, args.output)
    print(f"Proof saved to {args.output}")

if __name__ == '__main__':
    main()
