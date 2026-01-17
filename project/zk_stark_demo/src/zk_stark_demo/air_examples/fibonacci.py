from __future__ import annotations
from typing import List, Tuple
from ..algebra.field import FieldElement
from ..stark.air import AIR

class FibonacciAIR(AIR):
    def __init__(self, trace_length: int, result_value: FieldElement) -> None:
        self.length: int = trace_length
        self.result: FieldElement = result_value # Public input: the expected result at the end
        
    def trace_width(self) -> int:
        return 2

    def get_public_inputs(self) -> Dict[str, Any]:
        return {
            'length': self.length,
            'result': self.result
        }


    def generate_trace(self, start_values: List[int]) -> List[List[FieldElement]]:
        """
        Generates the trace for the Fibonacci sequence.
        start_values: [a, b]
        """
        assert len(start_values) == 2
        trace: List[List[FieldElement]] = []
        state: List[FieldElement] = [FieldElement(start_values[0]), FieldElement(start_values[1])]
        trace.append(state)
        
        for _ in range(self.length - 1):
            next_state: List[FieldElement] = [
                state[1],
                state[0] + state[1]
            ]
            trace.append(next_state)
            state = next_state
            
        return trace
        
    def trace_length(self) -> int:
        return self.length

    def get_boundary_constraints(self) -> List[Tuple[int, int, FieldElement]]:
        # Step 0: [1, 1] (Fib start)
        # Step last: [?, result]
        return [
            (0, 0, FieldElement(1)),
            (0, 1, FieldElement(1)),
            (self.length - 1, 1, self.result)
        ]

    def evaluate_transition_constraints(
        self, 
        current_step: List[FieldElement], 
        next_step: List[FieldElement]
    ) -> List[FieldElement]:
        # R0_cur, R1_cur = current_step
        # R0_next, R1_next = next_step
        
        # 1. R0_next = R1_cur
        c1 = next_step[0] - current_step[1]
        
        # 2. R1_next = R0_cur + R1_cur
        c2 = next_step[1] - (current_step[0] + current_step[1])
        
        return [c1, c2]
