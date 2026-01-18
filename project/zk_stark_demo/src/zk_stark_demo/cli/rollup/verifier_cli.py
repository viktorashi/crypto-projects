import argparse
import sys
import os
from typing import Any

# Add src to path if running directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from zk_stark_demo.cli.base import BaseVerifierCLI
from zk_stark_demo.air_examples.rollup import RollupAIR


class RollupVerifierCLI(BaseVerifierCLI[RollupAIR]):
    """Verifier CLI for High-Volume L2 Rollup computation."""

    @property
    def description(self) -> str:
        return "zk-STARK Verifier for High-Volume L2 Rollup"

    @property
    def default_proof_file(self) -> str:
        return "proof_rollup_large.json"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--db",
            type=str,
            default="mock_db.json",
            help="Path to the mock database file",
        )

    def create_air_from_proof(
        self, args: argparse.Namespace, proof: dict[str, Any]
    ) -> RollupAIR:
        inputs = proof.get("public_inputs", {})
        if not inputs:
            print("Error: No public inputs in proof.")
            sys.exit(1)

        length = inputs["length"]
        num_users = inputs["num_users"]
        init_bal = inputs["initial_balances"]
        final_bal = inputs["final_balances"]

        return RollupAIR(length, num_users, init_bal, final_bal)

    def get_verification_message(
        self, args: argparse.Namespace, proof: dict[str, Any]
    ) -> str:
        inputs = proof.get("public_inputs", {})
        length = inputs.get("length", "?")
        num_users = inputs.get("num_users", "?")
        init_bal = inputs.get("initial_balances", "?")
        final_bal = inputs.get("final_balances", "?")

        return (
            f"Verifying Rollup Batch...\n"
            f"Batch Size: {length}\n"
            f"Users: {num_users}\n"
            f"Initial State Root (Hash of balances? Here just raw): {init_bal}\n"
            f"Final State Root: {final_bal}"
        )


def main() -> None:
    cli = RollupVerifierCLI()
    cli.run()


if __name__ == "__main__":
    main()
