
from .field import FieldElement

class Polynomial:
    def __init__(self, coefficients):
        """
        coefficients: list of FieldElement, ordered from x^0 to x^n.
        P(x) = coeffs[0] + coeffs[1]*x + ...
        """
        self.coefficients = [c if isinstance(c, FieldElement) else FieldElement(c) for c in coefficients]
        # Remove trailing zeros (leading high-degree coefficients that are 0)
        while len(self.coefficients) > 0 and self.coefficients[-1] == FieldElement(0):
            self.coefficients.pop()
        if not self.coefficients:
            self.coefficients = [FieldElement(0)]

    def degree(self):
        return len(self.coefficients) - 1

    def eval(self, x):
        """
        Evaluate P(x) using Horner's method.
        """
        if isinstance(x, int):
            x = FieldElement(x)
            
        result = FieldElement(0)
        # Iterate backwards: ((a_n * x + a_{n-1}) * x + ...)
        for coef in reversed(self.coefficients):
            result = result * x + coef
        return result

    def __add__(self, other):
        max_len = max(len(self.coefficients), len(other.coefficients))
        new_coeffs = [FieldElement(0)] * max_len
        for i in range(max_len):
            c1 = self.coefficients[i] if i < len(self.coefficients) else FieldElement(0)
            c2 = other.coefficients[i] if i < len(other.coefficients) else FieldElement(0)
            new_coeffs[i] = c1 + c2
        return Polynomial(new_coeffs)

    def __sub__(self, other):
        max_len = max(len(self.coefficients), len(other.coefficients))
        new_coeffs = [FieldElement(0)] * max_len
        for i in range(max_len):
            c1 = self.coefficients[i] if i < len(self.coefficients) else FieldElement(0)
            c2 = other.coefficients[i] if i < len(other.coefficients) else FieldElement(0)
            new_coeffs[i] = c1 - c2
        return Polynomial(new_coeffs)

    def __mul__(self, other):
        if isinstance(other, FieldElement) or isinstance(other, int):
            return Polynomial([c * other for c in self.coefficients])
            
        # Basic O(N^2) multiplication
        deg1 = self.degree()
        deg2 = other.degree()
        new_coeffs = [FieldElement(0)] * (deg1 + deg2 + 1)
        for i in range(deg1 + 1):
            for j in range(deg2 + 1):
                new_coeffs[i+j] += self.coefficients[i] * other.coefficients[j]
        return Polynomial(new_coeffs)

    def __repr__(self):
        return f"Poly({self.coefficients})"

    @staticmethod
    def lagrange_interpolate(x_values, y_values):
        """
        Returns a Polynomial P such that P(x_i) = y_i for all i.
        Uses the standard Lagrange formula:
        L(x) = sum( y_i * l_i(x) )
        where l_i(x) = prod( (x - x_j) / (x_i - x_j) ) for j != i
        """
        assert len(x_values) == len(y_values)
        total_poly = Polynomial([FieldElement(0)])
        
        for i, (xi, yi) in enumerate(zip(x_values, y_values)):
            # Build l_i(x)
            numerator = Polynomial([FieldElement(1)])
            denominator = FieldElement(1)
            
            for j, xj in enumerate(x_values):
                if i == j:
                    continue
                # (x - xj)
                term = Polynomial([ -xj, FieldElement(1) ]) 
                numerator = numerator * term
                denominator = denominator * (xi - xj)
                
            # term_poly = yi * (numerator / denominator)
            basis_poly = numerator * (yi / denominator)
            total_poly = total_poly + basis_poly
            
        return total_poly
