# linprog_curvefit
[![Build Status](https://travis-ci.com/drofp/linprog_curvefit.svg?branch=master)](https://travis-ci.com/drofp/linprog_curvefit)
[![Coverage Status](https://coveralls.io/repos/github/drofp/linprog_curvefit/badge.svg?branch=master)](https://coveralls.io/github/drofp/linprog_curvefit?branch=master)

Curve fitting with linear programming.

## How to run
Make sure [`ortools`](https://developers.google.com/optimization/install) is installed.

Easy install:
```bash
python3 -m pip install --upgrade --user ortools
```

Run with:
```bash
python3 linprog_curvefit.py
```

## How it works
This algorithm attempts to minimize the error for a chosen set of polynomials.
Error is calculated in a variety of ways for comparison.

Input:
- Points to fit
- (optional) Best fit curve as calculated by equivalent closed form formula.
