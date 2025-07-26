#!/usr/bin/env python
import math
# Sebastian Raschka 2014
# Functions to calculate factorial, combinations, and permutations
# bundled in an simple command line interface.

def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n-1)
    
def combinations(n, r):
    numerator = factorial(n)
    denominator = factorial(r) * factorial(n-r)
    return int(numerator/denominator)
    
def permutations(n, r):
    numerator = factorial(n)
    denominator = factorial(n-r)
    return int(numerator/denominator)

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    return a / b

def power(a, b):
    return a ** b

def sqrt(a):
    return a ** 0.5

def log(a):
    return math.log(a)

def exp(a):
    return math.exp(a)


assert(factorial(3) == 6)
assert(combinations(20, 8) == 125970)
assert(permutations(30, 3) == 24360)