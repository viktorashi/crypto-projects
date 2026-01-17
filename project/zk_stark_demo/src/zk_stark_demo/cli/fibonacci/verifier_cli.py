import argparse
import sys
import os

# Add src to path if running directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from zk_stark_demo.air_examples.fibonacci import FibonacciAIR
from zk_stark_demo.stark.verifier import StarkVerifier
from zk_stark_demo.algebra.field import FieldElement
from zk_stark_demo.utils.serialization import load_proof


def main() -> None:
    parser = argparse.ArgumentParser(description="zk-STARK Verifier for Fibonacci")
    parser.add_argument(
        "--proof",
        type=str,
        default="proof.json",
        help="Path to proof.json",
    )
    parser.add_argument(
        "--length", type=int, required=False, help="Length of computation confirmed"
    )
    parser.add_argument(
        "--result", type=int, required=False, help="Expected result of the computation"
    )

    args = parser.parse_args()

    proof = load_proof(args.proof)

    # Determine length and result
    length = args.length
    result_val = args.result

    if length is None or result_val is None:
        # Try to load from proof
        if "public_inputs" in proof:
            inputs = proof["public_inputs"]
            if length is None:
                length = inputs.get("length")
            if result_val is None:
                # result might be int (from JSON)
                result_val = inputs.get("result")

    if length is None or result_val is None:
        print("Error: Public inputs (length/result) not provided in args or proof.")
        sys.exit(1)

    print(f"Verifying proof for Fib(len={length}) == {result_val}...")

    air = FibonacciAIR(length, FieldElement(result_val))
    verifier = StarkVerifier(air)

    if verifier.verify(proof):
        print("✅ Proof Verified! Computation is valid.")
    else:
        print("❌ Verification Failed! Proof is invalid.")
        sys.exit(1)


if __name__ == "__main__":
    main()
