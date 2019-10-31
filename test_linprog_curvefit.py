import unittest

class TestLinprogCurvefit(unittest.TestCase):
    def setUp(self):
        linprog_curvefit = __import__('linprog_curvefit')
        self.minimize_error = linprog_curvefit.minimize_error

    def test_minimize_error_LinearCurve(self):
        """https://www.wolframalpha.com/input/?i=linear+fit+%280%2C0%29%2C+%281.5%2C+3%29%2C+%284.5%2C+7%29"""
        points = ((0,0), (1.5, 3), (4.5, 7))
        coeff_ranges = ((-10, 10), (-10, 10))
        desired_coeff = (1.52381, 0.285714)
        self.assertEqual(
            self.minimize_error(points=points, coeff_ranges=coeff_ranges),
            desired_coeff)