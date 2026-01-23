import argparse
import sys
import os
import json
from typing import Any

# Add src to path if running directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from zk_stark_demo.cli.base import BaseProverCLI, validate_power_of_two
from zk_stark_demo.air_examples.rollup import RollupAIR


class RollupProverCLI(BaseProverCLI[RollupAIR]):
    """Prover CLI for High-Volume L2 Rollup computation."""

    @property
    def description(self) -> str:
        return "zk-STARK Prover for High-Volume L2 Rollup"

    @property
    def default_output(self) -> str:
        return "proof_rollup_large.json"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--db",
            type=str,
            default="mock_db.json",
            help="Path to JSON file containing users and transactions",
        )
        parser.add_argument(
            "--length",
            type=int,
            default=0,
            help="Trace length (power of 2). If 0, auto-calculates.",
        )

    def validate_args(self, args: argparse.Namespace) -> None:
        # Length validation is done after auto-calculation in create_air_and_trace
        pass

    def create_air_and_trace(
        self, args: argparse.Namespace
    ) -> tuple[RollupAIR, list[list[Any]]]:
        # Load DB
        db_path = args.db
        if not os.path.isabs(db_path):
             # Try to find it relative to this file
             current_dir = os.path.dirname(os.path.abspath(__file__))
             potential_path = os.path.join(current_dir, db_path)
             if os.path.exists(potential_path):
                 db_path = potential_path
                 
        with open(db_path, "r") as f:
            data = json.load(f)

        users = data["users"]  # List of initial balances. Index = UserID.
        txs = data["transactions"]  # List of {from, to, amount}

        num_users = len(users)
        num_txs = len(txs)

        print(f"Loaded {num_users} users and {num_txs} transactions.")

        # Determine Length
        length = args.length
        if length == 0:
            # Next power of 2 greater than num_txs
            target = num_txs + 1
            length = 1 << (target - 1).bit_length()
            print(f"Auto-calculated trace length: {length}")

        # Validate power of 2
        validate_power_of_two(length)

        if num_txs >= length:
            print("Error: Trace length too small for transactions")
            sys.exit(1)

        print("Executing Transactions off-chain...")

        # Execute "Off-chain" to get final state
        temp_air = RollupAIR(length, num_users, users, [0] * num_users)
        trace_data = temp_air.generate_trace(txs)

        final_balances = []
        final_row = trace_data[-1]
        for i in range(num_users):
            final_balances.append(final_row[i].val)

        print("Final Balances:")
        print(final_balances)

        # Setup Real AIR
        real_air = RollupAIR(length, num_users, users, final_balances)
        return real_air, trace_data


def main() -> None:
    cli = RollupProverCLI()
    cli.run()


if __name__ == "__main__":
    main()
