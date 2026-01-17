import unittest
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from zk_stark_demo.algebra.smaller_field import SmallField


class TestGeneratorVisual(unittest.TestCase):
    def test_visualize_generator(self):
        print("\n" + "=" * 50)
        print(f"VISUALIZING GENERATOR FOR GF({SmallField.P})")
        print("=" * 50)

        g = SmallField.generator()
        print(f"Using generator g = {g.val}")

        powers = []
        seen = set()

        print("\nCalculating powers g^i:")
        # We check powers from 0 to P-2 (the size of the multiplicative group)
        for i in range(SmallField.P - 1):
            val = g.pow(i).val
            powers.append(val)
            seen.add(val)
            print(f"  {g.val}^{i} \u2261 {val} (mod {SmallField.P})")

        print("\nSummary:")
        print(f"Set of powers: {powers}")
        print(f"Number of unique elements generated: {len(seen)}")
        print(f"Total non-zero elements in field: {SmallField.P - 1}")

        assert (
            len(seen) == SmallField.P - 1
        ), f"The element is not a generator! This element only generates a subgroup of size {len(seen)}"

        print("\nSUCCESS: The element is a generator! It hits every non-zero value.")
        print("=" * 50 + "\n")


if __name__ == "__main__":
    unittest.main()
