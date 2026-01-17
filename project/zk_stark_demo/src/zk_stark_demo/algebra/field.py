
import random

class FieldElement:
    """
    Represents an element effectively in a Finite Field GF(P).
    We use a small prime for this demo to keep debugging easy, 
    but large enough to generally work for small examples.
    
    Using P = 3 * 2^30 + 1 (a STARK-friendly prime) would be ideal for efficiency,
    but for this pure Python demo, we can just use a generic large prime or strictly enforce
    modulus operations.
    
    Let's use a prime that is 1 mod 2^k to allow for FFTs later if we get there.
    P = 3221225473 (3 * 2^30 + 1) is standard for some stark implementations.
    """
    # P = 3 * 2^30 + 1
    P = 3221225473 
    
    def __init__(self, val):
        if isinstance(val, FieldElement):
            self.val = val.val
        else:
            self.val = val % self.P

    def add(self, other):
        return FieldElement(self.val + other.val)

    def sub(self, other):
        return FieldElement(self.val - other.val)

    def mul(self, other):
        return FieldElement(self.val * other.val)

    def inv(self):
        # Fermat's Little Theorem: a^(P-2) = a^-1 (mod P)
        return self.pow(self.P - 2)

    def div(self, other):
        return self.mul(other.inv())

    def pow(self, exponent):
        return FieldElement(pow(self.val, exponent, self.P))
    
    def __add__(self, other):
        if isinstance(other, int): other = FieldElement(other)
        return self.add(other)
    
    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        if isinstance(other, int): other = FieldElement(other)
        return self.sub(other)
    
    def __rsub__(self, other):
        if isinstance(other, int): other = FieldElement(other)
        return other.sub(self)

    def __mul__(self, other):
        if isinstance(other, int): other = FieldElement(other)
        return self.mul(other)
    
    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        if isinstance(other, int): other = FieldElement(other)
        return self.div(other)
    
    def __rtruediv__(self, other):
        if isinstance(other, int): other = FieldElement(other)
        return other.div(self)

    def __neg__(self):
        return FieldElement(-self.val)

    def __eq__(self, other):
        if isinstance(other, int): other = FieldElement(other)
        return self.val == other.val

    def __repr__(self):
        return f"FieldElement({self.val})"
        
    def __str__(self):
        return str(self.val)

    @classmethod
    def zero(cls):
        return cls(0)

    @classmethod
    def one(cls):
        return cls(1)
        
    @classmethod
    def generator(cls):
        # Find a generator for the multiplicative group? 
        # For P = 3221225473, 5 is a generator.
        return cls(5)

    @classmethod
    def generator_of_order(cls, order):
        """
        Returns an element g such that g^order = 1 and g^(order/2) != 1.
        Assuming P-1 is divisible by order.
        """
        assert (cls.P - 1) % order == 0, f"Field does not have a subgroup of order {order}"
        g = cls.generator()
        # g is a generator of the whole group (size P-1)
        # We want g_target such that (g_target)^order = 1
        # g^(P-1) = 1
        # Let g_target = g ^ ((P-1) / order)
        return g.pow((cls.P - 1) // order)

