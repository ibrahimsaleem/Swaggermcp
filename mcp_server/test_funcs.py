def add(x, y):
    """Add two numbers."""
    return int(x) + int(y)

def subtract(x, y):
    """Subtract y from x."""
    return int(x) - int(y)

def multiply(a, b):
    """Multiply two numbers."""
    return float(a) * float(b)

def divide(a, b):
    """Divide a by b. Returns error if b is zero."""
    b_float = float(b)
    if b_float == 0:
        raise ValueError("Cannot divide by zero")
    return float(a) / b_float

def greet(name="world", greeting="Hello"):
    """Generate a greeting message."""
    return f"{greeting}, {name}!"

def parse_text(text, uppercase=False):
    """Process text with optional uppercase transformation."""
    result = text.strip()
    if uppercase:
        result = result.upper()
    return result

def calculate_area(shape, width, height=None):
    """Calculate area of rectangle or square."""
    w = float(width)
    if height is None:
        # Square
        return w * w
    else:
        # Rectangle
        return w * float(height)