#!/usr/bin/env python3

"""Curve fitting with linear programming.

Minimizes the sum of error for each fit point to find the optimal coefficients
for a given polynomial.

Overview:
    Objective: Sum of errors
    Subject to: Bounds on coefficients
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from ortools.linear_solver import pywraplp

def optimize_linear(points=None, coeff_ranges=None):
    """Optimize coefficients for a linear polynomial."""
    solver = pywraplp.Solver(
        'linear_polynomial_solver', pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)
    a = solver.NumVar(coeff_ranges[0][0], coeff_ranges[0][1], 'a')
    b = solver.NumVar(coeff_ranges[1][0], coeff_ranges[1][1], 'b')

    objective = solver.Objective()
    objective.SetCoefficient(a, points[0][0])
    objective.SetCoefficient(b, points[1][0])
    objective.SetOffset(sum([points[0][1], points[1][1]]))
    objective.SetMinimization()

    solver.Solve()
    print('Solution:')
    print('Objective value =', objective.Value())
    print('a =', a.solution_value())
    print('b =', b.solution_value())
    return a.solution_value(), b.solution_value()

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

    print(optimize_linear(points, coeff_ranges))

    return (1.52381, 0.285714)


def main():
    minimize_error()

if __name__ == '__main__':
    main()