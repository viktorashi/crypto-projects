from __future__ import annotations
from typing import List
from ..algebra.field import FieldElement

class Trace:
    """
    Represents the execution trace of the computation.
    A table where rows are steps and columns are registers.
    """
    def __init__(self, data: List[List[FieldElement]], width: int) -> None:
        self.width: int = width
        self.data: List[List[FieldElement]] = data # list of rows
        
        # Ensure length is power of 2
        self.length: int = self.next_power_of_two(len(data))
        
        # Pad with zeros
        while len(self.data) < self.length:
            self.data.append([FieldElement(0)] * width)
            
    def get_column(self, col_idx: int) -> List[FieldElement]:
        return [row[col_idx] for row in self.data]
        
    def get_row(self, row_idx: int) -> List[FieldElement]:
        return self.data[row_idx]

    @staticmethod
    def next_power_of_two(n: int) -> int:
        if n == 0: return 1
        return 1 << (n - 1).bit_length()

    def __repr__(self) -> str:
        return f"Trace(w={self.width}, h={self.length})"
