
import argparse
import sys
import os

# Add src to path if running directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from zk_stark_demo.air_examples.cubic import CubicAIR
from zk_stark_demo.stark.prover import StarkProver
from zk_stark_demo.algebra.field import FieldElement
from zk_stark_demo.utils.serialization import save_proof

def main() -> None:
    parser = argparse.ArgumentParser(description="zk-STARK Prover for Cubic Computation")
    parser.add_argument(
        "--length",
        type=int,
        default=128,
        help="Length of computation (must be power of 2)",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=1,
        help="Start value for the sequence",
    )
    parser.add_argument(
        "--output", type=str, default="proof_cubic.json", help="Output file for the proof"
    )

    args = parser.parse_args()

    length: int = args.length
    start_val: int = args.start
    
    # Check power of 2
    if (length & (length - 1) != 0) or length == 0:
        print(f"Error: Length {length} is not a power of 2. STARK protocol requires power-of-two trace length.")
        sys.exit(1)
        
    print(f"Generating proof for Cubic sequence of length {length} (start={start_val})...")

    # 1. Setup AIR & Trace
    # Use dummy result to generate trace
    dummy_air = CubicAIR(length, FieldElement(0), start_value=start_val)
    trace_data = dummy_air.generate_trace()
    
    # Get actual result from trace
    result = trace_data[-1][0]
    print(f"Computed Result: {result.val}")

    real_air = CubicAIR(length, result, start_value=start_val)

    # 2. Prove
    prover = StarkProver(real_air, trace_data)
    proof = prover.prove()

    # 3. Save
    save_proof(proof, args.output)
    print(f"Proof saved to {args.output}")


if __name__ == "__main__":
    main()
