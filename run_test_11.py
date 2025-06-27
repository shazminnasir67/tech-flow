#!/usr/bin/env python3
"""
Focused test runner for testing the improved test_11 method.
This script runs only the problematic test to verify the improvements.
"""

import os
import sys
import unittest
import logging
from datetime import datetime

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
selenium_tests_dir = os.path.join(current_dir, 'selenium-tests')
sys.path.insert(0, selenium_tests_dir)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('test_11_focused.log')
    ]
)

def run_test_11_only():
    """Run only test_11 to verify improvements."""
    print("=" * 80)
    print("FOCUSED TEST: test_11_ui_element_presence_checks")
    print("=" * 80)
    print(f"Start time: {datetime.now()}")
    print()
    
    try:
        # Import the test suite
        from test_suite import DevOpsAssignmentTestSuite
        
        # Create a test suite with only test_11
        suite = unittest.TestSuite()
        
        # Add only the test_11 method
        suite.addTest(DevOpsAssignmentTestSuite('test_11_ui_element_presence_checks'))
        
        # Run the test
        runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
        result = runner.run(suite)
        
        print()
        print("=" * 80)
        print("TEST RESULTS:")
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        print(f"Success: {result.wasSuccessful()}")
        print(f"End time: {datetime.now()}")
        
        # Print any failures or errors
        if result.failures:
            print("\nFAILURES:")
            for test, traceback in result.failures:
                print(f"- {test}: {traceback}")
        
        if result.errors:
            print("\nERRORS:")
            for test, traceback in result.errors:
                print(f"- {test}: {traceback}")
        
        print("=" * 80)
        
        return result.wasSuccessful()
        
    except Exception as e:
        print(f"ERROR: Failed to run test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = run_test_11_only()
    sys.exit(0 if success else 1)
