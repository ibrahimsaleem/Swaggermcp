"""
String Utility Functions Example
===============================

A collection of string manipulation functions that can be converted to API endpoints.
This demonstrates various string operations and text processing capabilities.
"""

import re
import random
import string
from typing import List, Dict, Optional, Tuple


def reverse_string(text: str) -> str:
    """Reverse a string."""
    return text[::-1]


def is_palindrome(text: str) -> bool:
    """Check if a string is a palindrome (reads the same forwards and backwards)."""
    # Remove non-alphanumeric characters and convert to lowercase
    cleaned = re.sub(r'[^a-zA-Z0-9]', '', text.lower())
    return cleaned == cleaned[::-1]


def count_words(text: str) -> int:
    """Count the number of words in a string."""
    if not text.strip():
        return 0
    return len(text.split())


def count_characters(text: str, include_spaces: bool = True) -> int:
    """Count the number of characters in a string."""
    if include_spaces:
        return len(text)
    return len(text.replace(" ", ""))


def count_vowels(text: str) -> int:
    """Count the number of vowels in a string."""
    vowels = "aeiouAEIOU"
    return sum(1 for char in text if char in vowels)


def count_consonants(text: str) -> int:
    """Count the number of consonants in a string."""
    consonants = "bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ"
    return sum(1 for char in text if char in consonants)


def to_uppercase(text: str) -> str:
    """Convert a string to uppercase."""
    return text.upper()


def to_lowercase(text: str) -> str:
    """Convert a string to lowercase."""
    return text.lower()


def to_titlecase(text: str) -> str:
    """Convert a string to title case."""
    return text.title()


def remove_spaces(text: str) -> str:
    """Remove all spaces from a string."""
    return text.replace(" ", "")


def remove_punctuation(text: str) -> str:
    """Remove all punctuation from a string."""
    return re.sub(r'[^\w\s]', '', text)


def extract_numbers(text: str) -> List[int]:
    """Extract all numbers from a string."""
    numbers = re.findall(r'\d+', text)
    return [int(num) for num in numbers]


def extract_emails(text: str) -> List[str]:
    """Extract all email addresses from a string."""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_pattern, text)


def extract_urls(text: str) -> List[str]:
    """Extract all URLs from a string."""
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(url_pattern, text)


def word_frequency(text: str) -> Dict[str, int]:
    """Count the frequency of each word in a string."""
    words = re.findall(r'\b\w+\b', text.lower())
    frequency = {}
    for word in words:
        frequency[word] = frequency.get(word, 0) + 1
    return frequency


def find_longest_word(text: str) -> str:
    """Find the longest word in a string."""
    words = text.split()
    if not words:
        return ""
    return max(words, key=len)


def find_shortest_word(text: str) -> str:
    """Find the shortest word in a string."""
    words = text.split()
    if not words:
        return ""
    return min(words, key=len)


def average_word_length(text: str) -> float:
    """Calculate the average length of words in a string."""
    words = text.split()
    if not words:
        return 0.0
    total_length = sum(len(word) for word in words)
    return total_length / len(words)


def is_anagram(str1: str, str2: str) -> bool:
    """Check if two strings are anagrams of each other."""
    # Remove spaces and convert to lowercase
    str1_clean = re.sub(r'\s', '', str1.lower())
    str2_clean = re.sub(r'\s', '', str2.lower())
    
    # Sort characters and compare
    return sorted(str1_clean) == sorted(str2_clean)


def generate_random_string(length: int, include_letters: bool = True, 
                          include_numbers: bool = True, include_symbols: bool = False) -> str:
    """Generate a random string of specified length."""
    if length <= 0:
        raise ValueError("Length must be positive")
    
    chars = ""
    if include_letters:
        chars += string.ascii_letters
    if include_numbers:
        chars += string.digits
    if include_symbols:
        chars += string.punctuation
    
    if not chars:
        raise ValueError("At least one character type must be selected")
    
    return ''.join(random.choice(chars) for _ in range(length))


def generate_vowel_name(length: int = 5) -> str:
    """Generate a random name using only vowels."""
    vowels = "aeiou"
    return ''.join(random.choice(vowels) for _ in range(length))


def caesar_cipher(text: str, shift: int) -> str:
    """Apply Caesar cipher to a string."""
    result = ""
    for char in text:
        if char.isalpha():
            # Determine the base (a or A)
            base = ord('a') if char.islower() else ord('A')
            # Apply shift and wrap around
            shifted = (ord(char) - base + shift) % 26
            result += chr(base + shifted)
        else:
            result += char
    return result


def rot13(text: str) -> str:
    """Apply ROT13 cipher to a string."""
    return caesar_cipher(text, 13)


def validate_password(password: str) -> Dict[str, bool]:
    """Validate a password and return criteria results."""
    validation = {
        "length_8": len(password) >= 8,
        "has_uppercase": any(char.isupper() for char in password),
        "has_lowercase": any(char.islower() for char in password),
        "has_digit": any(char.isdigit() for char in password),
        "has_special": any(char in string.punctuation for char in password)
    }
    validation["is_strong"] = all(validation.values())
    return validation


def format_phone_number(phone: str) -> str:
    """Format a phone number to (XXX) XXX-XXXX format."""
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    if len(digits) != 10:
        raise ValueError("Phone number must have exactly 10 digits")
    
    return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"


def format_credit_card(card_number: str) -> str:
    """Format a credit card number to XXXX-XXXX-XXXX-XXXX format."""
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', card_number)
    
    if len(digits) != 16:
        raise ValueError("Credit card number must have exactly 16 digits")
    
    return f"{digits[:4]}-{digits[4:8]}-{digits[8:12]}-{digits[12:]}"


def slugify(text: str) -> str:
    """Convert a string to a URL-friendly slug."""
    # Convert to lowercase and replace spaces with hyphens
    slug = text.lower().replace(" ", "-")
    # Remove special characters except hyphens
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    # Remove multiple consecutive hyphens
    slug = re.sub(r'-+', '-', slug)
    # Remove leading and trailing hyphens
    slug = slug.strip('-')
    return slug


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to a maximum length with optional suffix."""
    if len(text) <= max_length:
        return text
    
    # Account for suffix length
    actual_max = max_length - len(suffix)
    if actual_max <= 0:
        return suffix
    
    return text[:actual_max] + suffix


def wrap_text(text: str, width: int) -> List[str]:
    """Wrap text to specified width, breaking at word boundaries."""
    if width <= 0:
        raise ValueError("Width must be positive")
    
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        if len(current_line) + len(word) + 1 <= width:
            current_line += (word + " ")
        else:
            if current_line:
                lines.append(current_line.strip())
            current_line = word + " "
    
    if current_line:
        lines.append(current_line.strip())
    
    return lines


def analyze_text(text: str) -> Dict[str, any]:
    """Comprehensive text analysis."""
    analysis = {
        "length": len(text),
        "word_count": count_words(text),
        "character_count": count_characters(text),
        "character_count_no_spaces": count_characters(text, include_spaces=False),
        "vowel_count": count_vowels(text),
        "consonant_count": count_consonants(text),
        "sentence_count": len(re.split(r'[.!?]+', text.strip())),
        "paragraph_count": len([p for p in text.split('\n\n') if p.strip()]),
        "longest_word": find_longest_word(text),
        "shortest_word": find_shortest_word(text),
        "average_word_length": average_word_length(text),
        "word_frequency": word_frequency(text),
        "is_palindrome": is_palindrome(text),
        "has_numbers": bool(extract_numbers(text)),
        "has_emails": bool(extract_emails(text)),
        "has_urls": bool(extract_urls(text))
    }
    
    return analysis


def find_substring_positions(text: str, substring: str) -> List[int]:
    """Find all positions of a substring in a string."""
    positions = []
    start = 0
    while True:
        pos = text.find(substring, start)
        if pos == -1:
            break
        positions.append(pos)
        start = pos + 1
    return positions


def replace_all(text: str, old: str, new: str) -> str:
    """Replace all occurrences of a substring in a string."""
    return text.replace(old, new)


def remove_duplicate_words(text: str) -> str:
    """Remove duplicate words from a string while preserving order."""
    words = text.split()
    seen = set()
    result = []
    
    for word in words:
        if word not in seen:
            seen.add(word)
            result.append(word)
    
    return " ".join(result)


def sort_words_alphabetically(text: str) -> str:
    """Sort words in a string alphabetically."""
    words = text.split()
    return " ".join(sorted(words))


def sort_words_by_length(text: str) -> str:
    """Sort words in a string by length."""
    words = text.split()
    return " ".join(sorted(words, key=len)) 