"""
Base classes for CLI applications to keep implementations DRY.
Provides abstract base classes for both Prover and Verifier CLIs.
"""

from abc import ABC, abstractmethod
import argparse
import sys
import os
from typing import Any, TypeVar, Generic

# Add src to path if running directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from zk_stark_demo.stark.prover import StarkProver
from zk_stark_demo.stark.verifier import StarkVerifier
from zk_stark_demo.stark.air import AIR
from zk_stark_demo.utils.serialization import save_proof, load_proof


# Type variable for AIR subclasses
AIR_T = TypeVar("AIR_T", bound=AIR)


class BaseProverCLI(ABC, Generic[AIR_T]):
    """
    Abstract base class for Prover CLI applications.

    Subclasses must implement:
        - description: str property for argparse help
        - default_output: str property for default output filename
        - add_arguments: method to add custom argparse arguments
        - create_air_and_trace: method to create AIR instance and generate trace
    """

    @property
    @abstractmethod
    def description(self) -> str:
        """Description for the argparse help message."""
        pass

    @property
    @abstractmethod
    def default_output(self) -> str:
        """Default output filename for the proof."""
        pass

    @abstractmethod
    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """
        Add custom arguments to the parser.

        Args:
            parser: The argparse.ArgumentParser to add arguments to.
        """
        pass

    @abstractmethod
    def create_air_and_trace(
        self, args: argparse.Namespace
    ) -> tuple[AIR_T, list[list[Any]]]:
        """
        Create the AIR instance and generate the trace.

        Args:
            args: Parsed command line arguments.

        Returns:
            A tuple of (configured AIR instance, trace data).
        """
        pass

    def validate_args(self, args: argparse.Namespace) -> None:
        """
        Optional validation of arguments. Override to add custom validation.
        Raise SystemExit with appropriate message if validation fails.

        Args:
            args: Parsed command line arguments.
        """
        pass

    def run(self) -> None:
        """Run the prover CLI application."""
        parser = argparse.ArgumentParser(description=self.description)

        # Add common output argument
        parser.add_argument(
            "--output",
            type=str,
            default=self.default_output,
            help="Output file for the proof",
        )

        # Add custom arguments
        self.add_arguments(parser)

        args = parser.parse_args()

        # Validate arguments
        self.validate_args(args)

        # Create AIR and generate trace
        air, trace_data = self.create_air_and_trace(args)

        # Generate proof
        print("Generating Proof...")
        prover = StarkProver(air, trace_data)
        proof = prover.prove()

        # Save proof
        save_proof(proof, args.output)
        print(f"Proof saved to {args.output}")


class BaseVerifierCLI(ABC, Generic[AIR_T]):
    """
    Abstract base class for Verifier CLI applications.

    Subclasses must implement:
        - description: str property for argparse help
        - default_proof_file: str property for default proof filename
        - add_arguments: method to add custom argparse arguments
        - create_air_from_proof: method to create AIR instance from proof data
    """

    @property
    @abstractmethod
    def description(self) -> str:
        """Description for the argparse help message."""
        pass

    @property
    @abstractmethod
    def default_proof_file(self) -> str:
        """Default proof filename to load."""
        pass

    @abstractmethod
    def create_air_from_proof(
        self, args: argparse.Namespace, proof: dict[str, Any]
    ) -> AIR_T:
        """
        Create the AIR instance from proof data and optional CLI overrides.

        Args:
            args: Parsed command line arguments (may contain override values).
            proof: The loaded proof dictionary containing public_inputs.

        Returns:
            A configured AIR instance matching the public inputs.
        """
        pass

    def get_verification_message(
        self, args: argparse.Namespace, proof: dict[str, Any]
    ) -> str:
        """
        Get a custom verification message. Override to customize.

        Args:
            args: Parsed command line arguments.
            proof: The loaded proof dictionary.

        Returns:
            A string message to print before verification.
        """
        return "Verifying proof..."

    def run(self) -> None:
        """Run the verifier CLI application."""
        parser = argparse.ArgumentParser(description=self.description)

        # Add common proof file argument
        parser.add_argument(
            "--proof",
            type=str,
            default=self.default_proof_file,
            help="Path to proof.json",
        )

        # Add custom arguments
        self.add_arguments(parser)

        args = parser.parse_args()

        # Load proof
        proof = load_proof(args.proof)

        # Print verification message
        print(self.get_verification_message(args, proof))

        # Create AIR from proof
        air = self.create_air_from_proof(args, proof)

        # Verify
        verifier = StarkVerifier(air)

        if verifier.verify(proof):
            print("✅ Proof Verified! Computation is valid.")
        else:
            print("❌ Verification Failed! Proof is invalid.")
            sys.exit(1)


def validate_power_of_two(value: int, name: str = "Length") -> None:
    """
    Validate that a value is a power of two.

    Args:
        value: The value to check.
        name: The name of the parameter (for error message).

    Raises:
        SystemExit: If value is not a power of two.
    """
    if value <= 0 or (value & (value - 1)) != 0:
        print(
            f"Error: {name} {value} is not a power of 2. STARK protocol requires power-of-two trace length."
        )
        sys.exit(1)
