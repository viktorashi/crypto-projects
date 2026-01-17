
# zk-STARK Demo

A from-scratch, educational implementation of a zero-knowledge STARK protocol in Python.

## Overview

This project implements the core components of a STARK proving system:
*   **Finite Field Arithmetic**: Operations over GF(P).
*   **Polynomials**: Evaluation, Interpolation.
*   **Merkle Trees**: Commitments using SHA-256.
*   **FRI Protocol**: Fast Reed-Solomon Interactive Oracle Proof of Proximity.
*   **AIR (Algebraic Intermediate Representation)**: Agnostic interface for computations.
*   **Fiat-Shamir**: Non-interactive proofs via cryptographic channel.

It includes a working example for proving the **Fibonacci Sequence**.

## Post-Quantum Security
See [README_SECURITY.md](README_SECURITY.md) for an explanation of why this protocol is resistant to quantum computer attacks (unlike Elliptic Curve SNARKs).

## Installation

This project uses `uv` for dependency management.

```bash
uv sync
```

## Running Tests

Verify the mathematical core and protocol logic:

```bash
uv run pytest
```

## Usage (CLI)

The project includes CLI tools to generating and verifying proofs.

### 1. Generate a Proof
Prove you know the computation trace for a Fibonacci sequence of length 8 (Result: 34).

```bash
uv run src/zk_stark_demo/cli/prover_cli.py --length 8 --output proof.json
```
This generates `proof.json`.

### 2. Verify a Proof
Verify the proof against the public inputs (Length=8, Result=34).

```bash
uv run src/zk_stark_demo/cli/verifier_cli.py --proof proof.json --length 8 --result 34
```

If valid, it will output: `✅ Proof Verified! Computation is valid.`

## Architecture

- `src/zk_stark_demo/algebra`: Math primitives (Field, Poly, Merkle).
- `src/zk_stark_demo/stark`: Protocol mechanics (Trace, LDE, FRI, Prover/Verifier).
- `src/zk_stark_demo/examples`: Concrete AIR implementations (Fibonacci, Cubic).
