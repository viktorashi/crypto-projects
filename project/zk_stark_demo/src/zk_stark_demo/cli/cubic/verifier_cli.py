
import argparse
import sys
import os

# Add src to path if running directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from zk_stark_demo.air_examples.cubic import CubicAIR
from zk_stark_demo.stark.verifier import StarkVerifier
from zk_stark_demo.algebra.field import FieldElement
from zk_stark_demo.utils.serialization import load_proof


def main() -> None:
    parser = argparse.ArgumentParser(description="zk-STARK Verifier for Cubic Computation")
    parser.add_argument(
        "--proof",
        type=str,
        default="proof_cubic.json",
        help="Path to proof.json",
    )
    # Optional args override public inputs from proof
    parser.add_argument(
        "--length", type=int, required=False, help="Length of computation confirmed"
    )
    parser.add_argument(
        "--result", type=int, required=False, help="Expected result of the computation"
    )
    parser.add_argument(
        "--start", type=int, required=False, help="Start value of the computation"
    )

    args = parser.parse_args()

    proof = load_proof(args.proof)

    # Determine inputs
    length = args.length
    result_val = args.result
    start_val = args.start
    
    if length is None or result_val is None or start_val is None:
        if "public_inputs" in proof:
             inputs = proof["public_inputs"]
             if length is None: length = inputs.get("length")
             if result_val is None: result_val = inputs.get("result")
             if start_val is None: start_val = inputs.get("start_value")
    
    # Defaults handled in AIR logic? No, need explicit.
    # If start_val still None, assume AIR default? (CubicAIR defaults to 1)
    if start_val is None:
        start_val = 1
        
    if length is None or result_val is None:
        print("Error: Public inputs (length/result) not provided in args or proof.")
        sys.exit(1)

    print(f"Verifying proof for Cubic(len={length}, start={start_val}) == {result_val}...")

    air = CubicAIR(length, FieldElement(result_val), start_value=start_val)
    verifier = StarkVerifier(air)

    if verifier.verify(proof):
        print("✅ Proof Verified! Computation is valid.")
    else:
        print("❌ Verification Failed! Proof is invalid.")
        sys.exit(1)


if __name__ == "__main__":
    main()
