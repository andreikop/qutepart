#!/usr/bin/env python3
import unittest
import sys

if __name__ == "__main__":
    # Look for all tests. Using test_* instead of test_*.py finds modules (test_syntax and test_indenter).
    suite = unittest.TestLoader().discover('.', pattern="test_*")
    print("Suite created")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("Run done")

    # Indicate success or failure via the exit code: success = 0, failure = 1.
    if result.wasSuccessful():
        print("OK")
        sys.exit(0)
    else:
        print("Failed")
        sys.exit(not result.wasSuccessful())
