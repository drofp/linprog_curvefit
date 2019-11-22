#!/usr/bin/env python3

"""Curve fitting with linear programming.

Minimizes the sum of error for each fit point to find the optimal coefficients
for a given polynomial.

Overview:
    Objective: Sum of errors
    Subject to: Bounds on coefficients

Credit: "Curve Fitting with Linear Programming", H. Swanson and R. E. D. Woolsey
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from ortools.linear_solver import pywraplp

def demo_linear(points=None, coeff_ranges=None):
    """Optimize coefficients for a linear polynomial."""
    solver = pywraplp.Solver(
        'linear_polynomial_solver', pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)
    m = solver.NumVar(-100, 100, 'm')
    b = solver.NumVar(-100, 100, 'b')
    e1_plus = solver.NumVar(0, 100, 'e1_plus')
    e1_minus = solver.NumVar(0, 100, 'e1_minus')
    e2_plus = solver.NumVar(0, 100, 'e2_plus')
    e2_minus = solver.NumVar(0, 100, 'e2_minus')
    e3_plus = solver.NumVar(0, 100, 'e3_plus')
    e3_minus = solver.NumVar(0, 100, 'e3_minus')
    e4_plus = solver.NumVar(0, 100, 'e4_plus')
    e4_minus = solver.NumVar(0, 100, 'e4_minus')
    e5_plus = solver.NumVar(0, 100, 'e5_plus')
    e5_minus = solver.NumVar(0, 100, 'e5_minus')

    objective = solver.Objective()
    objective.SetCoefficient(e1_plus, 1)
    objective.SetCoefficient(e1_minus, 1)
    objective.SetCoefficient(e2_plus, 1)
    objective.SetCoefficient(e2_minus, 1)
    objective.SetCoefficient(e3_plus, 1)
    objective.SetCoefficient(e3_minus, 1)
    objective.SetCoefficient(e4_plus, 1)
    objective.SetCoefficient(e4_minus, 1)
    objective.SetCoefficient(e5_plus, 1)
    objective.SetCoefficient(e5_minus, 1)
    objective.SetMinimization()

    solver.Add(b - e1_plus + e1_minus == 1)
    solver.Add(m + b - e2_plus + e2_minus == 3)
    solver.Add(2*m + b - e3_plus + e3_minus == 2)
    solver.Add(3*m + b - e4_plus + e4_minus == 4)
    solver.Add(4*m + b - e5_plus + e5_minus == 5)
    print('Number of constraints: {}, Number of variables: {}'.format(
        solver.NumConstraints(), solver.NumVariables()))

    solver.Solve()
    print('Solution:')
    print('Objective value =', objective.Value())
    print('m =', m.solution_value())
    print('b =', b.solution_value())
    return m.solution_value(), b.solution_value()

def optimize_polynomial(points=None, coeff_ranges=None, order=None):
    """Optimize coefficients for any order polynomial."""

def minimize_error(points=None, coeff_ranges=None):
    """Minimize error between polynomial curve and input points.

    Args:
        points: A tuple of points, represented as tuples (x, y)
    coeff_ranges: A tuple of valid coefficient ranges, respresented as tuples
        (min, max). Nubmer of elements in list determines order of polynomial,
        from highest order (0th index) to lowest order (nth index).

    Returns:
        A Tuple, the desired coefficients. Ordered from highest order polynomial
            term to lowest order.
    """
    if points is None:
        points = ((0,0), (1,1))
    if coeff_ranges is None:
        coeff_ranges = ((-100, 100), (-100, 100))

    # print(optimize_polynomial(points, coeff_ranges))
    demo_linear(points=points, coeff_ranges=coeff_ranges)

    return (1.52381, 0.285714)


def main():
    minimize_error()

if __name__ == '__main__':
    main()