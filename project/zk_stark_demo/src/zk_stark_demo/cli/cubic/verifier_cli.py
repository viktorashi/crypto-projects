import argparse
import sys
import os
from typing import Any

# Add src to path if running directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from zk_stark_demo.cli.base import BaseVerifierCLI
from zk_stark_demo.air_examples.cubic import CubicAIR
from zk_stark_demo.algebra.field import FieldElement


class CubicVerifierCLI(BaseVerifierCLI[CubicAIR]):
    """Verifier CLI for Cubic computation."""

    @property
    def description(self) -> str:
        return "zk-STARK Verifier for Cubic Computation"

    @property
    def default_proof_file(self) -> str:
        return "proof_cubic.json"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--length",
            type=int,
            default=None,
            help="Length of the trace",
        )
        parser.add_argument(
            "--result",
            type=int,
            default=None,
            help="Result of the computation",
        )
        parser.add_argument(
            "--start",
            type=int,
            default=None,
            help="Start value of the computation",
        )

    def create_air_from_proof(
        self, args: argparse.Namespace, proof: dict[str, Any]
    ) -> CubicAIR:
        # Determine inputs from args or proof
        length = args.length
        result_val = args.result
        start_val = args.start

        if length is None or result_val is None or start_val is None:
            if "public_inputs" in proof:
                inputs = proof["public_inputs"]
                if length is None:
                    length = inputs.get("length")
                if result_val is None:
                    result_val = inputs.get("result")
                if start_val is None:
                    start_val = inputs.get("start_value")

        # Default start_val if still None
        if start_val is None:
            start_val = 1

        if length is None or result_val is None:
            print("Error: Public inputs (length/result) not provided in args or proof.")
            sys.exit(1)

        return CubicAIR(length, FieldElement(result_val), start_value=start_val)

    def get_verification_message(
        self, args: argparse.Namespace, proof: dict[str, Any]
    ) -> str:
        inputs = proof.get("public_inputs", {})
        length = args.length or inputs.get("length", "?")
        start = args.start or inputs.get("start_value", 1)
        result = args.result or inputs.get("result", "?")
        return f"Verifying proof for Cubic(len={length}, start={start}) == {result}..."


def main() -> None:
    cli = CubicVerifierCLI()
    cli.run()


if __name__ == "__main__":
    main()
