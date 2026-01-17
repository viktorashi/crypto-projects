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
        length = len(data)
        if (length & (length - 1) != 0) or length == 0:
            raise ValueError(f"Trace length must be a power of two. Got {length}.")
        
        self.length: int = length
            
    def get_column(self, col_idx: int) -> List[FieldElement]:
        return [row[col_idx] for row in self.data]
        
    def get_row(self, row_idx: int) -> List[FieldElement]:
        return self.data[row_idx]



    def __repr__(self) -> str:
        return f"Trace(w={self.width}, h={self.length})"
