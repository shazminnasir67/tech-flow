#!/usr/bin/env python3
"""
Simple test script to verify basic functionality
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

def main():
    """Main test function."""
    print("Starting simple test...")
    
    base_url = "http://localhost:5000"
    
    # Test 1: Basic connectivity
    print("1. Testing basic connectivity...")
    try:
        response = requests.get(base_url, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ Basic connectivity successful")
        else:
            print(f"   ✗ Unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Connection failed: {e}")
        return False
    
    # Test 2: Health endpoint
    print("2. Testing health endpoint...")
    try:
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
    
    # Test 3: Selenium basic
    print("3. Testing Selenium basic functionality...")
    try:
        # Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Install ChromeDriver
        print("   Installing ChromeDriver...")
        service = Service(ChromeDriverManager().install())
        print("   ✓ ChromeDriver installed")
        
        # Initialize WebDriver
        print("   Initializing WebDriver...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(10)
        wait = WebDriverWait(driver, 10)
        print("   ✓ WebDriver initialized")
        
        # Test page load
        print("   Testing page load...")
        driver.get(base_url)
        body = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print(f"   ✓ Page loaded successfully")
        print(f"   Title: {driver.title}")
        
        # Test login page
        print("   Testing login page...")
        driver.get(f"{base_url}/login")
        username_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
        print("   ✓ Login page loaded")
        print(f"   Title: {driver.title}")
        
        # Test register page
        print("   Testing register page...")
        driver.get(f"{base_url}/register")
        username_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
        print("   ✓ Register page loaded")
        print(f"   Title: {driver.title}")
        
        # Cleanup
        driver.quit()
        print("   ✓ WebDriver closed")
        
        return True
        
    except Exception as e:
        print(f"   ✗ Selenium test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✓ All tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Tests failed!")
        sys.exit(1) 