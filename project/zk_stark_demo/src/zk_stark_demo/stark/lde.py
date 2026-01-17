
from ..algebra.field import FieldElement
from ..algebra.polynomial import Polynomial
from .trace import Trace

class LowDegreeExtension:
    """
    Handles the Low Degree Extension (LDE) of the trace.
    1. Interpolates the trace columns on a domain D (size N).
    2. Evaluates the polynomials on a larger domain D_LDE (size k * N).
    """
    def __init__(self, trace: Trace, blowup_factor=8):
        self.trace = trace
        self.blowup_factor = blowup_factor
        self.trace_length = trace.length
        self.lde_length = trace.length * blowup_factor
        
        # 1. Define Domain D (Trace Domain)
        # Generator g such that g^trace_length = 1
        self.g = FieldElement.generator_of_order(self.trace_length)
        self.domain_d = [self.g.pow(i) for i in range(self.trace_length)]
        
        # 2. Define Domain D_LDE (Evaluation Domain)
        # We need a generator for size k*N
        # We ideally want D to be a subgroup of D_LDE, or use a coset.
        # Simplest: use a generator of order k*N.
        # But for FRI/Security, we typically use a coset to avoid D.
        # For this simple demo, we will check if D is subset of D_LDE.
        # Actually, if we use generator w of order k*N, then w^k generates order N.
        # So D is a subset of D_LDE.
        # To avoid division by zero issues in constraints (x - x_i), we usually shift D_LDE by an offset.
        # Let's use a simple shift: offset * w^i
        self.shift = FieldElement(3) # Just a random generator or number
        self.h = FieldElement.generator_of_order(self.lde_length)
        self.domain_lde = [self.shift * self.h.pow(i) for i in range(self.lde_length)]
    
        # 3. Interpolate Trace Columns to get Polynomials P_0(x), P_1(x)...
        self.trace_polynomials = []
        self.compute_trace_polynomials()
        
        # 4. Evaluate on D_LDE
        self.lde_evaluations = [] # List of columns (lists of field elements)
        self.compute_lde_evaluations()

    def compute_trace_polynomials(self):
        self.trace_polynomials = []
        for col_idx in range(self.trace.width):
            col_values = self.trace.get_column(col_idx)
            # Interpolate: P(domain_d[i]) = col_values[i]
            # O(N^2) Lagrange
            poly = Polynomial.lagrange_interpolate(self.domain_d, col_values)
            self.trace_polynomials.append(poly)
            
    def compute_lde_evaluations(self):
        self.lde_evaluations = []
        for poly in self.trace_polynomials:
            # Evaluate poly on every point in domain_lde
            # O(N * k*N) = O(k N^2) basic evaluation
            evals = [poly.eval(x) for x in self.domain_lde]
            self.lde_evaluations.append(evals)

    def get_evaluation(self, step_idx):
        """Returns the row at step_idx in the LDE domain"""
        return [col[step_idx] for col in self.lde_evaluations]
