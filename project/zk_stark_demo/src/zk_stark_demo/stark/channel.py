
import hashlib
from ..algebra.field import FieldElement

class Channel:
    """
    Implements the Fiat-Shamir heuristic.
    A non-interactive channel that generates random challenges based on the transcript.
    """
    def __init__(self):
        self.state = b''

    def send(self, data: bytes):
        """
        Prover sends data to the channel.
        State is updated: state = hash(state || data)
        """
        self.state = hashlib.sha256(self.state + data).digest()

    def receive_random_field_element(self) -> FieldElement:
        """
        Verifier (simulated) sends a random field element.
        In non-interactive, this is derived from the current state.
        """
        # We need a number in [0, P-1]
        # Just take the first 8 bytes (64 bits) and mod P
        # For security, we should re-hash the state to avoid repeating.
        # Here we just use the current state hash.
        # To separate "randomness generation" from "state update", usually we hash with a counter or prefix.
        
        # Simple implementation: hash state again to get randomness, but don't change state?
        # A standard construction:
        # random_bytes = hash(state || "random")
        # state = hash(state || "random") # Maybe?
        
        # Let's do:
        # randomness = hash(state)
        # state = randomness (chaining)
        randomness = hashlib.sha256(self.state).digest()
        self.state = randomness # chaining
        
        val = int.from_bytes(randomness[:8], 'big')
        return FieldElement(val)

    def receive_random_int(self, min_val, max_val) -> int:
        """
        Returns random integer in [min_val, max_val).
        """
        rand_fe = self.receive_random_field_element()
        # Uniformity might be slightly biased but fine for demo
        range_size = max_val - min_val
        return min_val + (rand_fe.val % range_size)
