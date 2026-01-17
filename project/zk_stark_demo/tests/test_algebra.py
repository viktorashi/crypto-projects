
import unittest
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from zk_stark_demo.algebra.field import FieldElement
from zk_stark_demo.algebra.polynomial import Polynomial

class TestMath(unittest.TestCase):
    def test_field_arithmetic(self):
        a = FieldElement(10)
        b = FieldElement(20)
        c = a + b
        self.assertEqual(c.val, 30)
        
        d = a - b
        # 10 - 20 = -10 = P - 10
        self.assertEqual(d.val, FieldElement.P - 10)
        
        e = a * b
        self.assertEqual(e.val, 200)

    def test_field_inverse(self):
        a = FieldElement(12345)
        inv_a = a.inv()
        res = a * inv_a
        self.assertEqual(res, FieldElement(1))

    def test_polynomial_eval(self):
        # P(x) = 2x^2 + 3x + 5
        poly = Polynomial([5, 3, 2])
        # P(10) = 200 + 30 + 5 = 235
        val = poly.eval(10)
        self.assertEqual(val, FieldElement(235))

    def test_lagrange_interpolation(self):
        # Points: (1, 3), (2, 7), (3, 13)
        # Expected: P(x) = x^2 + x + 1
        # Check: 1+1+1=3, 4+2+1=7, 9+3+1=13
        xs = [FieldElement(1), FieldElement(2), FieldElement(3)]
        ys = [FieldElement(3), FieldElement(7), FieldElement(13)]
        
        poly = Polynomial.lagrange_interpolate(xs, ys)
        
        # Verify it interpolates correctly
        self.assertEqual(poly.eval(1), FieldElement(3))
        self.assertEqual(poly.eval(2), FieldElement(7))
        self.assertEqual(poly.eval(3), FieldElement(13))
        
        # Verify coefficients: x^2 + x + 1 -> [1, 1, 1]
        self.assertEqual(poly.coefficients[0], FieldElement(1))
        self.assertEqual(poly.coefficients[1], FieldElement(1))
        self.assertEqual(poly.coefficients[2], FieldElement(1))

if __name__ == '__main__':
    unittest.main()
