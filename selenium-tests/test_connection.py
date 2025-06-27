#!/usr/bin/env python3
"""
Simple connection test script for DevOps Assignment 3
Tests connectivity to the Flask web application on EC2
"""

import requests
import sys
import time

def test_connection():
    """Test connection to the web application."""
    base_url = "http://localhost:5000"
    
    print(f"Testing connection to {base_url}")
    
    # Test basic connectivity
    try:
        print("1. Testing basic connectivity...")
        response = requests.get(base_url, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response length: {len(response.text)} characters")
        if response.status_code == 200:
            print("   ✓ Basic connectivity successful")
        else:
            print(f"   ✗ Unexpected status code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ✗ Connection failed - application may not be running")
        return False
    except requests.exceptions.Timeout:
        print("   ✗ Connection timeout")
        return False
    except Exception as e:
        print(f"   ✗ Unexpected error: {e}")
        return False
    
    # Test health endpoint
    try:
        print("2. Testing health endpoint...")
        response = requests.get(f"{base_url}/api/health", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        if response.status_code == 200:
            print("   ✓ Health endpoint accessible")
        else:
            print(f"   ✗ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Health endpoint error: {e}")
        return False
    
    # Test login page
    try:
        print("3. Testing login page...")
        response = requests.get(f"{base_url}/login", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ Login page accessible")
        else:
            print(f"   ✗ Login page failed: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Login page error: {e}")
        return False
    
    # Test register page
    try:
        print("4. Testing register page...")
        response = requests.get(f"{base_url}/register", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ Register page accessible")
        else:
            print(f"   ✗ Register page failed: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Register page error: {e}")
        return False
    
    print("\n✓ All connection tests passed!")
    return True

if __name__ == "__main__":
    success = test_connection()
    if not success:
        print("\n✗ Connection tests failed!")
        sys.exit(1)
    else:
        print("\n✓ Ready to run Selenium tests!")
        sys.exit(0) 