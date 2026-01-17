
from typing import List
from ..algebra.field import FieldElement

class Trace:
    """
    Represents the execution trace of the computation.
    A table where rows are steps and columns are registers.
    """
    def __init__(self, data: List[List[FieldElement]], width: int):
        self.width = width
        self.data = data # list of rows
        
        # Ensure length is power of 2
        self.length = self.next_power_of_two(len(data))
        
        # Pad with zeros (or last state? usually cyclic or don't care)
        # For simplicity, pad with zeros, but secure protocols might need care here.
        while len(self.data) < self.length:
            self.data.append([FieldElement(0)] * width)
            
    def get_column(self, col_idx):
        return [row[col_idx] for row in self.data]
        
    def get_row(self, row_idx):
        return self.data[row_idx]

    @staticmethod
    def next_power_of_two(n):
        if n == 0: return 1
        return 1 << (n - 1).bit_length()

    def __repr__(self):
        return f"Trace(w={self.width}, h={self.length})"
