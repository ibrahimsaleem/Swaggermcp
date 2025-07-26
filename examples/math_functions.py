"""
Mathematical Functions Example
=============================

A collection of mathematical functions that can be converted to API endpoints.
This demonstrates various function types and parameter handling.
"""

import math
from typing import List, Union, Optional


def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    return a - b


def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b


def divide(a: float, b: float) -> float:
    """Divide a by b."""
    if b == 0:
        raise ValueError("Division by zero")
    return a / b


def power(base: float, exponent: float) -> float:
    """Raise base to the power of exponent."""
    return base ** exponent


def sqrt(number: float) -> float:
    """Calculate the square root of a number."""
    if number < 0:
        raise ValueError("Cannot calculate square root of negative number")
    return math.sqrt(number)


def factorial(n: int) -> int:
    """Calculate the factorial of a non-negative integer."""
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0:
        return 1
    return n * factorial(n - 1)


def fibonacci(n: int) -> int:
    """Calculate the nth Fibonacci number."""
    if n < 0:
        raise ValueError("Fibonacci is not defined for negative numbers")
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


def gcd(a: int, b: int) -> int:
    """Calculate the greatest common divisor of two integers."""
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def lcm(a: int, b: int) -> int:
    """Calculate the least common multiple of two integers."""
    return abs(a * b) // gcd(a, b)


def is_prime(n: int) -> bool:
    """Check if a number is prime."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True


def prime_factors(n: int) -> List[int]:
    """Find the prime factorization of a number."""
    if n < 2:
        return []
    
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors


def combinations(n: int, r: int) -> int:
    """Calculate the number of combinations (nCr)."""
    if r > n or r < 0:
        return 0
    if r == 0 or r == n:
        return 1
    return factorial(n) // (factorial(r) * factorial(n - r))


def permutations(n: int, r: int) -> int:
    """Calculate the number of permutations (nPr)."""
    if r > n or r < 0:
        return 0
    return factorial(n) // factorial(n - r)


def mean(numbers: List[float]) -> float:
    """Calculate the arithmetic mean of a list of numbers."""
    if not numbers:
        raise ValueError("Cannot calculate mean of empty list")
    return sum(numbers) / len(numbers)


def median(numbers: List[float]) -> float:
    """Calculate the median of a list of numbers."""
    if not numbers:
        raise ValueError("Cannot calculate median of empty list")
    
    sorted_numbers = sorted(numbers)
    n = len(sorted_numbers)
    
    if n % 2 == 0:
        return (sorted_numbers[n // 2 - 1] + sorted_numbers[n // 2]) / 2
    else:
        return sorted_numbers[n // 2]


def mode(numbers: List[float]) -> List[float]:
    """Find the mode(s) of a list of numbers."""
    if not numbers:
        raise ValueError("Cannot calculate mode of empty list")
    
    from collections import Counter
    counter = Counter(numbers)
    max_count = max(counter.values())
    return [num for num, count in counter.items() if count == max_count]


def standard_deviation(numbers: List[float]) -> float:
    """Calculate the standard deviation of a list of numbers."""
    if len(numbers) < 2:
        raise ValueError("Need at least 2 numbers for standard deviation")
    
    avg = mean(numbers)
    variance = sum((x - avg) ** 2 for x in numbers) / (len(numbers) - 1)
    return math.sqrt(variance)


def solve_quadratic(a: float, b: float, c: float) -> List[float]:
    """Solve a quadratic equation ax² + bx + c = 0."""
    if a == 0:
        raise ValueError("Coefficient 'a' cannot be zero")
    
    discriminant = b**2 - 4*a*c
    
    if discriminant > 0:
        x1 = (-b + math.sqrt(discriminant)) / (2*a)
        x2 = (-b - math.sqrt(discriminant)) / (2*a)
        return [x1, x2]
    elif discriminant == 0:
        x = -b / (2*a)
        return [x]
    else:
        return []


def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate the Euclidean distance between two points."""
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def calculate_area_circle(radius: float) -> float:
    """Calculate the area of a circle."""
    if radius < 0:
        raise ValueError("Radius cannot be negative")
    return math.pi * radius**2


def calculate_area_triangle(base: float, height: float) -> float:
    """Calculate the area of a triangle."""
    if base < 0 or height < 0:
        raise ValueError("Base and height cannot be negative")
    return 0.5 * base * height


def calculate_area_rectangle(length: float, width: float) -> float:
    """Calculate the area of a rectangle."""
    if length < 0 or width < 0:
        raise ValueError("Length and width cannot be negative")
    return length * width


def convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    """Convert temperature between Celsius, Fahrenheit, and Kelvin."""
    units = {"celsius": "C", "fahrenheit": "F", "kelvin": "K"}
    
    from_unit = from_unit.lower()
    to_unit = to_unit.lower()
    
    if from_unit not in units or to_unit not in units:
        raise ValueError("Invalid temperature unit")
    
    # Convert to Celsius first
    if from_unit == "fahrenheit":
        celsius = (value - 32) * 5/9
    elif from_unit == "kelvin":
        celsius = value - 273.15
    else:
        celsius = value
    
    # Convert from Celsius to target unit
    if to_unit == "fahrenheit":
        return celsius * 9/5 + 32
    elif to_unit == "kelvin":
        return celsius + 273.15
    else:
        return celsius 