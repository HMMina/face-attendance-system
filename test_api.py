#!/usr/bin/env python
"""
Script kiểm tra API endpoints
"""
import requests
import json

def test_endpoint(url, name):
    try:
        print(f"\n=== Testing {name}: {url} ===")
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error Response: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    # Test cả hai URL
    test_endpoint("http://127.0.0.1:8000/api/v1/employees/", "127.0.0.1")
    test_endpoint("http://localhost:8000/api/v1/employees/", "localhost")
    
    # Test root endpoints
    test_endpoint("http://127.0.0.1:8000/test", "127.0.0.1 test")
    test_endpoint("http://localhost:8000/test", "localhost test")
