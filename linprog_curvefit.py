#!/usr/bin/env python3

def minimize_error(points=None, coeff_ranges=None):
    """Minimize error between polynomial curve and input points.

    Args:
        points: A list of points, represented as tuples (x, y)
    coeff_ranges: A list of valid coefficient ranges, respresented as tuples
        (min, max). Nubmer of elements in list determines order of polynomial,
        from highest order (0th index) to lowest order (nth index).
    """
    if points is None:
        points = [(0,0), (1,1)]
    if coeff_ranges is None:
        coeff_ranges = [(-100, 100)]
    return 'foo'


def main():
    pass

if __name__ == '__main__':
    main()