#!/usr/bin/env python3
"""
Test runner for MurphyAI bot
Provides easy way to run tests with different configurations
"""

import subprocess
import sys
import os


def run_tests(test_type="all", coverage=False, verbose=False):
    """Run tests with specified configuration"""
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test selection
    if test_type == "unit":
        cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "fast":
        cmd.extend(["-m", "not slow"])
    
    # Add coverage if requested
    if coverage:
        cmd.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])
    
    # Add verbosity
    if verbose:
        cmd.extend(["-v", "-s"])
    
    # Run the tests
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=os.path.dirname(__file__))
    return result.returncode


def main():
    """Main test runner function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run MurphyAI bot tests")
    parser.add_argument(
        "--type", 
        choices=["all", "unit", "integration", "fast"], 
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true",
        help="Run with coverage reporting"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Run with verbose output"
    )
    
    args = parser.parse_args()
    
    # Check if pytest is installed
    try:
        import pytest
    except ImportError:
        print("Error: pytest not installed. Run: pip install -r requirements.txt")
        return 1
    
    # Run tests
    return run_tests(args.type, args.coverage, args.verbose)


if __name__ == "__main__":
    sys.exit(main())
