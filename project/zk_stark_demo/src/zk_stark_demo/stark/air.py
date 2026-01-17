
from abc import ABC, abstractmethod
from typing import List
from ..algebra.field import FieldElement

class AIR(ABC):
    """
    Algebraic Intermediate Representation.
    Defines the constraints for a specific computation.
    """
    
    @abstractmethod
    def trace_width(self) -> int:
        pass
        
    @abstractmethod
    def trace_length(self) -> int:
        pass
        
    @abstractmethod
    def get_boundary_constraints(self) -> List:
        """
        Returns list of (step_index, register_index, value) constraints.
        e.g. (0, 0, 1) -> Register 0 at step 0 must be 1.
        """
        pass
        
    @abstractmethod
    def evaluate_transition_constraints(self, current_step: List[FieldElement], next_step: List[FieldElement]) -> List[FieldElement]:
        """
        Returns a list of values that must be zero for a valid transition.
        P(x) constraints.
        """
        pass
