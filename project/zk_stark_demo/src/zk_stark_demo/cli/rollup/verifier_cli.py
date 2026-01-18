
import argparse
import sys
import os

# Add src to path if running directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from zk_stark_demo.air_examples.rollup import RollupAIR
from zk_stark_demo.stark.verifier import StarkVerifier
from zk_stark_demo.utils.serialization import load_proof

def main() -> None:
    parser = argparse.ArgumentParser(description="zk-STARK Verifier for High-Volume L2 Rollup")
    parser.add_argument("--proof", type=str, default="proof_rollup_large.json", help="Path to proof.json")
    
    args = parser.parse_args()
    proof = load_proof(args.proof)
    
    print("Verifying Rollup Batch...")
    
    inputs = proof.get('public_inputs', {})
    if not inputs:
        print("Error: No public inputs in proof.")
        sys.exit(1)
        
    length = inputs['length']
    num_users = inputs['num_users']
    init_bal = inputs['initial_balances']
    final_bal = inputs['final_balances']
    
    print(f"Batch Size: {length}")
    print(f"Users: {num_users}")
    print(f"Initial State Root (Hash of balances? Here just raw): {init_bal}")
    print(f"Final State Root: {final_bal}")
    
    air = RollupAIR(length, num_users, init_bal, final_bal)
    verifier = StarkVerifier(air)
    
    if verifier.verify(proof):
        print("✅ Proof Verified! The state transition is valid based on executed transactions.")
    else:
        print("❌ Verification Failed! Invalid batch.")
        sys.exit(1)

if __name__ == "__main__":
    main()
