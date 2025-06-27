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
        logging.FileHandler('test_execution.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Add file handler for detailed test results
test_results_logger = logging.getLogger('test_results')
test_results_logger.setLevel(logging.INFO)
fh = logging.FileHandler('test_results_detailed.log')
fh.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
test_results_logger.addHandler(fh)

# Add file handler for error-only logging
error_logger = logging.getLogger('error_logger')
error_logger.setLevel(logging.ERROR)
error_fh = logging.FileHandler('detailed_errors.log')
error_fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
error_logger.addHandler(error_fh)

# Also log errors to the main logger
def log_error(message):
    """Log error to both main logger and error logger."""
    logger.error(message)
    error_logger.error(message)

class DevOpsAssignmentTestSuite(unittest.TestCase):
    """Main test suite for DevOps Assignment 3 web application."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests."""
        logger.info("Setting up test environment...")
        test_results_logger.info("=" * 80)
        test_results_logger.info("TEST ENVIRONMENT SETUP")
        test_results_logger.info("=" * 80)
        
        # Test configuration
        cls.base_url = "http://localhost:5000"
        cls.test_results = []
        cls.screenshots_dir = "screenshots"
        
        test_results_logger.info(f"Base URL: {cls.base_url}")
        test_results_logger.info(f"Screenshots directory: {cls.screenshots_dir}")
        
        # Create screenshots directory
        if not os.path.exists(cls.screenshots_dir):
            os.makedirs(cls.screenshots_dir)
            test_results_logger.info("Created screenshots directory")
        
        # Test connection to web application
        logger.info(f"Testing connection to web application at {cls.base_url}")
        test_results_logger.info("Testing web application connectivity...")
        try:
            response = requests.get(f"{cls.base_url}/api/health", timeout=10)
            logger.info(f"Health check response: {response.status_code} - {response.text}")
            test_results_logger.info(f"Health check response: {response.status_code} - {response.text}")
            if response.status_code != 200:
                logger.error(f"Health check failed with status code: {response.status_code}")
                test_results_logger.error(f"Health check failed with status code: {response.status_code}")
                raise Exception(f"Web application health check failed: {response.status_code}")
            test_results_logger.info("✓ Web application connectivity successful")
        except Exception as e:
            logger.error(f"Failed to connect to web application: {e}")
            test_results_logger.error(f"Failed to connect to web application: {e}")
            log_error(f"Failed to connect to web application: {e}")
            logger.error("Please ensure the Flask application is running on the EC2 instance")
            test_results_logger.error("Please ensure the Flask application is running on the EC2 instance")
            raise
        
        # Chrome options for headless testing
        test_results_logger.info("Setting up Chrome WebDriver...")
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        test_results_logger.info("Chrome options configured")
        
        # Use webdriver-manager to handle ChromeDriver
        try:
            test_results_logger.info("Installing ChromeDriver...")
            driver_path = ChromeDriverManager().install()
            logger.info(f"ChromeDriver path: {driver_path}")
            test_results_logger.info(f"ChromeDriver path: {driver_path}")
            
            # Find the real chromedriver executable
            base_dir = os.path.dirname(driver_path)
            logger.info(f"Base directory: {base_dir}")
            test_results_logger.info(f"Base directory: {base_dir}")
            
            # The actual chromedriver is usually in a subdirectory
            # Look for directories that might contain the executable
            actual_driver_path = None
            
            # First, check if we're already in the right directory
            if os.path.basename(driver_path) == 'chromedriver' and os.access(driver_path, os.X_OK):
                actual_driver_path = driver_path
                logger.info(f"Found chromedriver executable: {actual_driver_path}")
                test_results_logger.info(f"Found chromedriver executable: {actual_driver_path}")
            else:
                # Look for subdirectories
                for item in os.listdir(base_dir):
                    item_path = os.path.join(base_dir, item)
                    if os.path.isdir(item_path):
                        logger.info(f"Checking subdirectory: {item_path}")
                        test_results_logger.info(f"Checking subdirectory: {item_path}")
                        # Look for chromedriver executable in this subdirectory
                        for file in os.listdir(item_path):
                            if file == 'chromedriver':
                                candidate = os.path.join(item_path, file)
                                if os.access(candidate, os.X_OK):
                                    actual_driver_path = candidate
                                    logger.info(f"Found chromedriver executable: {actual_driver_path}")
                                    test_results_logger.info(f"Found chromedriver executable: {actual_driver_path}")
                                    break
                        if actual_driver_path:
                            break
            
            if not actual_driver_path:
                logger.error("Could not find a valid chromedriver executable!")
                test_results_logger.error("Could not find a valid chromedriver executable!")
                log_error("Could not find a valid chromedriver executable!")
                logger.error(f"Available files in {base_dir}:")
                for item in os.listdir(base_dir):
                    item_path = os.path.join(base_dir, item)
                    if os.path.isdir(item_path):
                        logger.error(f"  Directory: {item}")
                        try:
                            for subitem in os.listdir(item_path):
                                logger.error(f"    - {subitem}")
                        except:
                            logger.error(f"    - (cannot list contents)")
                    else:
                        logger.error(f"  File: {item}")
                raise Exception("No valid chromedriver executable found")
            
            service = Service(actual_driver_path)
            logger.info("ChromeDriver installed successfully")
            test_results_logger.info("✓ ChromeDriver installed successfully")
        except Exception as e:
            logger.error(f"Failed to install ChromeDriver: {e}")
            test_results_logger.error(f"Failed to install ChromeDriver: {e}")
            log_error(f"Failed to install ChromeDriver: {e}")
            raise
        
        # Initialize WebDriver
        try:
            test_results_logger.info("Initializing WebDriver...")
            cls.driver = webdriver.Chrome(service=service, options=chrome_options)
            cls.driver.implicitly_wait(10)
            cls.wait = WebDriverWait(cls.driver, 10)
            logger.info("WebDriver initialized successfully")
            test_results_logger.info("✓ WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            test_results_logger.error(f"Failed to initialize WebDriver: {e}")
            log_error(f"Failed to initialize WebDriver: {e}")
            raise
        
        logger.info("Test environment setup completed")
        test_results_logger.info("✓ Test environment setup completed")
        test_results_logger.info("=" * 80)
    
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
            test_results_logger.error(f"TEST FAILED: {self._testMethodName}")
            test_results_logger.error(f"Screenshot saved: {screenshot_path}")
            
            # Log the actual error details
            if hasattr(self, '_outcome'):
                for test, traceback in self._outcome.errors:
                    test_results_logger.error(f"Error in {test}: {traceback}")
                for test, traceback in self._outcome.failures:
                    test_results_logger.error(f"Failure in {test}: {traceback}")
        else:
            test_results_logger.info(f"TEST PASSED: {self._testMethodName}")
        
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
        test_results_logger.info(f"Test duration: {test_duration:.2f}s")
    
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
    
    def wait_for_text_present(self, text, timeout=10):
        """Wait for text to be present in page."""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{text}')]"))
        )
    
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
        
        logger.info("Page load verification completed successfully")

    def test_02_user_registration_valid_data(self):
        """Test 2: User registration with valid data."""
        logger.info("Testing user registration with valid data...")
        
        test_data = self.generate_test_data()
        
        # Navigate to registration page
        self.driver.get(f"{self.base_url}/register")
        
        # Fill registration form
        username_field = self.wait_for_element(By.ID, "username")
        email_field = self.wait_for_element(By.ID, "email")
        password_field = self.wait_for_element(By.ID, "password")
        confirm_password_field = self.wait_for_element(By.ID, "confirm_password")
        terms_checkbox = self.wait_for_element(By.ID, "terms")
        
        self.clear_and_fill_input(username_field, test_data['username'])
        self.clear_and_fill_input(email_field, test_data['email'])
        self.clear_and_fill_input(password_field, test_data['password'])
        self.clear_and_fill_input(confirm_password_field, test_data['password'])
        terms_checkbox.click()
        
        self.take_screenshot("registration_form_filled")
        
        # Submit form
        submit_button = self.wait_for_element_clickable(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # Verify successful registration
        self.wait_for_text_present("Registration successful")
        self.assertIn("login", self.driver.current_url)
        self.take_screenshot("registration_success")
        
        logger.info("User registration with valid data completed successfully")

    def test_03_user_registration_invalid_data(self):
        """Test 3: User registration with invalid data."""
        logger.info("Testing user registration with invalid data...")
        
        test_data = self.generate_test_data()
        
        # Navigate to registration page
        self.driver.get(f"{self.base_url}/register")
        
        # Test with invalid username (too short)
        username_field = self.wait_for_element(By.ID, "username")
        email_field = self.wait_for_element(By.ID, "email")
        password_field = self.wait_for_element(By.ID, "password")
        confirm_password_field = self.wait_for_element(By.ID, "confirm_password")
        
        self.clear_and_fill_input(username_field, test_data['invalid_username'])
        self.clear_and_fill_input(email_field, test_data['email'])
        self.clear_and_fill_input(password_field, test_data['password'])
        self.clear_and_fill_input(confirm_password_field, test_data['password'])
        
        self.take_screenshot("registration_invalid_username")
        
        # Submit form
        submit_button = self.wait_for_element_clickable(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # Verify error message
        self.wait_for_text_present("Username must be at least 3 characters long")
        self.take_screenshot("registration_username_error")
        
        # Test with invalid email
        self.clear_and_fill_input(username_field, test_data['username'])
        self.clear_and_fill_input(email_field, test_data['invalid_email'])
        submit_button.click()
        
        # Verify error message
        self.wait_for_text_present("Please enter a valid email address")
        self.take_screenshot("registration_email_error")
        
        # Test with invalid password (too short)
        self.clear_and_fill_input(email_field, test_data['email'])
        self.clear_and_fill_input(password_field, test_data['invalid_password'])
        submit_button.click()
        
        # Verify error message
        self.wait_for_text_present("Password must be at least 8 characters long")
        self.take_screenshot("registration_password_error")
        
        logger.info("User registration with invalid data completed successfully")

    def test_04_user_login_valid_credentials(self):
        """Test 4: User login with valid credentials."""
        logger.info("Testing user login with valid credentials...")
        
        # First register a user
        test_data = self.generate_test_data()
        self.driver.get(f"{self.base_url}/register")
        
        username_field = self.wait_for_element(By.ID, "username")
        email_field = self.wait_for_element(By.ID, "email")
        password_field = self.wait_for_element(By.ID, "password")
        confirm_password_field = self.wait_for_element(By.ID, "confirm_password")
        terms_checkbox = self.wait_for_element(By.ID, "terms")
        
        self.clear_and_fill_input(username_field, test_data['username'])
        self.clear_and_fill_input(email_field, test_data['email'])
        self.clear_and_fill_input(password_field, test_data['password'])
        self.clear_and_fill_input(confirm_password_field, test_data['password'])
        terms_checkbox.click()
        
        submit_button = self.wait_for_element_clickable(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # Wait for registration success and redirect to login
        self.wait_for_text_present("Registration successful")
        
        # Now test login
        username_field = self.wait_for_element(By.ID, "username")
        password_field = self.wait_for_element(By.ID, "password")
        
        self.clear_and_fill_input(username_field, test_data['username'])
        self.clear_and_fill_input(password_field, test_data['password'])
        
        self.take_screenshot("login_form_filled")
        
        # Submit login form
        submit_button = self.wait_for_element_clickable(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # Verify successful login
        self.wait_for_text_present(f"Welcome back, {test_data['username']}")
        self.assertIn("dashboard", self.driver.current_url)
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
        
        # Submit form
        submit_button = self.wait_for_element_clickable(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # Verify error message
        self.wait_for_text_present("Invalid username or password")
        self.take_screenshot("login_error_message")
        
        # Test with empty fields
        self.clear_and_fill_input(username_field, "")
        self.clear_and_fill_input(password_field, "")
        submit_button.click()
        
        # Verify error message
        self.wait_for_text_present("Please enter both username and password")
        self.take_screenshot("login_empty_fields")
        
        logger.info("User login with invalid credentials completed successfully")

    def test_06_navigation_between_pages(self):
        """Test 6: Navigation between pages."""
        logger.info("Testing navigation between pages...")
        
        # Start from home page
        self.driver.get(self.base_url)
        self.take_screenshot("navigation_start")
        
        # Navigate to login page
        login_link = self.wait_for_element_clickable(By.LINK_TEXT, "Login")
        login_link.click()
        self.assertIn("login", self.driver.current_url)
        self.take_screenshot("navigation_to_login")
        
        # Navigate to register page
        register_link = self.wait_for_element_clickable(By.LINK_TEXT, "Sign up")
        register_link.click()
        self.assertIn("register", self.driver.current_url)
        self.take_screenshot("navigation_to_register")
        
        # Navigate back to home
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
        
        username_field = self.wait_for_element(By.ID, "username")
        email_field = self.wait_for_element(By.ID, "email")
        password_field = self.wait_for_element(By.ID, "password")
        confirm_password_field = self.wait_for_element(By.ID, "confirm_password")
        terms_checkbox = self.wait_for_element(By.ID, "terms")
        
        self.clear_and_fill_input(username_field, test_data['username'])
        self.clear_and_fill_input(email_field, test_data['email'])
        self.clear_and_fill_input(password_field, test_data['password'])
        self.clear_and_fill_input(confirm_password_field, test_data['password'])
        terms_checkbox.click()
        
        submit_button = self.wait_for_element_clickable(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # Verify registration success
        self.wait_for_text_present("Registration successful")
        self.take_screenshot("database_registration")
        
        # Login with the same credentials to verify database persistence
        username_field = self.wait_for_element(By.ID, "username")
        password_field = self.wait_for_element(By.ID, "password")
        
        self.clear_and_fill_input(username_field, test_data['username'])
        self.clear_and_fill_input(password_field, test_data['password'])
        
        submit_button = self.wait_for_element_clickable(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # Verify successful login (database verification)
        self.wait_for_text_present(f"Welcome back, {test_data['username']}")
        self.assertIn("dashboard", self.driver.current_url)
        self.take_screenshot("database_login_verification")
        
        logger.info("Database operations verification completed successfully")

    def test_09_logout_functionality(self):
        """Test 9: Logout functionality."""
        logger.info("Testing logout functionality...")
        
        # First login a user
        test_data = self.generate_test_data()
        
        # Register and login
        self.driver.get(f"{self.base_url}/register")
        username_field = self.wait_for_element(By.ID, "username")
        email_field = self.wait_for_element(By.ID, "email")
        password_field = self.wait_for_element(By.ID, "password")
        confirm_password_field = self.wait_for_element(By.ID, "confirm_password")
        terms_checkbox = self.wait_for_element(By.ID, "terms")
        
        self.clear_and_fill_input(username_field, test_data['username'])
        self.clear_and_fill_input(email_field, test_data['email'])
        self.clear_and_fill_input(password_field, test_data['password'])
        self.clear_and_fill_input(confirm_password_field, test_data['password'])
        terms_checkbox.click()
        
        submit_button = self.wait_for_element_clickable(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # Login
        username_field = self.wait_for_element(By.ID, "username")
        password_field = self.wait_for_element(By.ID, "password")
        
        self.clear_and_fill_input(username_field, test_data['username'])
        self.clear_and_fill_input(password_field, test_data['password'])
        
        submit_button = self.wait_for_element_clickable(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # Verify login success
        self.wait_for_text_present(f"Welcome back, {test_data['username']}")
        
        # Test logout
        logout_link = self.wait_for_element_clickable(By.LINK_TEXT, "Logout")
        logout_link.click()
        
        # Verify logout success
        self.wait_for_text_present("You have been logged out successfully")
        self.assertIn("index", self.driver.current_url)
        self.take_screenshot("logout_success")
        
        # Verify user is redirected to login when trying to access dashboard
        self.driver.get(f"{self.base_url}/dashboard")
        self.wait_for_text_present("Please login to access the dashboard")
        self.take_screenshot("logout_redirect_verification")
        
        logger.info("Logout functionality completed successfully")

    def test_10_error_message_display(self):
        """Test 10: Error message display."""
        logger.info("Testing error message display...")
        
        # Test registration error messages
        self.driver.get(f"{self.base_url}/register")
        
        # Try to register with existing username (if any)
        username_field = self.wait_for_element(By.ID, "username")
        email_field = self.wait_for_element(By.ID, "email")
        password_field = self.wait_for_element(By.ID, "password")
        confirm_password_field = self.wait_for_element(By.ID, "confirm_password")
        
        self.clear_and_fill_input(username_field, "testuser")
        self.clear_and_fill_input(email_field, "test@example.com")
        self.clear_and_fill_input(password_field, "password123")
        self.clear_and_fill_input(confirm_password_field, "password123")
        
        submit_button = self.wait_for_element_clickable(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # Check for error message display
        try:
            error_element = self.wait_for_element(By.CLASS_NAME, "alert-danger", timeout=5)
            self.assertTrue(error_element.is_displayed())
            self.take_screenshot("error_message_display")
        except TimeoutException:
            # No error message means username is available
            pass
        
        # Test login error messages
        self.driver.get(f"{self.base_url}/login")
        
        username_field = self.wait_for_element(By.ID, "username")
        password_field = self.wait_for_element(By.ID, "password")
        
        self.clear_and_fill_input(username_field, "nonexistent")
        self.clear_and_fill_input(password_field, "wrongpassword")
        
        submit_button = self.wait_for_element_clickable(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # Verify error message
        error_element = self.wait_for_element(By.CLASS_NAME, "alert-danger")
        self.assertTrue(error_element.is_displayed())
        self.assertIn("Invalid username or password", error_element.text)
        self.take_screenshot("login_error_display")
        
        logger.info("Error message display testing completed successfully")

    def test_11_ui_element_presence_checks(self):
        """Test 11: UI element presence checks."""
        logger.info("Testing UI element presence checks...")
        
        # Test home page elements
        self.driver.get(self.base_url)
        
        # Check for navigation elements
        self.wait_for_element(By.CLASS_NAME, "navbar")
        self.wait_for_element(By.LINK_TEXT, "Home")
        self.wait_for_element(By.LINK_TEXT, "Login")
        self.wait_for_element(By.LINK_TEXT, "Sign Up")
        
        # Check for main content elements
        self.wait_for_element(By.TAG_NAME, "h1")
        self.wait_for_element(By.CLASS_NAME, "card")
        self.wait_for_element(By.TAG_NAME, "footer")
        
        self.take_screenshot("ui_elements_home")
        
        # Test login page elements
        self.driver.get(f"{self.base_url}/login")
        
        # Check for form elements
        self.wait_for_element(By.ID, "username")
        self.wait_for_element(By.ID, "password")
        self.wait_for_element(By.CSS_SELECTOR, "button[type='submit']")
        self.wait_for_element(By.LINK_TEXT, "Sign up")
        
        self.take_screenshot("ui_elements_login")
        
        # Test register page elements
        self.driver.get(f"{self.base_url}/register")
        
        # Check for form elements
        self.wait_for_element(By.ID, "username")
        self.wait_for_element(By.ID, "email")
        self.wait_for_element(By.ID, "password")
        self.wait_for_element(By.ID, "confirm_password")
        self.wait_for_element(By.ID, "terms")
        self.wait_for_element(By.CSS_SELECTOR, "button[type='submit']")
        self.wait_for_element(By.LINK_TEXT, "Sign in")
        
        self.take_screenshot("ui_elements_register")
        
        logger.info("UI element presence checks completed successfully")

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


def run_test_suite():
    """Run the complete test suite and generate report."""
    logger.info("Starting DevOps Assignment 3 Test Suite...")
    test_results_logger.info("=" * 80)
    test_results_logger.info("STARTING TEST SUITE EXECUTION")
    test_results_logger.info("=" * 80)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(DevOpsAssignmentTestSuite)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=3, stream=sys.stdout)
    result = runner.run(suite)
    
    # Generate summary
    total_tests = result.testsRun
    failed_tests = len(result.failures)
    error_tests = len(result.errors)
    passed_tests = total_tests - failed_tests - error_tests
    
    # Log summary to file
    test_results_logger.info("=" * 80)
    test_results_logger.info("TEST SUITE SUMMARY")
    test_results_logger.info("=" * 80)
    test_results_logger.info(f"Total Tests: {total_tests}")
    test_results_logger.info(f"Passed: {passed_tests}")
    test_results_logger.info(f"Failed: {failed_tests}")
    test_results_logger.info(f"Errors: {error_tests}")
    test_results_logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    logger.info("=" * 60)
    logger.info("TEST SUITE SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total Tests: {total_tests}")
    logger.info(f"Passed: {passed_tests}")
    logger.info(f"Failed: {failed_tests}")
    logger.info(f"Errors: {error_tests}")
    logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    logger.info("=" * 60)
    
    # Print detailed failure information
    if result.failures:
        logger.error("FAILURES:")
        test_results_logger.error("FAILURES:")
        for test, traceback in result.failures:
            logger.error(f"Test: {test}")
            logger.error(f"Traceback: {traceback}")
            logger.error("-" * 40)
            test_results_logger.error(f"Test: {test}")
            test_results_logger.error(f"Traceback: {traceback}")
            test_results_logger.error("-" * 40)
    
    if result.errors:
        logger.error("ERRORS:")
        test_results_logger.error("ERRORS:")
        for test, traceback in result.errors:
            logger.error(f"Test: {test}")
            logger.error(f"Traceback: {traceback}")
            logger.error("-" * 40)
            test_results_logger.error(f"Test: {test}")
            test_results_logger.error(f"Traceback: {traceback}")
            test_results_logger.error("-" * 40)
    
    # Save detailed results to JSON file
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
    
    with open('test_results_detailed.json', 'w') as f:
        json.dump(detailed_results, f, indent=2, default=str)
    
    test_results_logger.info("Detailed results saved to test_results_detailed.json")
    
    # Exit with appropriate code
    if failed_tests > 0 or error_tests > 0:
        logger.error("Test suite failed!")
        test_results_logger.error("TEST SUITE FAILED!")
        sys.exit(1)
    else:
        logger.info("Test suite passed!")
        test_results_logger.info("TEST SUITE PASSED!")
        sys.exit(0)


if __name__ == "__main__":
    run_test_suite() 