import unittest

from ortools.linear_solver import pywraplp

class TestLinprogCurvefit(unittest.TestCase):
    def setUp(self):
        linprog_curvefit = __import__('linprog_curvefit')
        self.minimize_error = linprog_curvefit.minimize_error
        self.generate_variables = linprog_curvefit._generate_variables

    def test_generate_variables_2PointsLinearCorrectVarCnt(self):
        points = ((0, 0), (1.5, 3))
        coeff_ranges = ((-10, 10), (-10, 10))
        solver = pywraplp.Solver(
            'polynomial_solver', pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)
        expected_num_of_vars = 6
        variables = self.generate_variables(
                solver, points=points, coeff_ranges=coeff_ranges, max_err=100)
        self.assertEqual(len(variables), expected_num_of_vars)
