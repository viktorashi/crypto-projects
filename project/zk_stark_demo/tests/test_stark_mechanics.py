
import unittest
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from zk_stark_demo.algebra.field import FieldElement
from zk_stark_demo.stark.trace import Trace
from zk_stark_demo.stark.lde import LowDegreeExtension

class TestStarkMechanics(unittest.TestCase):
    
    def test_trace_length_validation(self):
        # Create a trace with 3 rows, width 1
        data = [[FieldElement(1)], [FieldElement(2)], [FieldElement(3)]]
        
        # Should raise ValueError because 3 is not power of 2
        with self.assertRaises(ValueError):
             Trace(data, 1)
             
        # Power of 2 should work
        data_pow2 = [[FieldElement(1)], [FieldElement(2)], [FieldElement(3)], [FieldElement(0)]]
        trace = Trace(data_pow2, 1)
        self.assertEqual(trace.length, 4)

    def test_lde_interpolation(self):
        """
        Verify that LDE polynomials evaluate to the correct trace values 
        on the original domain D.
        """
        # Trace: 1, 2, 3, 4
        data = [[FieldElement(1)], [FieldElement(2)], [FieldElement(3)], [FieldElement(4)]]
        trace = Trace(data, width=1)
        
        # Blowup factor 4 -> size 16
        lde = LowDegreeExtension(trace, blowup_factor=4)
        
        # Verify LDE length
        self.assertEqual(lde.lde_length, 16)
        
        # Check that P(d_i) == trace[i]
        # Iterate over original domain D
        for i in range(trace.length):
            x = lde.domain_d[i]
            # Evaluate using the polynomial derived
            val = lde.trace_polynomials[0].eval(x)
            self.assertEqual(val, data[i][0])

if __name__ == '__main__':
    unittest.main()
