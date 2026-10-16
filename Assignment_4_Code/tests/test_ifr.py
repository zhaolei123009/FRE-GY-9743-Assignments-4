import unittest
from types import SimpleNamespace

import numpy as np

from fixedincomelib.utilities.numerics import Interpolator1DPCP, ExtrapMethod
from fixedincomelib.yield_curve.yield_curve_model import YieldCurve


class InterpolatorTests(unittest.TestCase):
    def setUp(self):
        self.curve = Interpolator1DPCP(np.array([1., 3., 5., 7.]),
                                      np.array([3., 4., 5., 6.]), ExtrapMethod.FLAT)

    def test_left_continuity_and_flat_extrapolation(self):
        for x, expected in [(-2, 3), (.5, 3), (1, 3), (1.5, 4),
                            (3, 4), (5, 5), (5.5, 6), (7, 6), (8, 6)]:
            with self.subTest(x=x):
                self.assertEqual(self.curve.interpolate(x), expected)
        np.testing.assert_array_equal(self.curve.gradient_wrt_ordinate(3), [0, 1, 0, 0])

    def test_integral_and_analytic_weights(self):
        # Areas: 1*3 + 2*4 + 2*5 + 3*6 = 39.
        self.assertEqual(self.curve.integrate(0, 8), 39)
        np.testing.assert_array_equal(
            self.curve.gradient_of_integrated_value_wrt_ordinate(0, 8), [1, 2, 2, 3])
        self.assertEqual(self.curve.integrate(8, 0), -39)
        self.assertEqual(self.curve.integrate(3, 3), 0)
        self.assertEqual(self.curve.integrate(-2, 0), 6)
        self.assertEqual(self.curve.integrate(1.5, 4), 11)

    def test_single_node(self):
        curve = Interpolator1DPCP(np.array([1.]), np.array([.02]), ExtrapMethod.FLAT)
        self.assertAlmostEqual(curve.integrate(0, 15), .3)
        np.testing.assert_array_equal(curve.gradient_of_integrated_value_wrt_ordinate(0, 15), [15])

    def test_gradient_against_independent_bumps(self):
        weights = self.curve.gradient_of_integrated_value_wrt_ordinate(-1, 8)
        for i in range(4):
            up = self.curve.values.copy()
            down = self.curve.values.copy()
            up[i] += 1e-5
            down[i] -= 1e-5
            plus = Interpolator1DPCP(self.curve.axis1, up, ExtrapMethod.FLAT)
            minus = Interpolator1DPCP(self.curve.axis1, down, ExtrapMethod.FLAT)
            numerical = (plus.integrate(-1, 8) - minus.integrate(-1, 8)) / 2e-5
            self.assertAlmostEqual(numerical, weights[i], places=8)


class ReferenceTests(unittest.TestCase):
    def model(self, references):
        components = {}
        for name, reference, factor in references:
            index = SimpleNamespace(name=lambda name=name: name, reference_index=reference)
            components[name] = SimpleNamespace(component_identifier=index,
                discount_factor=lambda date, factor=factor: factor)
        return SimpleNamespace(retrieve_model_component=lambda index: components[index])

    def test_reference_chain(self):
        model = self.model([('base', None, .9), ('spread', 'base', .8), ('extra', 'spread', .7)])
        self.assertAlmostEqual(YieldCurve.discount_factor(model, 'extra', None), .9*.8*.7)

    def test_reference_cycle(self):
        model = self.model([('a', 'b', 1), ('b', 'a', 1)])
        with self.assertRaisesRegex(ValueError, 'Circular'):
            YieldCurve.discount_factor(model, 'a', None)


if __name__ == '__main__':
    unittest.main()
