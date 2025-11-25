#!/usr/bin/env python3
"""
Test runner script for CircularQuery.
"""
import sys
import subprocess
import os

def run_tests():
    """Run all tests and display results."""
    print("🧪 Running CircularQuery Test Suite...")
    print("=" * 50)
    
    # Check if pytest is available
    try:
        import pytest
    except ImportError:
        print("❌ pytest not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest"])
        import pytest
    
    # Add current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # Run tests
    test_args = [
        "tests/",
        "-v",
        "--tb=short",
        "--color=yes"
    ]
    
    result = pytest.main(test_args)
    
    if result == 0:
        print("\n✅ All tests passed!")
        print("Your refactored application is ready to use.")
    else:
        print(f"\n❌ Some tests failed (exit code: {result})")
        print("Please check the test output above for details.")
    
    return result


if __name__ == "__main__":
    sys.exit(run_tests())