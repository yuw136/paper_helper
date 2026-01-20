#!/usr/bin/env python3
"""Quick test to see what's happening with apostrophes"""

from server.utils.latex_utils import escape_latex_preserve_math, escape_latex_text

# Test strings with apostrophes
test_strings = [
    "Lu's conjecture for minimal surfaces",
    "Chern's conjecture on the discreteness",
    "Test with 'single quotes' and \"double quotes\"",
    "Test with typographic ' apostrophe",
]

print("Testing escape_latex_preserve_math:")
print("=" * 60)
for test in test_strings:
    result = escape_latex_preserve_math(test)
    print(f"Input:  {test}")
    print(f"Output: {result}")
    print(f"Match: {test == result}")
    print()

print("\nTesting escape_latex_text:")
print("=" * 60)
for test in test_strings:
    result = escape_latex_text(test)
    print(f"Input:  {test}")
    print(f"Output: {result}")
    print(f"Match: {test == result}")
    print()
