from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Tuple
from ..algebra.field import FieldElement

class AIR(ABC):
    """
    Algebraic Intermediate Representation.
    Defines the constraints for a specific computation.
    """
    
    @abstractmethod
    def trace_width(self) -> int:
        pass
        
    def constraint_degree(self) -> int:
        """
        Returns the algebraic degree of the transition constraints.
        Default is 1 (Linear).
        If constraints involve multiplication of trace variables (e.g. x^2), return 2, etc.
        """
        return 1

        
    @abstractmethod
    def trace_length(self) -> int:
        pass
        
    @abstractmethod
    def get_boundary_constraints(self) -> List[Tuple[int, int, FieldElement]]:
        """
        Returns list of (step_index, register_index, value) constraints.
        e.g. (0, 0, 1) -> Register 0 at step 0 must be 1.
        """
        pass
        
    @abstractmethod
    def evaluate_transition_constraints(
        self, 
        current_step: List[FieldElement], 
        next_step: List[FieldElement]
    ) -> List[FieldElement]:
        """
        Returns a list of values that must be zero for a valid transition.
        P(x) constraints.
        """
        pass

    def get_public_inputs(self) -> Dict[str, Any]:
        """
        Returns a dictionary of public inputs defining the computation instance.
        e.g. {'trace_length': 8, 'result': FieldElement(34)}
        """
        return {}

