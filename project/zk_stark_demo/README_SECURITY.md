# Post-Quantum Security of zk-STARKs

This document explains why the protocol implemented in this demo is considered **Post-Quantum Secure**, unlike many traditional zk-SNARKs.

## The Quantum Threat
Classical public-key cryptography (RSA, Elliptic Curves) relies on the hardness of specific number-theoretic problems:
1.  **Integer Factorization** (RSA)
2.  **Discrete Logarithm Problem** (Elliptic Curves, Diffie-Hellman)

A sufficiently powerful quantum computer running **Shor's Algorithm** can solve these problems efficiently (in polynomial time). This would break most current blockchain cryptography (signatures, key exchanges) and zk-SNARKs (like Groth16) that rely on "Trusted Setups" based on these problems.

## Why STARKs are Different

zk-STARKs (Scalable Transparent Arguments of Knowledge) do **not** rely on Elliptic Curves or factorization. Instead, their security foundation is built on two primitives that are believed to be resistant to quantum attacks:

### 1. Collision-Resistant Hash Functions (CRHF)
The only cryptographic assumption in a STARK is the security of the Hash Function (e.g., SHA-256 or BLAKE3) used in the **Merkle Trees**.
*   **Grover's Algorithm** can speed up finding collisions on a quantum computer, but only quadratically. This means we can maintain security simply by doubling the hash output size (e.g., using 256-bit hashes provides ~128 bits of post-quantum security).

### 2. Information Theoretic Security (Reed-Solomon Codes)
The logic of the proof (FRI, Trace Constraints) relies on **Polynomial Proximity Testing**.
*   We prove that a committed dataset corresponds to a low-degree polynomial.
*   This property is **Information Theoretic**: if the Prover tries to cheat, the probability of them generating a valid proof is strictly bounded by the mathematics of Reed-Solomon codes (Trace Degree vs Blowup Factor).
*   No amount of computational power (quantum or classical) can bypass these probability bounds.

## Comparison: STARK vs SNARK

| Feature | zk-SNARK (Groth16 / KZG) | zk-STARK (This Demo) |
| :--- | :--- | :--- |
| **Cryptography** | Elliptic Curves (Pairings) | Hash Functions + Polynomials |
| **Quantum Safe?** | ❌ No (Shor's Algo) | ✅ Yes (hashes are safe) |
| **Trusted Setup?** | ⚠️ Yes (Toxic Waste) | ✅ No (Transparent) |
| **Proof Size** | Very Small (~200 bytes) | Larger (40KB - 100KB+) |

## In This Demo
Our implementation confirms this:
*   We use **SHA-256** for Merkle Tree commitments.
*   We use **Finite Field Arithmetic** and **FRI** for logic verification.
*   There are no Elliptic Curve operations or "Powers of Tau" setups.

This makes the system transparent and future-proof against quantum adversaries.
