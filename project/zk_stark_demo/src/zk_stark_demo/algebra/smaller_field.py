from __future__ import annotations
from typing import Union, Type

class SmallField:
    """
    Veryy small field, for representative purposes
    """

    P: int = 7

    def __init__(self, val: Union[int, SmallField]) -> None:
        if isinstance(val, SmallField):
            self.val: int = val.val
        else:
            self.val: int = val % self.P

    def add(self, other: SmallField) -> SmallField:
        return SmallField(self.val + other.val)

    def sub(self, other: SmallField) -> SmallField:
        return SmallField(self.val - other.val)

    def mul(self, other: SmallField) -> SmallField:
        return SmallField(self.val * other.val)

    def inv(self) -> SmallField:
        # Fermat's Little Theorem: a^(P-2) = a^-1 (mod P)
        return self.pow(self.P - 2)

    def div(self, other: SmallField) -> SmallField:
        return self.mul(other.inv())

    def pow(self, exponent: int) -> SmallField:
        return SmallField(pow(self.val, exponent, self.P))

    def __add__(self, other: Union[int, SmallField]) -> SmallField:
        if isinstance(other, int):
            other = SmallField(other)
        return self.add(other)

    def __radd__(self, other: Union[int, SmallField]) -> SmallField:
        return self + other

    def __sub__(self, other: Union[int, SmallField]) -> SmallField:
        if isinstance(other, int):
            other = SmallField(other)
        return self.sub(other)

    def __rsub__(self, other: Union[int, SmallField]) -> SmallField:
        if isinstance(other, int):
            other = SmallField(other)
        return other.sub(self)

    def __mul__(self, other: Union[int, SmallField]) -> SmallField:
        if isinstance(other, int):
            other = SmallField(other)
        return self.mul(other)

    def __rmul__(self, other: Union[int, SmallField]) -> SmallField:
        return self * other

    def __truediv__(self, other: Union[int, SmallField]) -> SmallField:
        if isinstance(other, int):
            other = SmallField(other)
        return self.div(other)

    def __rtruediv__(self, other: Union[int, SmallField]) -> SmallField:
        if isinstance(other, int):
            other = SmallField(other)
        return other.div(self)

    def __neg__(self) -> SmallField:
        return SmallField(-self.val)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, int):
            other = SmallField(other)
        if not isinstance(other, SmallField):
            return False
        return self.val == other.val

    def __repr__(self) -> str:
        return f"FieldElement({self.val})"

    def __str__(self) -> str:
        return str(self.val)

    @classmethod
    def zero(cls: Type[SmallField]) -> SmallField:
        return cls(0)

    @classmethod
    def one(cls: Type[SmallField]) -> SmallField:
        return cls(1)

    @classmethod
    def generator(cls: Type[SmallField]) -> SmallField:
        # Find a generator for the multiplicative group?
        # For P = 7, 3 is a generator. (2 only generates {1, 2, 4})
        return cls(3)

    @classmethod
    def generator_of_order(cls: Type[SmallField], order: int) -> SmallField:
        """
        Returns an element g such that g^order = 1 and g^(order/2) != 1.
        Assuming P-1 is divisible by order.
        """
        assert (
            cls.P - 1
        ) % order == 0, f"Field does not have a subgroup of order {order}"
        g = cls.generator()
        # g is a generator of the whole group (size P-1)
        # We want g_target such that (g_target)^order = 1
        # g^(P-1) = 1
        # Let g_target = g ^ ((P-1) / order)
        return g.pow((cls.P - 1) // order)
