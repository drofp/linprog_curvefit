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

def _demo_add_objective(
    solver, m, b, e1_plus, e1_minus, e2_plus, e2_minus, e3_plus, e3_minus,
    e4_plus, e4_minus, e5_plus, e5_minus):
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
    return objective

def _demo_add_constraints(
    solver, m, b, e1_plus, e1_minus, e2_plus, e2_minus, e3_plus, e3_minus,
    e4_plus, e4_minus, e5_plus, e5_minus):
    # solver.Add(b - e1_plus + e1_minus == 1) # Alternative for constraint0
    constraint0 = solver.Constraint(1, 1)
    constraint0.SetCoefficient(b, 1)
    constraint0.SetCoefficient(e1_plus, -1)
    constraint0.SetCoefficient(e1_minus, 1)

    # solver.Add(m + b - e2_plus + e2_minus == 3) # Alternative constraint1
    constraint1 = solver.Constraint(3, 3)
    constraint1.SetCoefficient(m, 1)
    constraint1.SetCoefficient(b, 1)
    constraint1.SetCoefficient(e2_plus, -1)
    constraint1.SetCoefficient(e2_minus, 1)

    solver.Add(2*m + b - e3_plus + e3_minus == 2)
    solver.Add(3*m + b - e4_plus + e4_minus == 4)
    solver.Add(4*m + b - e5_plus + e5_minus == 5)

def demo_linear(points=None, coeff_ranges=None):
    """Optimize coefficients for a linear polynomial."""
    solver = pywraplp.Solver(
        'linear_polynomial_solver', pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)
    # m = solver.NumVar(-100, 100, 'm')
    # b = solver.NumVar(-100, 100, 'b')
    m = solver.NumVar(-solver.Infinity(), solver.Infinity(), 'm')
    b = solver.NumVar(-solver.Infinity(), solver.Infinity(), 'b')
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

    objective = _demo_add_objective(
        solver, m, b, e1_plus, e1_minus, e2_plus, e2_minus, e3_plus, e3_minus,
        e4_plus, e4_minus, e5_plus, e5_minus)

    _demo_add_constraints(
        solver, m, b, e1_plus, e1_minus, e2_plus, e2_minus, e3_plus, e3_minus,
        e4_plus, e4_minus, e5_plus, e5_minus)
    print('Number of constraints: {}, Number of variables: {}'.format(
        solver.NumConstraints(), solver.NumVariables()))

    solver.Solve()
    print('Solution:')
    print('Objective value =', objective.Value())
    print('m =', m.solution_value())
    print('b =', b.solution_value())
    return m.solution_value(), b.solution_value()

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
        if coeff_ranges[coeff_num][1] is None:
            upper_bound = solver.Infinity()
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
        print('just added error vars "{}" and "{}"'.format(
            positive_err_var.name(), negative_err_var.name()))
    return variables

def _generate_objective_fn(
    solver, num_of_coeff, variables, error_def=ErrorDefinition.SUM_ABS_DEV):
    """Generate objective function for given error definition."""
    objective = solver.Objective()
    for variable in variables[num_of_coeff:]:
        objective.SetCoefficient(variable, 1)
        print('just set objective for "{}"'.format(variable.name()))
    return objective

def _generate_constraints(solver, points, num_of_coeff, variables):
    constraints = []
    for point_num, point in enumerate(points):
        # Equivalency constraint
        constraint = solver.Constraint(point[1], point[1])
        print('generating constraint equal to: {}'.format(point[1]))
        # Resultant Coefficient terms
        for coeff_num, coeff in enumerate(variables[:num_of_coeff]):
            power = num_of_coeff - coeff_num - 1
            x_val = point[0] ** power
            print('x_val: {}'.format(x_val))
            constraint.SetCoefficient(coeff, x_val)
            print('just set term with coeff: {}, point[0]: {}, power: {}'.format(
                coeff, point[0], power))

        # Error terms
        ex_plus = variables[num_of_coeff + 2 * point_num]
        ex_minus = variables[num_of_coeff + 2 * point_num + 1]
        print('setting ex_plus: {}, ex_minus: {}'.format(
            ex_plus.name(), ex_minus.name()))
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
    print('generated {} variables!'.format(solver.NumVariables()))
    print('variables: {}, each of type {}'.format(variables, type(variables[0])))
    num_of_coeff = len(coeff_ranges)
    objective = _generate_objective_fn(solver, num_of_coeff, variables)
    print('generated objective: {}'.format(objective))
    _generate_constraints(solver, points, num_of_coeff, variables)
    print('generated {} constraints!'.format(solver.NumConstraints()))
    print('variables are still: {}'.format(variables))
    solver.Solve()
    print('solved linear program with {} coefficients!'.format(num_of_coeff))
    print('variables are still: {}'.format(variables[:num_of_coeff]))
    print('m: {}, b: {}'.format(
        variables[0].solution_value(), variables[1].solution_value()))
    var_to_val = dict()
    for coeff in variables[:num_of_coeff]:
        var_to_val[coeff.name()] = coeff.solution_value()
    return var_to_val

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

    # print(get_optimal_polynomial(points, coeff_ranges))
    demo_linear(points=points, coeff_ranges=coeff_ranges)

    return (1.52381, 0.285714)

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
    minimize_error()
    demo_optimal_cubic_10points()

if __name__ == '__main__':
    main()