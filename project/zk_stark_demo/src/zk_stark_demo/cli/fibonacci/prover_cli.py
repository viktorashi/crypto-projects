import argparse
import sys
import os
from typing import Any

# Add src to path if running directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from zk_stark_demo.cli.base import BaseProverCLI, validate_power_of_two
from zk_stark_demo.air_examples.fibonacci import FibonacciAIR
from zk_stark_demo.algebra.field import FieldElement


class FibonacciProverCLI(BaseProverCLI[FibonacciAIR]):
    """Prover CLI for Fibonacci sequence computation."""

    @property
    def description(self) -> str:
        return "zk-STARK Prover for Fibonacci"

    @property
    def default_output(self) -> str:
        return "proof.json"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--length",
            type=int,
            default=8,
            help="Length of Fibonacci sequence (must be power of 2)",
        )

    def validate_args(self, args: argparse.Namespace) -> None:
        validate_power_of_two(args.length)

    def create_air_and_trace(
        self, args: argparse.Namespace
    ) -> tuple[FibonacciAIR, list[list[Any]]]:
        length: int = args.length
        print(f"Generating proof for Fibonacci sequence of length {length}...")

        # Setup AIR & Trace
        dummy_air = FibonacciAIR(length, FieldElement(0))
        trace_data = dummy_air.generate_trace([1, 1])
        result = trace_data[-1][1]

        print(f"Computed Result: {result.val}")

        real_air = FibonacciAIR(length, result)
        return real_air, trace_data


def main() -> None:
    cli = FibonacciProverCLI()
    cli.run()


if __name__ == "__main__":
    main()
