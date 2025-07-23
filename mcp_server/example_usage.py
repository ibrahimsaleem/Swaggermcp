#!/usr/bin/env python3
"""
Example: How to use the MCP server to convert Python functions to API endpoints.

This example shows:
1. Creating a Python file with functions
2. Uploading it to the MCP server
3. Using the generated API endpoints
"""

import requests
import tempfile
import time

# Example 1: Create a Python file with some utility functions
utility_functions = '''
def celsius_to_fahrenheit(celsius):
    """Convert Celsius to Fahrenheit."""
    c = float(celsius)
    return (c * 9/5) + 32

def fahrenheit_to_celsius(fahrenheit):
    """Convert Fahrenheit to Celsius."""
    f = float(fahrenheit)
    return (f - 32) * 5/9

def calculate_bmi(weight_kg, height_m):
    """Calculate Body Mass Index."""
    w = float(weight_kg)
    h = float(height_m)
    if h <= 0:
        raise ValueError("Height must be positive")
    return w / (h * h)

def is_prime(n):
    """Check if a number is prime."""
    num = int(n)
    if num < 2:
        return False
    for i in range(2, int(num ** 0.5) + 1):
        if num % i == 0:
            return False
    return True

def fibonacci(n):
    """Get the nth Fibonacci number."""
    n = int(n)
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        a, b = 0, 1
        for _ in range(n - 1):
            a, b = b, a + b
        return b
'''

def main():
    print("🔧 MCP Server Usage Example\n")
    
    # Step 1: Save the Python code to a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(utility_functions)
        temp_file = f.name
    
    print("1. Created temporary Python file with utility functions")
    
    # Step 2: Upload to MCP server
    print("\n2. Uploading to MCP server...")
    with open(temp_file, 'rb') as f:
        files = {'file': ('utilities.py', f, 'text/x-python')}
        response = requests.post('http://localhost:8000/upload', files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Upload successful!")
        print(f"   Generated endpoints: {result['endpoints']}")
        print(f"   Swagger URL: {result['swagger_url']}")
    else:
        print(f"   ❌ Upload failed: {response.text}")
        return
    
    # Wait a moment for the generated server to start
    time.sleep(2)
    
    # Step 3: Test the generated API endpoints
    print("\n3. Testing generated API endpoints:")
    
    api_base = "http://localhost:8001"
    
    # Test temperature conversion
    print("\n   📊 Temperature Conversion:")
    resp = requests.get(f"{api_base}/celsius_to_fahrenheit?celsius=25")
    print(f"   25°C = {resp.json()['result']}°F")
    
    resp = requests.get(f"{api_base}/fahrenheit_to_celsius?fahrenheit=77")
    print(f"   77°F = {resp.json()['result']}°C")
    
    # Test BMI calculation
    print("\n   💪 BMI Calculation:")
    resp = requests.get(f"{api_base}/calculate_bmi?weight_kg=70&height_m=1.75")
    print(f"   BMI for 70kg, 1.75m = {resp.json()['result']:.2f}")
    
    # Test prime numbers
    print("\n   🔢 Prime Number Check:")
    for n in [7, 10, 17, 100]:
        resp = requests.get(f"{api_base}/is_prime?n={n}")
        is_prime = resp.json()['result']
        print(f"   {n} is {'prime' if is_prime else 'not prime'}")
    
    # Test Fibonacci
    print("\n   🌀 Fibonacci Sequence:")
    fibs = []
    for i in range(10):
        resp = requests.get(f"{api_base}/fibonacci?n={i}")
        fibs.append(str(resp.json()['result']))
    print(f"   First 10 numbers: {', '.join(fibs)}")
    
    print(f"\n✨ All done! Check out the interactive API docs at: {result['swagger_url']}")

if __name__ == "__main__":
    print("⚠️  Make sure the MCP server is running on port 8000 first!")
    print("    Run: uvicorn main:app --port 8000\n")
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to MCP server. Is it running?")