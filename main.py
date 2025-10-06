#!/usr/bin/env python3
"""
Financial Document Redactor - Main Entry Point

A Python application for automatically redacting sensitive information from 
financial documents (bank statements, W2 forms, tax returns, pay stubs).

Usage:
    python main.py          # Launch GUI interface
    python main.py --help   # Show help
"""

import sys
import argparse


def show_help():
    """Show help information."""
    print(__doc__)
    print("Available interfaces:")
    print("  GUI:  python redactor-gui.py    # Graphical interface")
    print("  CLI:  Coming soon               # Command line interface")
    print()
    print("For more information, see README.md")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Financial Document Redactor",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--help-all', 
        action='store_true',
        help='Show detailed help information'
    )
    
    if len(sys.argv) == 1:
        # No arguments, launch GUI
        try:
            from subprocess import run
            run([sys.executable, 'redactor-gui.py'])
        except Exception as e:
            print(f"Error launching GUI: {e}")
            print("Try running: python redactor-gui.py")
    else:
        args = parser.parse_args()
        if args.help_all:
            show_help()
        else:
            parser.print_help()


if __name__ == "__main__":
    main()