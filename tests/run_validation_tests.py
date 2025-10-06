#!/usr/bin/env python3
"""
Quick runner for redaction validation tests
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_redaction_validation import main

if __name__ == "__main__":
    main()