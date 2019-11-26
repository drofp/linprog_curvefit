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

import enum
import string

from ortools.linear_solver import pywraplp

class ErrorDefinition(enum.Enum):
    SUM_ABS_DEV = enum.auto()
    SUM_MAX_DEVIATION = enum.auto()


def _generate_variables(solver, points, coeff_ranges, err_max, error_def):
    """Create coefficient variables.

    Initial version works for up to 26 variable polynomial. One letter per
    english alphabet used for coefficient names.
    TODO(drofp): Figure out naming scheme for arbitrary number of variables.
    """
    num_of_coeff = len(coeff_ranges)
    variables = []
    coeff_names = []

    # Add coefficients to variable list.
    if num_of_coeff == 2:
        coeff_names.append('m')
        coeff_names.append('b')
    else:
        for letter_cnt in range(num_of_coeff):
            coeff_names.append(string.ascii_lowercase[letter_cnt])
    for coeff_num in range(num_of_coeff):
        if coeff_ranges[coeff_num][0] is None:
            lower_bound = -solver.Infinity()
        else:
            lower_bound = coeff_ranges[coeff_num][0]
        if coeff_ranges[coeff_num][1] is None:
            upper_bound = solver.Infinity()
        else:
            upper_bound = coeff_ranges[coeff_num][1]
        variables.append(
            solver.NumVar(lower_bound, upper_bound, coeff_names[coeff_num]))

    # Add absolute error variables to variable list
    for point_cnt in range(len(points)):
        positive_err_var = solver.NumVar(
            0, err_max, 'e' + str(point_cnt + 1) + '_plus')
        negative_err_var = solver.NumVar(
            0, err_max, 'e' + str(point_cnt + 1) + '_minus')
        variables.append(positive_err_var)
        variables.append(negative_err_var)
    return variables

def _generate_objective_fn(
    solver, num_of_coeff, variables, error_def=ErrorDefinition.SUM_ABS_DEV):
    """Generate objective function for given error definition."""
    objective = solver.Objective()
    for variable in variables[num_of_coeff:]:
        objective.SetCoefficient(variable, 1)
    return objective

def _generate_constraints(solver, points, num_of_coeff, variables):
    constraints = []
    for point_num, point in enumerate(points):
        # Equivalency constraint
        constraint = solver.Constraint(point[1], point[1])
        # Resultant Coefficient terms
        for coeff_num, coeff in enumerate(variables[:num_of_coeff]):
            power = num_of_coeff - coeff_num - 1
            x_val = point[0] ** power
            constraint.SetCoefficient(coeff, x_val)

        # Error terms
        ex_plus = variables[num_of_coeff + 2 * point_num]
        ex_minus = variables[num_of_coeff + 2 * point_num + 1]
        constraint.SetCoefficient(ex_plus, -1)
        constraint.SetCoefficient(ex_minus, 1)
        constraints.append(constraint)
    return constraints

def get_optimal_polynomial(
    points=None, coeff_ranges=None, error_def=ErrorDefinition.SUM_ABS_DEV,
    err_max=10000, solver=None):
    """Optimize coefficients for any order polynomial.

    Args:
        points: A tuple of points, represented as tuples (x, y)
    coeff_ranges: A tuple of valid coefficient ranges, respresented as tuples
        (min, max). Nubmer of elements in list determines order of polynomial,
        from highest order (0th index) to lowest order (nth index).
    err_def: An ErrorDefinition enum, specifying the definition for error.
    err_max: An Integer, specifying the maximum error allowable.
    solver: a ortools.pywraplp.Solver object, if a specific solver instance is
        requested by caller.

    Returns:
        A Dictionary, the desired coefficients mapped to ther values.
    """
    if coeff_ranges is None:
        raise ValueError('Please provide appropriate coefficient range.')
    if solver is None:
        solver = pywraplp.Solver(
            'polynomial_solver', pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)
    variables = _generate_variables(
        solver, points, coeff_ranges, err_max=err_max,
        error_def=error_def)
    num_of_coeff = len(coeff_ranges)
    _generate_objective_fn(solver, num_of_coeff, variables)
    _generate_constraints(solver, points, num_of_coeff, variables)
    solver.Solve()

    var_to_val = dict()
    for coeff in variables[:num_of_coeff]:
        var_to_val[coeff.name()] = coeff.solution_value()
    return var_to_val

def demo_optimal_linear_5points():
    """Demonstration of getting optimal linear polynomial.

    Uses 5 points from Swanson's curve fitting paper.
    """
    print('STARTING LINEAR DEMO WITH 5 POINTS FROM SWANSON PAPER')
    points = (0,1), (1,3), (2,2), (3,4), (4,5)
    coeff_ranges = ((None, None), (None, None))
    # solver = pywraplp.Solver(
    #     'polynomial_solver', pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)
    optimized_coefficients = get_optimal_polynomial(
        points=points, coeff_ranges=coeff_ranges)
    for elm in optimized_coefficients:
        print('elm: {}'.format(elm))
    print(
        'type(optimized_coefficients): {}'.format(
        type(optimized_coefficients)))
    print('optimized_coefficients: {}'.format(optimized_coefficients))
    # m, b = optimized_coefficients
    # print('Optimized m: {}, b: {}'.format(m, b))

def demo_optimal_linear_10points():
    print('STARTING LINEAR DEMO WITH 10 POINTS FROM WILLIAMS')
    x_vals = [0.0, 0.5, 1.0, 1.5, 1.9, 2.5, 3.0, 3.5, 4.0, 4.5]
    y_vals = [1.0, 0.9, 0.7, 1.5, 2.0, 2.4, 3.2, 2.0, 2.7, 3.5]
    points = tuple(zip(x_vals, y_vals))
    coeff_ranges = ((None, None), (None, None))
    print(get_optimal_polynomial(points=points, coeff_ranges=coeff_ranges))

def demo_optimal_quadratic_10points():
    print('STARTING QUADRATIC DEMO WITH 10 POINTS FROM WILLIAMS')
    x_vals = [0.0, 0.5, 1.0, 1.5, 1.9, 2.5, 3.0, 3.5, 4.0, 4.5]
    y_vals = [1.0, 0.9, 0.7, 1.5, 2.0, 2.4, 3.2, 2.0, 2.7, 3.5]
    points = tuple(zip(x_vals, y_vals))
    coeff_ranges = ((None, None), (None, None), (None, None))
    print(get_optimal_polynomial(points=points, coeff_ranges=coeff_ranges))

def demo_optimal_quadratic_19points():
    print('STARTING QUADRATIC DEMO WITH 19 POINTS FROM WILLIAMS')
    x_vals = [0.0, 0.5, 1.0, 1.5, 1.9, 2.5, 3.0, 3.5, 4.0, 4.5]
    x_vals.extend([5.0, 5.5, 6.0, 6.6, 7.0, 7.6, 8.5, 9.0, 10.0])
    y_vals = [1.0, 0.9, 0.7, 1.5, 2.0, 2.4, 3.2, 2.0, 2.7, 3.5]
    y_vals.extend([1.0, 4.0, 3.6, 2.7, 5.7, 4.6, 6.0, 6.8, 7.3])
    points = tuple(zip(x_vals, y_vals))
    coeff_ranges = ((None, None), (None, None), (None, None))
    print(get_optimal_polynomial(points=points, coeff_ranges=coeff_ranges))

def demo_optimal_cubic_10points():
    print('STARTING CUBIC DEMO WITH 10 POINTS FROM WILLIAMS')
    x_vals = [0.0, 0.5, 1.0, 1.5, 1.9, 2.5, 3.0, 3.5, 4.0, 4.5]
    y_vals = [1.0, 0.9, 0.7, 1.5, 2.0, 2.4, 3.2, 2.0, 2.7, 3.5]
    points = tuple(zip(x_vals, y_vals))
    coeff_ranges = ((None, None), (None, None), (None, None), (None, None))
    print(get_optimal_polynomial(points=points, coeff_ranges=coeff_ranges))

def main():
    demo_optimal_quadratic_19points()

if __name__ == '__main__':
    main()