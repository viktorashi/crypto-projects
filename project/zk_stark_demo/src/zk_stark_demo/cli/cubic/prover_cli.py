import argparse
import sys
import os
from typing import Any

# Add src to path if running directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from zk_stark_demo.cli.base import BaseProverCLI, validate_power_of_two
from zk_stark_demo.air_examples.cubic import CubicAIR
from zk_stark_demo.algebra.field import FieldElement


class CubicProverCLI(BaseProverCLI[CubicAIR]):
    """Prover CLI for Cubic computation."""

    @property
    def description(self) -> str:
        return "zk-STARK Prover for Cubic Computation"

    @property
    def default_output(self) -> str:
        return "proof_cubic.json"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--length",
            type=int,
            default=128,
            help="Length of computation lol (must be power of 2)",
        )
        parser.add_argument(
            "--start",
            type=int,
            default=1,
            help="Start value for the sequence",
        )

    def validate_args(self, args: argparse.Namespace) -> None:
        validate_power_of_two(args.length)

    def create_air_and_trace(
        self, args: argparse.Namespace
    ) -> tuple[CubicAIR, list[list[Any]]]:
        length: int = args.length
        start_val: int = args.start

        print(
            f"Generating proof for Cubic sequence of length {length} (start={start_val})..."
        )

        # Setup AIR & Trace with dummy result
        dummy_air = CubicAIR(length, FieldElement(0), start_value=start_val)
        trace_data = dummy_air.generate_trace()

        # Get actual result from trace
        result = trace_data[-1][0]
        print(f"Computed Result: {result.val}")

        real_air = CubicAIR(length, result, start_value=start_val)
        return real_air, trace_data


def main() -> None:
    cli = CubicProverCLI()
    cli.run()


if __name__ == "__main__":
    main()
