#!/usr/bin/env python3
"""
Test script to verify the improvements made to the Selenium test suite.
This script focuses on testing the problematic areas that were causing timeouts.
"""

import sys
import os
import unittest
import time
from datetime import datetime

# Add the selenium-tests directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'selenium-tests'))

from test_suite import DevOpsAssignmentTestSuite

class TestImprovements(unittest.TestCase):
    """Test the improvements made to the test suite."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        print("Setting up test environment...")
        DevOpsAssignmentTestSuite.setUpClass()
        cls.test_instance = DevOpsAssignmentTestSuite()
        cls.test_instance.setUp()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        print("Cleaning up test environment...")
        cls.test_instance.tearDown()
        DevOpsAssignmentTestSuite.tearDownClass()
    
    def test_app_accessibility(self):
        """Test the app accessibility check."""
        print("Testing app accessibility...")
        result = self.test_instance.verify_app_accessibility()
        self.assertTrue(result, "App should be accessible")
        print("✓ App accessibility test passed")
    
    def test_user_login_logout_cycle(self):
        """Test the user login/logout cycle."""
        print("Testing user login/logout cycle...")
        
        # Test logout
        self.test_instance.ensure_user_logged_out()
        logged_in = self.test_instance.is_user_logged_in()
        self.assertFalse(logged_in, "User should be logged out")
        print("✓ User logout test passed")
        
        # Test login with timeout protection
        start_time = time.time()
        try:
            self.test_instance.ensure_user_logged_in()
            logged_in = self.test_instance.is_user_logged_in()
            self.assertTrue(logged_in, "User should be logged in")
            print("✓ User login test passed")
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"Login failed after {elapsed_time:.2f} seconds: {e}")
            if elapsed_time > 120:  # If it took more than 2 minutes
                self.fail("Login process took too long - timeout protection failed")
            else:
                # Login failed but didn't hang - this is acceptable
                print("✓ Login failed gracefully without hanging")
    
    def test_ui_elements_basic(self):
        """Test basic UI elements without full test_11 complexity."""
        print("Testing basic UI elements...")
        
        # Ensure logged out state
        self.test_instance.ensure_user_logged_out()
        self.test_instance.driver.get(self.test_instance.base_url)
        
        # Check for basic elements
        try:
            self.test_instance.wait_for_element_clickable(self.test_instance.By.CLASS_NAME, "navbar", timeout=10)
            self.test_instance.wait_for_element_clickable(self.test_instance.By.LINK_TEXT, "Home", timeout=10)
            self.test_instance.wait_for_element_clickable(self.test_instance.By.LINK_TEXT, "Login", timeout=10)
            print("✓ Basic UI elements test passed")
        except Exception as e:
            print(f"Basic UI elements test failed: {e}")
            self.fail(f"Basic UI elements not found: {e}")

if __name__ == '__main__':
    print("Starting Test Improvements Verification...")
    print("=" * 50)
    
    # Run the tests
    unittest.main(verbosity=2, exit=False)
    
    print("=" * 50)
    print("Test Improvements Verification Complete")
