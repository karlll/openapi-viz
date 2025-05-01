#!/usr/bin/env python3
"""
Simple script to run the tests for the OpenAPI Visualization Tool.
"""

import unittest
import sys
import os

# Add the parent directory to the path so we can import the test module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the test module
from tests.test_openapi_viz import TestOpenAPIGraphGenerator

if __name__ == "__main__":
    # Create a test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestOpenAPIGraphGenerator)
    
    # Run the tests
    result = unittest.TextTestRunner().run(suite)
    
    # Exit with appropriate status code
    sys.exit(not result.wasSuccessful())