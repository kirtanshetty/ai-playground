#!/usr/bin/env python3
"""
Check if all required dependencies are installed for the debug server.
"""

import sys
import subprocess

required_modules = [
    'openai',
    'langchain',
    'langchain_core',
    'psycopg2',
]

missing_modules = []

for module in required_modules:
    try:
        __import__(module)
        print(f"✓ {module}")
    except ImportError:
        print(f"✗ {module} - MISSING")
        missing_modules.append(module)

if missing_modules:
    print("\nMissing dependencies. Install them with:")
    print("  pip install -r ../tq-lambda/requirements.txt")
    print("  pip install -r ../../common-lib/llm/requirements.txt")
    sys.exit(1)
else:
    print("\nAll dependencies are installed!")
    sys.exit(0)

