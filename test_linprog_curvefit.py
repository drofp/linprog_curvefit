import unittest

class TestLinprogCurvefit(unittest.TestCase):
    def setUp(self):
        linprog_curvefit = __import__('linprog_curvefit')
        self.minimize_error = linprog_curvefit.minimize_error

    def test_minimize_error_LinearCurve(self):
        self.assertEqual(self.minimize_error(), 'foo')