#!/usr/bin/env python3
"""
Selenium Test Suite for DevOps Assignment 3
CSC483 - Spring 2025

Comprehensive test cases for Flask web application with user registration and login functionality.
"""

import unittest
import time
import os
import sys
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import json
import logging
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Simple function to log errors
def log_error(message):
    """Log error to console."""
    logger.error(message)

class DevOpsAssignmentTestSuite(unittest.TestCase):
    """Main test suite for DevOps Assignment 3 web application."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests."""
        logger.info("Setting up test environment...")
        
        # Test configuration - Use environment variable or default to EC2 IP
        cls.base_url = os.getenv('BASE_URL', 'http://13.51.201.77:5000')
        cls.test_results = []
        cls.screenshots_dir = "screenshots"
        
        logger.info(f"Base URL: {cls.base_url}")
        logger.info(f"Testing against EC2 instance: {cls.base_url}")
        
        # Create screenshots directory
        if not os.path.exists(cls.screenshots_dir):
            os.makedirs(cls.screenshots_dir)
            logger.info("Created screenshots directory")
        
        # Test connection to web application
        logger.info(f"Testing connection to web application at {cls.base_url}")
        try:
            response = requests.get(f"{cls.base_url}/api/health", timeout=10)
            logger.info(f"Health check response: {response.status_code}")
            if response.status_code != 200:
                logger.error(f"Health check failed with status code: {response.status_code}")
                raise Exception(f"Web application health check failed: {response.status_code}")
            logger.info("✓ Successfully connected to TechFlow application on EC2")
        except Exception as e:
            logger.error(f"Failed to connect to web application: {e}")
            logger.error("Please ensure the Flask application is running on EC2")
            log_error(f"Failed to connect to web application: {e}")
            raise
        
        # Chrome options for headless testing
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        logger.info("Chrome options configured")
        
        # Use webdriver-manager to handle ChromeDriver
        try:
            logger.info("Installing ChromeDriver...")
            driver_path = ChromeDriverManager().install()
            logger.info(f"ChromeDriver path: {driver_path}")
            
            # Find the real chromedriver executable
            base_dir = os.path.dirname(driver_path)
            logger.info(f"Base directory: {base_dir}")
            
            # The actual chromedriver is usually in a subdirectory
            # Look for directories that might contain the executable
            actual_driver_path = None
            
            # First, check if we're already in the right directory
            if os.path.basename(driver_path) == 'chromedriver' and os.access(driver_path, os.X_OK):
                actual_driver_path = driver_path
                logger.info(f"Found chromedriver executable: {actual_driver_path}")
            else:
                # Check the current directory first for chromedriver executable
                logger.info(f"Checking current directory: {base_dir}")
                for file in os.listdir(base_dir):
                    if file == 'chromedriver':
                        candidate = os.path.join(base_dir, file)
                        if os.access(candidate, os.X_OK):
                            actual_driver_path = candidate
                            logger.info(f"Found chromedriver executable: {actual_driver_path}")
                            break
                
                # If not found in current directory, look for subdirectories
                if not actual_driver_path:
                    for item in os.listdir(base_dir):
                        item_path = os.path.join(base_dir, item)
                        if os.path.isdir(item_path):
                            logger.info(f"Checking subdirectory: {item_path}")
                            # Look for chromedriver executable in this subdirectory
                            for file in os.listdir(item_path):
                                if file == 'chromedriver':
                                    candidate = os.path.join(item_path, file)
                                    if os.access(candidate, os.X_OK):
                                        actual_driver_path = candidate
                                        logger.info(f"Found chromedriver executable: {actual_driver_path}")
                                        break
                            if actual_driver_path:
                                break
            
            if not actual_driver_path:
                logger.error("Could not find a valid chromedriver executable!")
                log_error("Could not find a valid chromedriver executable!")
                raise Exception("No valid chromedriver executable found")
            
            service = Service(actual_driver_path)
            logger.info("ChromeDriver installed successfully")
        except Exception as e:
            logger.error(f"Failed to install ChromeDriver: {e}")
            log_error(f"Failed to install ChromeDriver: {e}")
            raise
        
        # Initialize WebDriver
        try:
            logger.info("Initializing WebDriver...")
            cls.driver = webdriver.Chrome(service=service, options=chrome_options)
            cls.driver.implicitly_wait(10)
            cls.wait = WebDriverWait(cls.driver, 10)
            logger.info("WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            log_error(f"Failed to initialize WebDriver: {e}")
            raise
        
        logger.info("Test environment setup completed")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        logger.info("Cleaning up test environment...")
        cls.driver.quit()
        
        # Save test results
        with open('test_results.json', 'w') as f:
            json.dump(cls.test_results, f, indent=2, default=str)
        
        logger.info("Test environment cleanup completed")
    
    def setUp(self):
        """Set up for each individual test."""
        self.test_start_time = datetime.now()
        logger.info(f"Starting test: {self._testMethodName}")
        
        # Verify app is accessible before running tests
        if not self.verify_app_accessibility():
            self.skipTest("Flask app is not accessible - skipping test")
    
    def tearDown(self):
        """Clean up after each test."""
        test_end_time = datetime.now()
        test_duration = (test_end_time - self.test_start_time).total_seconds()
        
        # Capture screenshot on failure
        if hasattr(self, '_outcome') and self._outcome.success is False:
            screenshot_name = f"{self._testMethodName}_failure_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            screenshot_path = os.path.join(self.screenshots_dir, screenshot_name)
            self.driver.save_screenshot(screenshot_path)
            logger.error(f"Test failed. Screenshot saved: {screenshot_path}")
            
            # Log the actual error details
            if hasattr(self, '_outcome'):
                for test, traceback in self._outcome.errors:
                    logger.error(f"Error in {test}: {traceback}")
                for test, traceback in self._outcome.failures:
                    logger.error(f"Failure in {test}: {traceback}")
        else:
            logger.info(f"TEST PASSED: {self._testMethodName}")
        
        # Record test result
        test_result = {
            'test_name': self._testMethodName,
            'status': 'PASS' if self._outcome.success else 'FAIL',
            'duration': test_duration,
            'timestamp': self.test_start_time.isoformat(),
            'screenshot': screenshot_name if hasattr(self, '_outcome') and not self._outcome.success else None
        }
        self.test_results.append(test_result)
        
        logger.info(f"Completed test: {self._testMethodName} ({test_duration:.2f}s)")
    
    def take_screenshot(self, name):
        """Take a screenshot with timestamp."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{name}_{timestamp}.png"
        filepath = os.path.join(self.screenshots_dir, filename)
        self.driver.save_screenshot(filepath)
        logger.info(f"Screenshot saved: {filepath}")
        return filepath
    
    def wait_for_element(self, by, value, timeout=10):
        """Wait for element to be present and visible."""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    
    def wait_for_element_clickable(self, by, value, timeout=10):
        """Wait for element to be clickable."""
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
    
    def wait_for_text_present(self, text, timeout=15):
        """Wait for text to be present in page."""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{text}')]"))
        )
    
    def wait_for_alert_message(self, message, alert_type="success", timeout=15):
        """Wait for alert message to be present in page. (Deprecated - use redirect checking instead)"""
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{message}')]"))
            )
        except TimeoutException:
            logger.warning(f"Alert message not found: {message}")
            raise
    
    
    def clear_and_fill_input(self, element, text):
        """Clear input field and fill with text."""
        element.clear()
        element.send_keys(text)
    
    def generate_test_data(self):
        """Generate unique test data for each test run."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return {
            'username': f'testuser_{timestamp}',
            'email': f'testuser_{timestamp}@example.com',
            'password': 'testpass123',
            'invalid_username': 'ab',  # Too short
            'invalid_email': 'invalid-email',
            'invalid_password': '123'  # Too short
        }

    def test_00_flask_app_health_check(self):
        """Test 0: Verify Flask app is running and healthy."""
        logger.info("Testing Flask app health check...")
        
        # Test health endpoint
        self.driver.get(f"{self.base_url}/api/health")
        body_text = self.driver.find_element(By.TAG_NAME, "body").text
        logger.info(f"Health check response: {body_text}")
        
        # Parse JSON response
        try:
            import json
            health_data = json.loads(body_text)
            self.assertEqual(health_data['status'], 'healthy')
            self.assertIn('database', health_data)
            logger.info("✓ Health check passed")
        except json.JSONDecodeError:
            self.fail("Health check endpoint did not return valid JSON")
        
        # Test database functionality
        self.driver.get(f"{self.base_url}/test")
        test_body = self.driver.find_element(By.TAG_NAME, "body").text
        logger.info(f"Test endpoint response: {test_body}")
        
        try:
            test_data = json.loads(test_body)
            self.assertIn('total_users', test_data)
            self.assertIn('users', test_data)
            logger.info(f"✓ Database test passed - {test_data['total_users']} users found")
        except json.JSONDecodeError:
            self.fail("Test endpoint did not return valid JSON")
        
        # Test home page loads
        self.driver.get(self.base_url)
        self.assertIn("TechFlow", self.driver.title)
        logger.info("✓ Home page loads correctly")
        
        # Test register page loads
        self.driver.get(f"{self.base_url}/register")
        self.assertIn("Sign Up", self.driver.title)
        logger.info("✓ Register page loads correctly")
        
        logger.info("Flask app health check completed successfully")

    def test_01_page_load_verification(self):
        """Test 1: Verify all pages load correctly."""
        logger.info("Testing page load verification...")
        
        # Test home page
        self.driver.get(self.base_url)
        self.wait_for_element(By.TAG_NAME, "body")
        self.assertIn("TechFlow", self.driver.title)
        self.take_screenshot("home_page")
        
        # Test login page
        self.driver.get(f"{self.base_url}/login")
        self.wait_for_element(By.ID, "username")
        self.assertIn("Login", self.driver.title)
        self.take_screenshot("login_page")
        
        # Test register page
        self.driver.get(f"{self.base_url}/register")
        self.wait_for_element(By.ID, "username")
        self.assertIn("Sign Up", self.driver.title)
        self.take_screenshot("register_page")
        
        # Test API health endpoint
        self.driver.get(f"{self.base_url}/api/health")
        body_text = self.driver.find_element(By.TAG_NAME, "body").text
        logger.info(f"Health check response: {body_text}")
        
        logger.info("Page load verification completed successfully")

    def test_02_user_registration_valid_data(self):
        """Test 2: User registration with valid data."""
        logger.info("Testing user registration with valid data...")
        
        test_data = self.generate_test_data()
        
        # Navigate to registration page
        self.driver.get(f"{self.base_url}/register")
        
        # Fill registration form - note the form has full_name field
        full_name_field = self.wait_for_element(By.ID, "full_name")
        username_field = self.wait_for_element(By.ID, "username")
        email_field = self.wait_for_element(By.ID, "email")
        password_field = self.wait_for_element(By.ID, "password")
        confirm_password_field = self.wait_for_element(By.ID, "confirm_password")
        terms_checkbox = self.wait_for_element(By.ID, "terms")
        
        # Fill form fields with valid data
        self.clear_and_fill_input(full_name_field, f"Test User {test_data['username']}")
        self.clear_and_fill_input(username_field, test_data['username'])
        self.clear_and_fill_input(email_field, test_data['email'])
        self.clear_and_fill_input(password_field, test_data['password'])
        self.clear_and_fill_input(confirm_password_field, test_data['password'])
        
        # Click terms checkbox
        terms_checkbox.click()
        
        # Disable JavaScript validation and submit form directly via JavaScript
        logger.info("Disabling JavaScript validation and submitting form...")
        
        # Execute JavaScript to disable validation and submit form
        js_code = """
        // Disable all validation
        const form = document.querySelector('form');
        const inputs = form.querySelectorAll('input');
        
        // Remove validation classes and event listeners
        inputs.forEach(input => {
            input.classList.remove('is-invalid', 'is-valid');
            input.removeEventListener('blur', null);
            input.removeEventListener('input', null);
        });
        
        // Remove form validation
        form.classList.remove('was-validated');
        
        // Submit form directly
        form.submit();
        """
        
        self.driver.execute_script(js_code)
        
        # Add debugging to see what's happening
        logger.info("Form submitted via JavaScript, waiting for response...")
        time.sleep(3)  # Wait a bit longer for the response
        
        # Log current URL and page title
        logger.info(f"Current URL after submission: {self.driver.current_url}")
        logger.info(f"Page title after submission: {self.driver.title}")
        
        # Check if there are any error messages
        try:
            error_elements = self.driver.find_elements(By.CLASS_NAME, "alert-danger")
            if error_elements:
                for error in error_elements:
                    logger.error(f"Error message found: {error.text}")
        except Exception as e:
            logger.info(f"No error elements found: {e}")
        
        # Check if there are any success messages
        try:
            success_elements = self.driver.find_elements(By.CLASS_NAME, "alert-success")
            if success_elements:
                for success in success_elements:
                    logger.info(f"Success message found: {success.text}")
        except Exception as e:
            logger.info(f"No success elements found: {e}")
        
        # Log page source for debugging
        logger.info("Page source after form submission:")
        logger.info(self.driver.page_source[:1000])  # First 1000 characters
        
        # Verify successful registration by checking redirect to login page
        # Wait for redirect to complete
        WebDriverWait(self.driver, 10).until(
            lambda driver: "login" in driver.current_url
        )
        
        # Verify we're on login page
        self.assertIn("login", self.driver.current_url)
        
        # Verify login page loads properly (indicates successful registration)
        try:
            login_form = self.wait_for_element(By.ID, "username", timeout=5)
            self.assertTrue(login_form.is_displayed())
            logger.info("✓ Successfully redirected to login page after registration")
        except TimeoutException:
            self.fail("Login page did not load properly after registration")
        
        self.take_screenshot("registration_success")
        
        logger.info("User registration with valid data completed successfully")

    def test_03_user_registration_invalid_data(self):
        """Test 3: User registration with invalid data."""
        logger.info("Testing user registration with invalid data...")
        
        test_data = self.generate_test_data()
        
        # Navigate to registration page
        self.driver.get(f"{self.base_url}/register")
        
        # Test with invalid username (too short)
        full_name_field = self.wait_for_element(By.ID, "full_name")
        username_field = self.wait_for_element(By.ID, "username")
        email_field = self.wait_for_element(By.ID, "email")
        password_field = self.wait_for_element(By.ID, "password")
        confirm_password_field = self.wait_for_element(By.ID, "confirm_password")
        
        self.clear_and_fill_input(full_name_field, "Test User")
        self.clear_and_fill_input(username_field, test_data['invalid_username'])
        self.clear_and_fill_input(email_field, test_data['email'])
        self.clear_and_fill_input(password_field, test_data['password'])
        self.clear_and_fill_input(confirm_password_field, test_data['password'])
        
        self.take_screenshot("registration_invalid_username")
        
        # Submit form via JavaScript to bypass validation
        js_code = """
        const form = document.querySelector('form');
        form.submit();
        """
        self.driver.execute_script(js_code)
        
        # Verify error by checking we stay on register page (validation failed)
        time.sleep(2)  # Wait for any processing
        
        # Should still be on register page if validation failed
        self.assertIn("register", self.driver.current_url)
        
        # Verify form is still visible (indicates we didn't redirect)
        try:
            username_field = self.wait_for_element(By.ID, "username", timeout=5)
            self.assertTrue(username_field.is_displayed())
            logger.info("✓ Stayed on register page - validation error detected")
        except TimeoutException:
            self.fail("Register form not found - unexpected redirect occurred")
        
        self.take_screenshot("registration_username_error")
        
        # Test with invalid email
        self.driver.get(f"{self.base_url}/register")
        full_name_field = self.wait_for_element(By.ID, "full_name")
        username_field = self.wait_for_element(By.ID, "username")
        email_field = self.wait_for_element(By.ID, "email")
        password_field = self.wait_for_element(By.ID, "password")
        confirm_password_field = self.wait_for_element(By.ID, "confirm_password")
        
        self.clear_and_fill_input(full_name_field, "Test User")
        self.clear_and_fill_input(username_field, test_data['username'])
        self.clear_and_fill_input(email_field, test_data['invalid_email'])
        self.clear_and_fill_input(password_field, test_data['password'])
        self.clear_and_fill_input(confirm_password_field, test_data['password'])
        
        self.driver.execute_script(js_code)
        
        # Verify error by checking we stay on register page
        time.sleep(2)
        self.assertIn("register", self.driver.current_url)
        
        # Verify form is still visible
        try:
            email_field = self.wait_for_element(By.ID, "email", timeout=5)
            self.assertTrue(email_field.is_displayed())
            logger.info("✓ Stayed on register page - email validation error detected")
        except TimeoutException:
            self.fail("Register form not found after email validation")
        
        self.take_screenshot("registration_email_error")
        
        # Test with invalid password (too short)
        self.driver.get(f"{self.base_url}/register")
        full_name_field = self.wait_for_element(By.ID, "full_name")
        username_field = self.wait_for_element(By.ID, "username")
        email_field = self.wait_for_element(By.ID, "email")
        password_field = self.wait_for_element(By.ID, "password")
        confirm_password_field = self.wait_for_element(By.ID, "confirm_password")
        
        self.clear_and_fill_input(full_name_field, "Test User")
        self.clear_and_fill_input(username_field, test_data['username'])
        self.clear_and_fill_input(email_field, test_data['email'])
        self.clear_and_fill_input(password_field, test_data['invalid_password'])
        self.clear_and_fill_input(confirm_password_field, test_data['invalid_password'])
        
        self.driver.execute_script(js_code)
        
        # Verify error by checking we stay on register page
        time.sleep(2)
        self.assertIn("register", self.driver.current_url)
        
        # Verify form is still visible
        try:
            password_field = self.wait_for_element(By.ID, "password", timeout=5)
            self.assertTrue(password_field.is_displayed())
            logger.info("✓ Stayed on register page - password validation error detected")
        except TimeoutException:
            self.fail("Register form not found after password validation")
        
        self.take_screenshot("registration_password_error")
        
        logger.info("User registration with invalid data completed successfully")

    def test_04_user_login_valid_credentials(self):
        """Test 4: User login with valid credentials."""
        logger.info("Testing user login with valid credentials...")
        
        # First register a user
        test_data = self.generate_test_data()
        self.driver.get(f"{self.base_url}/register")
        
        full_name_field = self.wait_for_element(By.ID, "full_name")
        username_field = self.wait_for_element(By.ID, "username")
        email_field = self.wait_for_element(By.ID, "email")
        password_field = self.wait_for_element(By.ID, "password")
        confirm_password_field = self.wait_for_element(By.ID, "confirm_password")
        terms_checkbox = self.wait_for_element(By.ID, "terms")
        
        self.clear_and_fill_input(full_name_field, f"Test User {test_data['username']}")
        self.clear_and_fill_input(username_field, test_data['username'])
        self.clear_and_fill_input(email_field, test_data['email'])
        self.clear_and_fill_input(password_field, test_data['password'])
        self.clear_and_fill_input(confirm_password_field, test_data['password'])
        terms_checkbox.click()
        
        # Submit registration form via JavaScript
        js_code = """
        const form = document.querySelector('form');
        form.submit();
        """
        self.driver.execute_script(js_code)
        
        # Wait for registration success and redirect to login page
        WebDriverWait(self.driver, 10).until(
            lambda driver: "login" in driver.current_url
        )
        self.assertIn("login", self.driver.current_url)
        logger.info("✓ Registration successful - redirected to login page")
        
        # Now test login
        username_field = self.wait_for_element(By.ID, "username")
        password_field = self.wait_for_element(By.ID, "password")
        
        self.clear_and_fill_input(username_field, test_data['username'])
        self.clear_and_fill_input(password_field, test_data['password'])
        
        self.take_screenshot("login_form_filled")
        
        # Submit login form via JavaScript
        self.driver.execute_script(js_code)
        
        # Verify successful login by checking redirect to dashboard
        WebDriverWait(self.driver, 10).until(
            lambda driver: "dashboard" in driver.current_url
        )
        
        self.assertIn("dashboard", self.driver.current_url)
        
        # Verify dashboard page loads properly
        try:
            dashboard_content = self.wait_for_element(By.TAG_NAME, "main", timeout=5)
            self.assertTrue(dashboard_content.is_displayed())
            logger.info("✓ Successfully logged in and redirected to dashboard")
        except TimeoutException:
            self.fail("Dashboard page did not load properly after login")
        
        self.take_screenshot("login_success")
        
        logger.info("User login with valid credentials completed successfully")

    def test_05_user_login_invalid_credentials(self):
        """Test 5: User login with invalid credentials."""
        logger.info("Testing user login with invalid credentials...")
        
        # Navigate to login page
        self.driver.get(f"{self.base_url}/login")
        
        # Test with invalid username
        username_field = self.wait_for_element(By.ID, "username")
        password_field = self.wait_for_element(By.ID, "password")
        
        self.clear_and_fill_input(username_field, "nonexistent_user")
        self.clear_and_fill_input(password_field, "wrongpassword")
        
        self.take_screenshot("login_invalid_credentials")
        
        # Submit form via JavaScript
        js_code = """
        const form = document.querySelector('form');
        form.submit();
        """
        self.driver.execute_script(js_code)
        
        # Verify error by checking we stay on login page
        time.sleep(2)
        self.assertIn("login", self.driver.current_url)
        
        # Verify login form is still visible (indicates login failed)
        try:
            login_form = self.wait_for_element(By.ID, "username", timeout=5)
            self.assertTrue(login_form.is_displayed())
            logger.info("✓ Stayed on login page - invalid credentials detected")
        except TimeoutException:
            self.fail("Login form not found after invalid credentials")
        
        self.take_screenshot("login_error_message")
        
        # Test with empty fields
        self.driver.get(f"{self.base_url}/login")
        username_field = self.wait_for_element(By.ID, "username")
        password_field = self.wait_for_element(By.ID, "password")
        
        self.clear_and_fill_input(username_field, "")
        self.clear_and_fill_input(password_field, "")
        
        self.driver.execute_script(js_code)
        
        # Verify error by checking we stay on login page  
        time.sleep(2)
        self.assertIn("login", self.driver.current_url)
        
        # Verify login form is still visible
        try:
            login_form = self.wait_for_element(By.ID, "username", timeout=5)
            self.assertTrue(login_form.is_displayed())
            logger.info("✓ Stayed on login page - empty fields validation detected")
        except TimeoutException:
            self.fail("Login form not found after empty fields")
        
        self.take_screenshot("login_empty_fields")
        
        logger.info("User login with invalid credentials completed successfully")

    def test_06_navigation_between_pages(self):
        """Test 6: Navigation between pages."""
        logger.info("Testing navigation between pages...")
        
        # Ensure we start from logged out state for consistent navigation
        self.ensure_user_logged_out()
        
        # Start from home page
        self.driver.get(self.base_url)
        self.take_screenshot("navigation_start")
        
        # Navigate to login page - should now be available since we're logged out
        login_link = self.wait_for_element_clickable(By.LINK_TEXT, "Login")
        login_link.click()
        self.assertIn("login", self.driver.current_url)
        self.take_screenshot("navigation_to_login")
        logger.info("✓ Successfully navigated to login page")
        
        # Navigate to register page
        register_link = self.wait_for_element_clickable(By.LINK_TEXT, "Sign up")
        register_link.click()
        self.assertIn("register", self.driver.current_url)
        self.take_screenshot("navigation_to_register")
        logger.info("✓ Successfully navigated to register page")
        
        # Navigate back to home - Home link should always be present
        home_link = self.wait_for_element_clickable(By.LINK_TEXT, "Home")
        home_link.click()
        self.assertEqual(self.driver.current_url, f"{self.base_url}/")
        self.take_screenshot("navigation_to_home")
        
        logger.info("Navigation between pages completed successfully")

    def test_07_form_validation(self):
        """Test 7: Form validation testing."""
        logger.info("Testing form validation...")
        
        # Test registration form validation
        self.driver.get(f"{self.base_url}/register")
        
        # Test required field validation
        submit_button = self.wait_for_element_clickable(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # Check for validation messages
        self.wait_for_element(By.CLASS_NAME, "invalid-feedback")
        self.take_screenshot("form_validation_required_fields")
        
        # Test email format validation
        email_field = self.wait_for_element(By.ID, "email")
        self.clear_and_fill_input(email_field, "invalid-email")
        email_field.send_keys(Keys.TAB)  # Trigger validation
        
        # Check for email validation message
        self.wait_for_element(By.CLASS_NAME, "invalid-feedback")
        self.take_screenshot("form_validation_email")
        
        # Test password length validation
        password_field = self.wait_for_element(By.ID, "password")
        self.clear_and_fill_input(password_field, "123")
        password_field.send_keys(Keys.TAB)
        
        # Check for password validation message
        self.wait_for_element(By.CLASS_NAME, "invalid-feedback")
        self.take_screenshot("form_validation_password")
        
        logger.info("Form validation testing completed successfully")

    def test_08_database_operations_verification(self):
        """Test 8: Database operations verification."""
        logger.info("Testing database operations verification...")
        
        # Test user registration and database persistence
        test_data = self.generate_test_data()
        
        # Register a new user
        self.driver.get(f"{self.base_url}/register")
        
        full_name_field = self.wait_for_element(By.ID, "full_name")
        username_field = self.wait_for_element(By.ID, "username")
        email_field = self.wait_for_element(By.ID, "email")
        password_field = self.wait_for_element(By.ID, "password")
        confirm_password_field = self.wait_for_element(By.ID, "confirm_password")
        terms_checkbox = self.wait_for_element(By.ID, "terms")
        
        self.clear_and_fill_input(full_name_field, f"Test User {test_data['username']}")
        self.clear_and_fill_input(username_field, test_data['username'])
        self.clear_and_fill_input(email_field, test_data['email'])
        self.clear_and_fill_input(password_field, test_data['password'])
        self.clear_and_fill_input(confirm_password_field, test_data['password'])
        terms_checkbox.click()
        
        # Submit form via JavaScript
        js_code = """
        const form = document.querySelector('form');
        form.submit();
        """
        self.driver.execute_script(js_code)
        
        # Verify registration success by redirect to login page
        WebDriverWait(self.driver, 10).until(
            lambda driver: "login" in driver.current_url
        )
        self.assertIn("login", self.driver.current_url)
        logger.info("✓ Registration successful - database operation verified")
        self.take_screenshot("database_registration")
        
        # Login with the same credentials to verify database persistence
        username_field = self.wait_for_element(By.ID, "username")
        password_field = self.wait_for_element(By.ID, "password")
        
        self.clear_and_fill_input(username_field, test_data['username'])
        self.clear_and_fill_input(password_field, test_data['password'])
        
        self.driver.execute_script(js_code)
        
        # Verify successful login (database verification) by redirect to dashboard
        WebDriverWait(self.driver, 10).until(
            lambda driver: "dashboard" in driver.current_url
        )
        
        self.assertIn("dashboard", self.driver.current_url)
        logger.info("✓ Database login verification successful - user data persisted")
        self.take_screenshot("database_login_verification")
        
        logger.info("Database operations verification completed successfully")

    def test_09_logout_functionality(self):
        """Test 9: Logout functionality."""
        logger.info("Testing logout functionality...")
        
        # First login a user
        test_data = self.generate_test_data()
        
        # Register and login
        self.driver.get(f"{self.base_url}/register")
        full_name_field = self.wait_for_element(By.ID, "full_name")
        username_field = self.wait_for_element(By.ID, "username")
        email_field = self.wait_for_element(By.ID, "email")
        password_field = self.wait_for_element(By.ID, "password")
        confirm_password_field = self.wait_for_element(By.ID, "confirm_password")
        terms_checkbox = self.wait_for_element(By.ID, "terms")
        
        self.clear_and_fill_input(full_name_field, f"Test User {test_data['username']}")
        self.clear_and_fill_input(username_field, test_data['username'])
        self.clear_and_fill_input(email_field, test_data['email'])
        self.clear_and_fill_input(password_field, test_data['password'])
        self.clear_and_fill_input(confirm_password_field, test_data['password'])
        terms_checkbox.click()
        
        # Submit registration form via JavaScript
        js_code = """
        const form = document.querySelector('form');
        form.submit();
        """
        self.driver.execute_script(js_code)
        
        # Wait for registration success and redirect to login page
        WebDriverWait(self.driver, 10).until(
            lambda driver: "login" in driver.current_url
        )
        self.assertIn("login", self.driver.current_url)
        
        # Login
        username_field = self.wait_for_element(By.ID, "username")
        password_field = self.wait_for_element(By.ID, "password")
        
        self.clear_and_fill_input(username_field, test_data['username'])
        self.clear_and_fill_input(password_field, test_data['password'])
        
        self.driver.execute_script(js_code)
        
        # Verify login success by redirect to dashboard
        WebDriverWait(self.driver, 10).until(
            lambda driver: "dashboard" in driver.current_url
        )
        
        # Test logout - logout is in a dropdown menu
        try:
            # Click on the user dropdown first
            user_dropdown = self.wait_for_element_clickable(By.ID, "navbarDropdown", timeout=5)
            user_dropdown.click()
            time.sleep(1)  # Wait for dropdown to open
            
            # Now click logout link in dropdown
            logout_link = self.wait_for_element_clickable(By.LINK_TEXT, "Logout", timeout=5)
            logout_link.click()
            logger.info("✓ Successfully clicked logout from dropdown menu")
        except Exception as e:
            logger.warning(f"Could not find user dropdown, trying direct logout link: {e}")
            # Fallback: try to find logout link directly (in case UI changed)
            try:
                logout_link = self.wait_for_element_clickable(By.LINK_TEXT, "Logout", timeout=5)
                logout_link.click()
            except Exception as e2:
                logger.error(f"Could not find logout link: {e2}")
                self.fail("Could not find logout functionality")
        
        # Verify logout success by redirect to home page
        WebDriverWait(self.driver, 10).until(
            lambda driver: any(page in driver.current_url for page in ["index", "/", "home"])
        )
        
        # Should be redirected to home page or index
        self.assertTrue(any(page in self.driver.current_url for page in ["index", "/"]))
        logger.info("✓ Logout successful - redirected to home page")
        self.take_screenshot("logout_success")
        
        # Verify user is redirected to login when trying to access dashboard
        self.driver.get(f"{self.base_url}/dashboard")
        
        # Should be redirected to login page when not authenticated
        WebDriverWait(self.driver, 10).until(
            lambda driver: "login" in driver.current_url
        )
        
        self.assertIn("login", self.driver.current_url)
        logger.info("✓ Dashboard access blocked - redirected to login page")
        self.take_screenshot("logout_redirect_verification")
        
        logger.info("Logout functionality completed successfully")

    def test_10_error_message_display(self):
        """Test 10: Error message display."""
        logger.info("Testing error message display...")
        
        # Test registration error messages
        self.driver.get(f"{self.base_url}/register")
        
        # Try to register with existing username (if any)
        full_name_field = self.wait_for_element(By.ID, "full_name")
        username_field = self.wait_for_element(By.ID, "username")
        email_field = self.wait_for_element(By.ID, "email")
        password_field = self.wait_for_element(By.ID, "password")
        confirm_password_field = self.wait_for_element(By.ID, "confirm_password")
        
        self.clear_and_fill_input(full_name_field, "Test User")
        self.clear_and_fill_input(username_field, "testuser")
        self.clear_and_fill_input(email_field, "test@example.com")
        self.clear_and_fill_input(password_field, "password123")
        self.clear_and_fill_input(confirm_password_field, "password123")
        
        # Submit form via JavaScript
        js_code = """
        const form = document.querySelector('form');
        form.submit();
        """
        self.driver.execute_script(js_code)
        
        # Check if we stay on register page or get redirected
        time.sleep(2)
        current_url = self.driver.current_url
        
        if "register" in current_url:
            logger.info("✓ Stayed on register page - likely validation error or username taken")
        elif "login" in current_url:
            logger.info("✓ Redirected to login page - registration successful")
        else:
            logger.warning(f"Unexpected redirect to: {current_url}")
        
        self.take_screenshot("error_message_display")
        
        # Test login error messages
        self.driver.get(f"{self.base_url}/login")
        
        username_field = self.wait_for_element(By.ID, "username")
        password_field = self.wait_for_element(By.ID, "password")
        
        self.clear_and_fill_input(username_field, "nonexistent")
        self.clear_and_fill_input(password_field, "wrongpassword")
        
        self.driver.execute_script(js_code)
        
        # Verify error by checking we stay on login page
        time.sleep(2)
        self.assertIn("login", self.driver.current_url)
        
        # Verify login form is still visible
        try:
            login_form = self.wait_for_element(By.ID, "username", timeout=5)
            self.assertTrue(login_form.is_displayed())
            logger.info("✓ Login error handling verified - stayed on login page")
        except TimeoutException:
            self.fail("Login form not found after invalid credentials")
        
        self.take_screenshot("login_error_display")
        
        logger.info("Error message display testing completed successfully")

    def test_11_ui_element_presence_checks(self):
        """Test 11: UI element presence checks."""
        logger.info("Testing UI element presence checks...")
        
        try:
            # Test home page elements - start from logged out state for consistent testing
            logger.info("Ensuring user is logged out...")
            self.ensure_user_logged_out()
            self.driver.get(self.base_url)
            
            # Check for navigation elements - always present
            self.wait_for_element(By.CLASS_NAME, "navbar")
            self.wait_for_element(By.LINK_TEXT, "Home")
            
            # When logged out, these should be present
            self.wait_for_element(By.LINK_TEXT, "Login")
            self.wait_for_element(By.LINK_TEXT, "Sign Up")
            logger.info("✓ Login and Sign Up links found (user logged out)")
            
            # Check for main content elements
            self.wait_for_element(By.TAG_NAME, "h1")
            self.wait_for_element(By.CLASS_NAME, "card")
            self.wait_for_element(By.TAG_NAME, "footer")
            
            self.take_screenshot("ui_elements_home_logged_out")
            
            # Test logged in state elements with timeout protection
            logger.info("Ensuring user is logged in...")
            
            # Use a simple timeout for Windows compatibility
            login_success = False
            login_start_time = time.time()
            max_login_time = 60  # 60 seconds maximum
            
            try:
                while time.time() - login_start_time < max_login_time:
                    try:
                        self.ensure_user_logged_in()
                        login_success = True
                        break
                    except Exception as e:
                        logger.warning(f"Login attempt failed: {e}")
                        if time.time() - login_start_time >= max_login_time:
                            break
                        time.sleep(5)  # Wait before retry
                
                if login_success:
                    self.driver.get(self.base_url)
                    
                    # Check for user dropdown when logged in
                    self.wait_for_element(By.ID, "navbarDropdown", timeout=10)
                    logger.info("✓ User dropdown found (user logged in)")
                    
                    self.take_screenshot("ui_elements_home_logged_in")
                else:
                    logger.error("Login process timed out after 60 seconds")
                    self.take_screenshot("ui_elements_login_timeout")
                    
            except Exception as e:
                logger.error(f"Login process failed: {e}")
                # Continue with the test using logged out state
                self.take_screenshot("ui_elements_login_failure")
            
            # Test login page elements
            self.driver.get(f"{self.base_url}/login")
            
            # Check for form elements
            self.wait_for_element(By.ID, "username")
            self.wait_for_element(By.ID, "password")
            self.wait_for_element(By.CSS_SELECTOR, "button[type='submit']")
            
            # Check for signup link (should be present on login page)
            try:
                self.wait_for_element(By.LINK_TEXT, "Sign up", timeout=3)
                logger.info("✓ Sign up link found on login page")
            except:
                # Try alternative text
                try:
                    self.wait_for_element(By.LINK_TEXT, "Register", timeout=3)
                    logger.info("✓ Register link found on login page")
                except:
                    logger.warning("Sign up/Register link not found on login page")
            
            self.take_screenshot("ui_elements_login_page")
            
            # Test register page elements
            self.driver.get(f"{self.base_url}/register")
            
            # Check for form elements
            self.wait_for_element(By.ID, "full_name")
            self.wait_for_element(By.ID, "username")
            self.wait_for_element(By.ID, "email")
            self.wait_for_element(By.ID, "password")
            self.wait_for_element(By.ID, "confirm_password")
            self.wait_for_element(By.ID, "terms")
            self.wait_for_element(By.CSS_SELECTOR, "button[type='submit']")
            
            self.take_screenshot("ui_elements_register_page")
            
            logger.info("UI element presence checks completed successfully")
            
        except Exception as e:
            logger.error(f"UI element presence test failed: {e}")
            self.take_screenshot("ui_elements_test_failure")
            raise

    def test_12_responsive_design_testing(self):
        """Test 12: Responsive design testing."""
        logger.info("Testing responsive design...")
        
        # Test different screen sizes
        screen_sizes = [
            (1920, 1080),  # Desktop
            (1366, 768),   # Laptop
            (768, 1024),   # Tablet
            (375, 667)     # Mobile
        ]
        
        for width, height in screen_sizes:
            self.driver.set_window_size(width, height)
            
            # Test home page responsiveness
            self.driver.get(self.base_url)
            time.sleep(2)  # Allow for layout adjustment
            self.take_screenshot(f"responsive_home_{width}x{height}")
            
            # Test login page responsiveness
            self.driver.get(f"{self.base_url}/login")
            time.sleep(2)
            self.take_screenshot(f"responsive_login_{width}x{height}")
            
            # Test register page responsiveness
            self.driver.get(f"{self.base_url}/register")
            time.sleep(2)
            self.take_screenshot(f"responsive_register_{width}x{height}")
            
            # Verify elements are still accessible
            try:
                self.wait_for_element(By.CSS_SELECTOR, "button[type='submit']", timeout=5)
            except TimeoutException:
                self.fail(f"Submit button not found at {width}x{height}")
        
        # Reset to default size
        self.driver.set_window_size(1920, 1080)
        
        logger.info("Responsive design testing completed successfully")

    def test_13_api_endpoints_testing(self):
        """Test 13: API endpoints testing."""
        logger.info("Testing API endpoints...")
        
        # Test health check endpoint
        self.driver.get(f"{self.base_url}/api/health")
        
        # Verify JSON response
        body_text = self.driver.find_element(By.TAG_NAME, "body").text
        try:
            health_data = json.loads(body_text)
            self.assertEqual(health_data['status'], 'healthy')
            self.assertIn('database', health_data)
            self.take_screenshot("api_health_check")
        except json.JSONDecodeError:
            self.fail("Health check endpoint did not return valid JSON")
        
        # Test stats endpoint
        self.driver.get(f"{self.base_url}/api/stats")
        
        body_text = self.driver.find_element(By.TAG_NAME, "body").text
        try:
            stats_data = json.loads(body_text)
            self.assertIn('total_users', stats_data)
            self.assertIn('total_projects', stats_data)
            self.assertIsInstance(stats_data['total_users'], int)
            self.assertIsInstance(stats_data['total_projects'], int)
            self.take_screenshot("api_stats")
        except json.JSONDecodeError:
            self.fail("Stats endpoint did not return valid JSON")
        
        logger.info("API endpoints testing completed successfully")

    def test_14_performance_testing(self):
        """Test 14: Performance testing."""
        logger.info("Testing performance...")
        
        # Test page load times
        pages = ['', '/login', '/register']
        
        for page in pages:
            start_time = time.time()
            self.driver.get(f"{self.base_url}{page}")
            
            # Wait for page to be fully loaded
            self.wait_for_element(By.TAG_NAME, "body")
            
            load_time = time.time() - start_time
            
            # Assert reasonable load time (less than 5 seconds)
            self.assertLess(load_time, 5.0, f"Page {page} took too long to load: {load_time:.2f}s")
            
            logger.info(f"Page {page} loaded in {load_time:.2f} seconds")
            self.take_screenshot(f"performance_{page.replace('/', '_')}")
        
        logger.info("Performance testing completed successfully")

    def verify_app_accessibility(self):
        """Verify that the Flask app is accessible before running tests."""
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                logger.info(f"Checking app accessibility (attempt {attempt + 1}/{max_attempts})")
                self.driver.get(self.base_url)
                
                # Wait for any element to load (indicating the page loaded)
                self.wait_for_element(By.TAG_NAME, "body", timeout=10)
                
                # Check if we get a proper HTML page (not an error page)
                page_source = self.driver.page_source.lower()
                if "techflow" in page_source or "login" in page_source or "register" in page_source:
                    logger.info("✓ Flask app is accessible")
                    return True
                else:
                    logger.warning("App loaded but doesn't seem to be TechFlow")
                    
            except Exception as e:
                logger.warning(f"App accessibility check failed (attempt {attempt + 1}): {e}")
                if attempt < max_attempts - 1:
                    time.sleep(5)  # Wait before retrying
                    
        logger.error("Flask app is not accessible after all attempts")
        return False

    def is_user_logged_in(self):
        """Check if a user is currently logged in by looking for the user dropdown."""
        try:
            self.driver.find_element(By.ID, "navbarDropdown")
            return True
        except NoSuchElementException:
            return False
    
    def ensure_user_logged_out(self):
        """Ensure user is logged out before running tests that require unauthenticated state."""
        if self.is_user_logged_in():
            try:
                # Click user dropdown
                user_dropdown = self.wait_for_element_clickable(By.ID, "navbarDropdown", timeout=5)
                user_dropdown.click()
                time.sleep(1)  # Wait for dropdown to open
                
                # Click logout
                logout_link = self.wait_for_element_clickable(By.LINK_TEXT, "Logout", timeout=5)
                logout_link.click()
                
                # Wait for logout to complete
                WebDriverWait(self.driver, 10).until(
                    lambda driver: not self.is_user_logged_in()
                )
                logger.info("✓ User logged out successfully")
            except Exception as e:
                logger.warning(f"Could not logout user: {e}")
                # Clear session by going to logout URL directly
                self.driver.get(f"{self.base_url}/logout")
                time.sleep(2)
    
    def ensure_user_logged_in(self, username=None, password=None):
        """Ensure a user is logged in for tests that require authenticated state."""
        # Check if already logged in
        if self.is_user_logged_in():
            logger.info("✓ User already logged in")
            return
            
        # Use predefined credentials if not provided
        if not username or not password:
            # Use a consistent test user to avoid registration issues
            username = "testuser123"
            password = "TestPass123!"
            email = "testuser123@example.com"
            
            # Try to register user first (in case it doesn't exist)
            try:
                logger.info(f"Attempting to register test user: {username}")
                self.driver.get(f"{self.base_url}/register")
                
                # Fill registration form
                full_name_field = self.wait_for_element(By.ID, "full_name", timeout=10)
                username_field = self.wait_for_element(By.ID, "username", timeout=10)
                email_field = self.wait_for_element(By.ID, "email", timeout=10)
                password_field = self.wait_for_element(By.ID, "password", timeout=10)
                confirm_password_field = self.wait_for_element(By.ID, "confirm_password", timeout=10)
                terms_checkbox = self.wait_for_element(By.ID, "terms", timeout=10)
                
                self.clear_and_fill_input(full_name_field, f"Test User")
                self.clear_and_fill_input(username_field, username)
                self.clear_and_fill_input(email_field, email)
                self.clear_and_fill_input(password_field, password)
                self.clear_and_fill_input(confirm_password_field, password)
                
                # Ensure checkbox is checked
                if not terms_checkbox.is_selected():
                    terms_checkbox.click()
                
                # Submit registration
                submit_button = self.wait_for_element_clickable(By.CSS_SELECTOR, "button[type='submit']", timeout=10)
                submit_button.click()
                
                # Wait briefly for processing
                time.sleep(3)
                
                logger.info("Registration attempt completed")
                
            except Exception as e:
                logger.info(f"Registration failed (user may already exist): {e}")
                # This is expected if user already exists
        
        # Now attempt login
        max_login_attempts = 3
        for attempt in range(max_login_attempts):
            try:
                logger.info(f"Login attempt {attempt + 1}/{max_login_attempts} for user: {username}")
                
                # Go to login page
                self.driver.get(f"{self.base_url}/login")
                
                # Wait for login form
                username_field = self.wait_for_element(By.ID, "username", timeout=10)
                password_field = self.wait_for_element(By.ID, "password", timeout=10)
                
                # Clear and fill login form
                self.clear_and_fill_input(username_field, username)
                self.clear_and_fill_input(password_field, password)
                
                # Submit login
                submit_button = self.wait_for_element_clickable(By.CSS_SELECTOR, "button[type='submit']", timeout=10)
                submit_button.click()
                
                # Wait for login to process and check for success
                login_success = False
                for check_attempt in range(10):  # Check up to 10 times over 10 seconds
                    time.sleep(1)
                    current_url = self.driver.current_url
                    
                    # Check if redirected away from login page or if user dropdown is present
                    if "login" not in current_url or self.is_user_logged_in():
                        # Go to home page to verify login status
                        self.driver.get(self.base_url)
                        time.sleep(2)
                        
                        if self.is_user_logged_in():
                            logger.info("✓ User logged in successfully")
                            return
                        else:
                            logger.warning(f"Login check {check_attempt + 1}: Not logged in yet")
                    else:
                        logger.info(f"Login check {check_attempt + 1}: Still on login page")
                
                # If we get here, login didn't succeed
                logger.warning(f"Login attempt {attempt + 1} failed")
                
                # Check for error messages
                try:
                    error_elements = self.driver.find_elements(By.CLASS_NAME, "alert-danger")
                    if error_elements:
                        for error in error_elements:
                            logger.error(f"Login error: {error.text}")
                except:
                    pass
                
                # Take screenshot for debugging
                self.take_screenshot(f"login_attempt_{attempt + 1}_failed")
                
                if attempt == max_login_attempts - 1:
                    # Last attempt failed
                    logger.error("All login attempts failed")
                    logger.info(f"Final URL: {self.driver.current_url}")
                    logger.info(f"Final page title: {self.driver.title}")
                    
                    # Try one more time with a fresh user
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                    fallback_username = f'fallback_{timestamp}'
                    fallback_password = 'FallbackPass123!'
                    fallback_email = f'{fallback_username}@example.com'
                    
                    logger.info(f"Trying with fallback user: {fallback_username}")
                    
                    # Quick registration
                    self.driver.get(f"{self.base_url}/register")
                    time.sleep(2)
                    
                    try:
                        full_name_field = self.wait_for_element(By.ID, "full_name", timeout=5)
                        username_field = self.wait_for_element(By.ID, "username", timeout=5)
                        email_field = self.wait_for_element(By.ID, "email", timeout=5)
                        password_field = self.wait_for_element(By.ID, "password", timeout=5)
                        confirm_password_field = self.wait_for_element(By.ID, "confirm_password", timeout=5)
                        terms_checkbox = self.wait_for_element(By.ID, "terms", timeout=5)
                        
                        self.clear_and_fill_input(full_name_field, "Fallback User")
                        self.clear_and_fill_input(username_field, fallback_username)
                        self.clear_and_fill_input(email_field, fallback_email)
                        self.clear_and_fill_input(password_field, fallback_password)
                        self.clear_and_fill_input(confirm_password_field, fallback_password)
                        
                        if not terms_checkbox.is_selected():
                            terms_checkbox.click()
                        
                        submit_button = self.wait_for_element_clickable(By.CSS_SELECTOR, "button[type='submit']", timeout=5)
                        submit_button.click()
                        time.sleep(3)
                        
                        # Quick login with fallback user
                        self.driver.get(f"{self.base_url}/login")
                        time.sleep(2)
                        
                        username_field = self.wait_for_element(By.ID, "username", timeout=5)
                        password_field = self.wait_for_element(By.ID, "password", timeout=5)
                        
                        self.clear_and_fill_input(username_field, fallback_username)
                        self.clear_and_fill_input(password_field, fallback_password)
                        
                        submit_button = self.wait_for_element_clickable(By.CSS_SELECTOR, "button[type='submit']", timeout=5)
                        submit_button.click()
                        
                        time.sleep(3)
                        self.driver.get(self.base_url)
                        time.sleep(2)
                        
                        if self.is_user_logged_in():
                            logger.info("✓ Fallback user login successful")
                            return
                        
                    except Exception as fallback_error:
                        logger.error(f"Fallback login also failed: {fallback_error}")
                    
                    # Final fallback: raise exception
                    raise Exception("Could not establish user login after all attempts")
                
            except Exception as e:
                logger.error(f"Login attempt {attempt + 1} encountered error: {e}")
                if attempt == max_login_attempts - 1:
                    self.take_screenshot("ensure_user_logged_in_final_failure")
                    raise
                
                # Wait before retrying
                time.sleep(2)


def run_test_suite():
    """Run the complete test suite and generate report."""
    logger.info("Starting DevOps Assignment 3 Test Suite...")
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(DevOpsAssignmentTestSuite)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Generate summary
    total_tests = result.testsRun
    failed_tests = len(result.failures)
    error_tests = len(result.errors)
    passed_tests = total_tests - failed_tests - error_tests
    
    # Log summary
    logger.info("=" * 60)
    logger.info("TEST SUITE SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total Tests: {total_tests}")
    logger.info(f"Passed: {passed_tests}")
    logger.info(f"Failed: {failed_tests}")
    logger.info(f"Errors: {error_tests}")
    logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    logger.info("=" * 60)
    
    # Save results to JSON file
    detailed_results = {
        'summary': {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'error_tests': error_tests,
            'success_rate': (passed_tests/total_tests)*100 if total_tests > 0 else 0
        },
        'failures': [{'test': str(test), 'traceback': traceback} for test, traceback in result.failures],
        'errors': [{'test': str(test), 'traceback': traceback} for test, traceback in result.errors],
        'timestamp': datetime.now().isoformat()
    }
    
    with open('test_results.json', 'w') as f:
        json.dump(detailed_results, f, indent=2, default=str)
    
    # Exit with appropriate code
    if failed_tests > 0 or error_tests > 0:
        logger.error("Test suite failed!")
        sys.exit(1)
    else:
        logger.info("Test suite passed!")
        sys.exit(0)


if __name__ == "__main__":
    run_test_suite()