
import argparse
import sys
import os
import json

# Add src to path if running directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from zk_stark_demo.air_examples.rollup import RollupAIR
from zk_stark_demo.stark.prover import StarkProver
from zk_stark_demo.utils.serialization import save_proof

def main() -> None:
    parser = argparse.ArgumentParser(description="zk-STARK Prover for High-Volume L2 Rollup")
    parser.add_argument(
        "--db",
        type=str,
        required=True,
        help="Path to JSON file containing users and transactions",
    )
    parser.add_argument(
        "--length", type=int, default=0, help="Trace length (power of 2). If 0, auto-calculates."
    )
    parser.add_argument(
        "--output", type=str, default="proof_rollup_large.json", help="Output file for the proof"
    )

    args = parser.parse_args()
    
    # Load DB
    with open(args.db, 'r') as f:
        data = json.load(f)
        
    users = data['users'] # List of initial balances. Index = UserID.
    txs = data['transactions'] # List of {from, to, amount}
    
    num_users = len(users)
    num_txs = len(txs)
    
    print(f"Loaded {num_users} users and {num_txs} transactions.")
    
    # Determine Length
    length = args.length
    if length == 0:
        # Next power of 2 greater than num_txs
        # Need trace length > num_txs because row i processes tx i, and we need N+1 rows for states.
        target = num_txs + 1
        length = 1 << (target - 1).bit_length()
        print(f"Auto-calculated trace length: {length}")
        
    # Check power of 2
    if (length & (length - 1) != 0):
        print("Error: Length must be power of 2")
        sys.exit(1)
        
    if num_txs >= length:
        print("Error: Trace length too small for transactions")
        sys.exit(1)
        
    print("Executing Transactions off-chain...")
    
    # 1. Execute "Off-chain" to get final state
    temp_air = RollupAIR(length, num_users, users, [0]*num_users)
    trace_data = temp_air.generate_trace(txs)
    
    final_balances = []
    final_row = trace_data[-1]
    for i in range(num_users):
        final_balances.append(final_row[i].val)
        
    print("Final Balances:")
    print(final_balances)
    
    # 2. Setup Real AIR
    real_air = RollupAIR(length, num_users, users, final_balances)
    
    # 3. Prove
    print("Generating Proof... (This may take a while for large N)")
    prover = StarkProver(real_air, trace_data)
    proof = prover.prove()
    
    save_proof(proof, args.output)
    print(f"Proof saved to {args.output}")

if __name__ == "__main__":
    main()
