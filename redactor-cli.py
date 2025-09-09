#!/usr/bin/env python3
"""
Main entry point for the Financial Document Redactor CLI.
Maintains backward compatibility with the original interface.
"""

import os
import sys

# Add current directory to path to handle direct execution
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cli.interface import run_cli_interface


def main():
    """Main entry point for the application."""
    run_cli_interface()


if __name__ == "__main__":
    main()