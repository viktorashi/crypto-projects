import argparse
import sys
import os
from typing import Any

# Add src to path if running directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from zk_stark_demo.cli.base import BaseVerifierCLI
from zk_stark_demo.air_examples.fibonacci import FibonacciAIR
from zk_stark_demo.algebra.field import FieldElement


class FibonacciVerifierCLI(BaseVerifierCLI[FibonacciAIR]):
    """Verifier CLI for Fibonacci sequence computation."""

    @property
    def description(self) -> str:
        return "zk-STARK Verifier for Fibonacci"

    @property
    def default_proof_file(self) -> str:
        return "proof.json"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--length",
            type=int,
            required=False,
            help="Length of computation confirmed",
        )
        parser.add_argument(
            "--result",
            type=int,
            required=False,
            help="Expected result of the computation",
        )

    def create_air_from_proof(
        self, args: argparse.Namespace, proof: dict[str, Any]
    ) -> FibonacciAIR:
        # Determine length and result from args or proof
        length = args.length
        result_val = args.result

        if length is None or result_val is None:
            if "public_inputs" in proof:
                inputs = proof["public_inputs"]
                if length is None:
                    length = inputs.get("length")
                if result_val is None:
                    result_val = inputs.get("result")

        if length is None or result_val is None:
            print("Error: Public inputs (length/result) not provided in args or proof.")
            sys.exit(1)

        return FibonacciAIR(length, FieldElement(result_val))

    def get_verification_message(
        self, args: argparse.Namespace, proof: dict[str, Any]
    ) -> str:
        inputs = proof.get("public_inputs", {})
        length = args.length or inputs.get("length", "?")
        result = args.result or inputs.get("result", "?")
        return f"Verifying proof for Fib(len={length}) == {result}..."


def main() -> None:
    cli = FibonacciVerifierCLI()
    cli.run()


if __name__ == "__main__":
    main()
