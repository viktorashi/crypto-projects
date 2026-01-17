from __future__ import annotations
from typing import List, Tuple
from ..algebra.field import FieldElement
from ..stark.air import AIR


class CubicAIR(AIR):
    """
    Proves computation of a repeated cubic function:
    x_{mnext} = x_{curr}^3 + x_{curr} + 5

    This computation is 'harder' because:
    1. Cubic growth is much faster than Fibonacci.
    2. The constraint degree is 3, which requires the prover to interpolate
       the composition polynomial on a larger subset of the LDE domain
       (degree ~ 2N instead of N).
    """

    def __init__(
        self, trace_length: int, result_value: FieldElement, start_value: int = 1
    ) -> None:
        self.length: int = trace_length
        self.result: FieldElement = result_value
        self.start_value: int = start_value

    def trace_width(self) -> int:
        return 1

    def get_public_inputs(self) -> Dict[str, Any]:
        return {
            "length": self.length,
            "result": self.result,
            "start_value": self.start_value,
        }

    def constraint_degree(self) -> int:
        return 3  # Cubic constraints

    def generate_trace(self) -> List[List[FieldElement]]:
        trace: List[List[FieldElement]] = []
        current = FieldElement(self.start_value)
        trace.append([current])

        for _ in range(self.length - 1):
            # x_{next} = x^3 + x + 5
            # We break this down:
            x_cubed = current.pow(3)
            val = x_cubed + current + FieldElement(5)

            trace.append([val])
            current = val

        return trace

    def trace_length(self) -> int:
        return self.length

    def get_boundary_constraints(self) -> List[Tuple[int, int, FieldElement]]:
        return [
            (0, 0, FieldElement(self.start_value)),
            (self.length - 1, 0, self.result),
        ]

    def evaluate_transition_constraints(
        self, current_step: List[FieldElement], next_step: List[FieldElement]
    ) -> List[FieldElement]:
        # Constraint: x_next - (x_curr^3 + x_curr + 5) = 0

        x_curr = current_step[0]
        x_next = next_step[0]

        computed_next = x_curr.pow(3) + x_curr + FieldElement(5)
        constraint = x_next - computed_next

        return [constraint]
