"""
Test Configuration for DevOps Assignment 3
CSC483 - Spring 2025

Configuration settings for Selenium test suite.
"""

import os
from datetime import datetime

class TestConfig:
    """Configuration class for test settings."""
    
    # Application URLs
    BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')
    WEB_APP_URL = os.getenv('WEB_APP_URL', 'http://localhost:5000')
    
    # Browser Configuration
    BROWSER = os.getenv('BROWSER', 'chrome')
    HEADLESS = os.getenv('HEADLESS', 'true').lower() == 'true'
    WINDOW_SIZE = os.getenv('WINDOW_SIZE', '1920,1080')
    
    # Test Configuration
    IMPLICIT_WAIT = int(os.getenv('IMPLICIT_WAIT', '10'))
    EXPLICIT_WAIT = int(os.getenv('EXPLICIT_WAIT', '10'))
    PAGE_LOAD_TIMEOUT = int(os.getenv('PAGE_LOAD_TIMEOUT', '30'))
    
    # Screenshot Configuration
    SCREENSHOTS_DIR = os.getenv('SCREENSHOTS_DIR', 'screenshots')
    TAKE_SCREENSHOTS = os.getenv('TAKE_SCREENSHOTS', 'true').lower() == 'true'
    
    # Test Data Configuration
    TEST_DATA_PREFIX = os.getenv('TEST_DATA_PREFIX', 'testuser')
    TEST_EMAIL_DOMAIN = os.getenv('TEST_EMAIL_DOMAIN', 'example.com')
    
    # Performance Configuration
    MAX_PAGE_LOAD_TIME = float(os.getenv('MAX_PAGE_LOAD_TIME', '5.0'))
    PERFORMANCE_THRESHOLD = float(os.getenv('PERFORMANCE_THRESHOLD', '3.0'))
    
    # Reporting Configuration
    REPORT_DIR = os.getenv('REPORT_DIR', 'reports')
    HTML_REPORT = os.getenv('HTML_REPORT', 'true').lower() == 'true'
    JSON_REPORT = os.getenv('JSON_REPORT', 'true').lower() == 'true'
    
    # Email Configuration (for notifications)
    EMAIL_ENABLED = os.getenv('EMAIL_ENABLED', 'false').lower() == 'true'
    EMAIL_SMTP_SERVER = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
    EMAIL_SMTP_PORT = int(os.getenv('EMAIL_SMTP_PORT', '587'))
    EMAIL_USERNAME = os.getenv('EMAIL_USERNAME', '')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
    EMAIL_RECIPIENTS = os.getenv('EMAIL_RECIPIENTS', '').split(',')
    
    # Chrome Options
    CHROME_OPTIONS = [
        '--headless' if HEADLESS else '',
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        f'--window-size={WINDOW_SIZE}',
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        '--disable-extensions',
        '--disable-plugins',
        '--disable-images',
        '--disable-javascript',
        '--disable-css',
        '--disable-web-security',
        '--allow-running-insecure-content',
        '--disable-features=VizDisplayCompositor'
    ]
    
    # Test Data Templates
    VALID_USER_DATA = {
        'username': 'testuser_valid',
        'email': 'testuser_valid@example.com',
        'password': 'validpass123',
        'confirm_password': 'validpass123'
    }
    
    INVALID_USER_DATA = {
        'username': 'ab',  # Too short
        'email': 'invalid-email',
        'password': '123',  # Too short
        'confirm_password': 'different'
    }
    
    # Expected Elements
    EXPECTED_ELEMENTS = {
        'home_page': [
            'navbar',
            'home_link',
            'login_link',
            'register_link',
            'main_content',
            'footer'
        ],
        'login_page': [
            'username_field',
            'password_field',
            'login_button',
            'register_link'
        ],
        'register_page': [
            'username_field',
            'email_field',
            'password_field',
            'confirm_password_field',
            'terms_checkbox',
            'register_button',
            'login_link'
        ],
        'dashboard_page': [
            'user_profile',
            'activity_log',
            'logout_button',
            'navigation_menu'
        ]
    }
    
    # Error Messages
    EXPECTED_ERROR_MESSAGES = {
        'invalid_username': 'Username must be at least 3 characters long',
        'invalid_email': 'Please enter a valid email address',
        'invalid_password': 'Password must be at least 6 characters long',
        'password_mismatch': 'Passwords do not match',
        'invalid_credentials': 'Invalid username or password',
        'empty_fields': 'Please enter both username and password',
        'access_denied': 'Please login to access the dashboard'
    }
    
    # Success Messages
    EXPECTED_SUCCESS_MESSAGES = {
        'registration_success': 'Registration successful',
        'login_success': 'Welcome back',
        'logout_success': 'You have been logged out successfully'
    }
    
    @classmethod
    def get_test_data(cls, test_name):
        """Generate unique test data for a specific test."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return {
            'username': f"{cls.TEST_DATA_PREFIX}_{test_name}_{timestamp}",
            'email': f"{cls.TEST_DATA_PREFIX}_{test_name}_{timestamp}@{cls.TEST_EMAIL_DOMAIN}",
            'password': f"pass{timestamp}",
            'confirm_password': f"pass{timestamp}"
        }
    
    @classmethod
    def get_chrome_options(cls):
        """Get Chrome options for WebDriver."""
        from selenium.webdriver.chrome.options import Options
        options = Options()
        
        for option in cls.CHROME_OPTIONS:
            if option:
                options.add_argument(option)
        
        return options
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories for test execution."""
        directories = [cls.SCREENSHOTS_DIR, cls.REPORT_DIR]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    @classmethod
    def get_report_filename(cls):
        """Generate report filename with timestamp."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"test_report_{timestamp}"
    
    @classmethod
    def get_screenshot_filename(cls, test_name, status=''):
        """Generate screenshot filename."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{test_name}_{timestamp}"
        if status:
            filename += f"_{status}"
        return f"{filename}.png" 