from __future__ import annotations
import hashlib
from typing import List, Any, Iterable

class MerkleTree:
    """
    A simple Merkle Tree implementation using SHA256.
    """
    
    def __init__(self, data: List[bytes]) -> None:
        """
        data: list of bytes to commit to.
        """
        self.leaves: List[bytes] = data
        self.tree: List[List[bytes]] = []
        self._build_tree()

    def _hash(self, data: bytes) -> bytes:
        return hashlib.sha256(data).digest()

    def _build_tree(self) -> None:
        """
        Layer 0 are the leaves
        """
        current_layer: List[bytes] = [self._hash(d) for d in self.leaves]
        self.tree = [current_layer]
        
        while len(current_layer) > 1:
            next_layer: List[bytes] = []
            for i in range(0, len(current_layer), 2):
                left = current_layer[i]
                # If odd number of nodes, duplicate the last one
                right = current_layer[i+1] if i+1 < len(current_layer) else left
                combined = self._hash(left + right)
                next_layer.append(combined)
            self.tree.append(next_layer)
            current_layer = next_layer

    @property
    def root(self) -> bytes:
        if not self.tree:
            return b''
        return self.tree[-1][0]

    def get_authentication_path(self, index: int) -> List[bytes]:
        """
        Returns the authentication path for the leaf at `index`.
        The path is a list of sibling hashes needed to reconstruct the root.
        """
        path: List[bytes] = []
        for layer in self.tree[:-1]: # Don't need root's sibling (it has none)
            is_right_child = (index % 2 == 1)
            sibling_index = index - 1 if is_right_child else index + 1
            
            # Handle case where last node duplicates itself
            if sibling_index >= len(layer):
                sibling_index = index
                
            path.append(layer[sibling_index])
            index //= 2
            
        return path

    @staticmethod
    def verify_claim(root: bytes, leaf_data: bytes, path: List[bytes], index: int) -> bool:
        """
        Verifies that `leaf_data` is at `index` in the tree with `root`.
        """
        current_hash = hashlib.sha256(leaf_data).digest()
        
        for sibling in path:
            is_right_child = (index % 2 == 1)
            if is_right_child:
                # current is right, sibling is left
                current_hash = hashlib.sha256(sibling + current_hash).digest()
            else:
                # current is left, sibling is right
                current_hash = hashlib.sha256(current_hash + sibling).digest()
            index //= 2
            
        return current_hash == root

    @staticmethod
    def commit(data_elements: Iterable[Any]) -> MerkleTree:
        """
        Helper to quickly get a root from data.
        """
        # data_elements can be field elements, strings, etc.
        # we need to serialize them to bytes first.
        bytes_data = [str(d).encode() for d in data_elements]
        return MerkleTree(bytes_data)
