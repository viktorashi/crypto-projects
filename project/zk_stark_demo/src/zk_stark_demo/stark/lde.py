from __future__ import annotations
from typing import List
from ..algebra.field import FieldElement
from ..algebra.polynomial import Polynomial
from .trace import Trace

class LowDegreeExtension:
    """
    Handles the Low Degree Extension (LDE) of the trace.
    1. Interpolates the trace columns on a domain D (size N).
    2. Evaluates the polynomials on a larger domain D_LDE (size k * N).
    """
    def __init__(self, trace: Trace, blowup_factor: int = 8) -> None:
        self.trace: Trace = trace
        self.blowup_factor: int = blowup_factor
        self.lde_length: int = trace.length * blowup_factor
        
        # 1. Define Domain D (Trace Domain)
        # Generator g such that g^trace_length = 1
        self.g: FieldElement = FieldElement.generator_of_order(self.trace.length)
        self.domain_d: List[FieldElement] = [self.g.pow(i) for i in range(self.trace.length)]
        
        # 2. Define Domain D_LDE (Evaluation Domain)
        # To avoid division by zero issues in constraints (x - x_i), we usually shift D_LDE by an offset.
        self.shift: FieldElement = FieldElement(3) # Just a random generator or number
        self.h: FieldElement = FieldElement.generator_of_order(self.lde_length)
        self.domain_lde: List[FieldElement] = [self.shift * self.h.pow(i) for i in range(self.lde_length)]
    
        # 3. Interpolate Trace Columns to get Polynomials P_0(x), P_1(x)...
        self.trace_polynomials: List[Polynomial] = []
        self.compute_trace_polynomials()
        
        # 4. Evaluate on D_LDE
        self.lde_evaluations: List[List[FieldElement]] = [] # List of columns
        self.compute_lde_evaluations()

    def compute_trace_polynomials(self) -> None:
        self.trace_polynomials = []
        for col_idx in range(self.trace.width):
            col_values = self.trace.get_column(col_idx)
            # Interpolate: P(domain_d[i]) = col_values[i]
            # O(N^2) Lagrange
            poly = Polynomial.lagrange_interpolate(self.domain_d, col_values)
            self.trace_polynomials.append(poly)
            
    def compute_lde_evaluations(self) -> None:
        self.lde_evaluations = []
        for poly in self.trace_polynomials:
            # Evaluate poly on every point in domain_lde
            # O(N * k*N) = O(k N^2) basic evaluation
            evals = [poly.eval(x) for x in self.domain_lde]
            self.lde_evaluations.append(evals)

    def get_evaluation(self, step_idx: int) -> List[FieldElement]:
        """Returns the row at step_idx in the LDE domain"""
        return [col[step_idx] for col in self.lde_evaluations]
