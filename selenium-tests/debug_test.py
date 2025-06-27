#!/usr/bin/env python3
"""
Debug test script for DevOps Assignment 3
Simple connectivity and basic functionality test
"""

import requests
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def test_connectivity():
    """Test basic connectivity to the web application."""
    base_url = "http://localhost:5000"
    
    print("=== Testing Basic Connectivity ===")
    
    try:
        # Test basic connectivity
        print("1. Testing basic connectivity...")
        response = requests.get(base_url, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response length: {len(response.text)} characters")
        if response.status_code == 200:
            print("   ✓ Basic connectivity successful")
        else:
            print(f"   ✗ Unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Connection failed: {e}")
        return False
    
    try:
        # Test health endpoint
        print("2. Testing health endpoint...")
        response = requests.get(f"{base_url}/api/health", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        if response.status_code == 200:
            print("   ✓ Health endpoint accessible")
        else:
            print(f"   ✗ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Health endpoint error: {e}")
        return False
    
    return True

def test_selenium_basic():
    """Test basic Selenium functionality."""
    print("\n=== Testing Selenium Basic Functionality ===")
    
    try:
        # Chrome options for headless testing
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Use webdriver-manager to handle ChromeDriver
        print("1. Installing ChromeDriver...")
        service = Service(ChromeDriverManager().install())
        print("   ✓ ChromeDriver installed successfully")
        
        # Initialize WebDriver
        print("2. Initializing WebDriver...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(10)
        wait = WebDriverWait(driver, 10)
        print("   ✓ WebDriver initialized successfully")
        
        # Test basic page load
        print("3. Testing page load...")
        driver.get("http://localhost:5000")
        body = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print(f"   ✓ Page loaded successfully")
        print(f"   Title: {driver.title}")
        
        # Test login page
        print("4. Testing login page...")
        driver.get("http://localhost:5000/login")
        username_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
        print("   ✓ Login page loaded successfully")
        print(f"   Title: {driver.title}")
        
        # Test register page
        print("5. Testing register page...")
        driver.get("http://localhost:5000/register")
        username_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
        print("   ✓ Register page loaded successfully")
        print(f"   Title: {driver.title}")
        
        # Cleanup
        driver.quit()
        print("   ✓ WebDriver closed successfully")
        
        return True
        
    except Exception as e:
        print(f"   ✗ Selenium test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main debug function."""
    print("Starting Debug Test for DevOps Assignment 3")
    print("=" * 50)
    
    # Test connectivity
    connectivity_ok = test_connectivity()
    
    if not connectivity_ok:
        print("\n✗ Connectivity test failed!")
        sys.exit(1)
    
    # Test Selenium
    selenium_ok = test_selenium_basic()
    
    if not selenium_ok:
        print("\n✗ Selenium test failed!")
        sys.exit(1)
    
    print("\n✓ All debug tests passed!")
    print("Ready to run full test suite.")
    sys.exit(0)

if __name__ == "__main__":
    main() 