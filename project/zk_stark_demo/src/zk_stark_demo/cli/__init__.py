"""
CLI module for zk-STARK provers and verifiers.

Provides base classes for building CLI applications:
- BaseProverCLI: Template for prover CLI applications
- BaseVerifierCLI: Template for verifier CLI applications
- validate_power_of_two: Utility for validating power-of-2 constraints
"""

from zk_stark_demo.cli.base import (
    BaseProverCLI,
    BaseVerifierCLI,
    validate_power_of_two,
)

__all__ = [
    "BaseProverCLI",
    "BaseVerifierCLI",
    "validate_power_of_two",
]
