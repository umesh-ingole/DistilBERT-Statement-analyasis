#!/usr/bin/env python3
"""
Quick local testing script for Flask + DistilBERT API
Tests all endpoints and validates deployment readiness
"""

import requests
import json
import sys
import time
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:5000"
ENDPOINTS_TO_TEST = [
    {
        "name": "Health Check",
        "method": "GET",
        "path": "/health",
        "expected_keys": ["status", "model_loaded"]
    },
    {
        "name": "Positive Sentiment",
        "method": "POST",
        "path": "/api/predict",
        "data": {"text": "This movie was absolutely amazing and I loved every second!"},
        "expected_keys": ["success", "label", "confidence"]
    },
    {
        "name": "Negative Sentiment",
        "method": "POST",
        "path": "/api/predict",
        "data": {"text": "Terrible film, complete waste of time and money."},
        "expected_keys": ["success", "label", "confidence"]
    },
    {
        "name": "Neutral/Mixed Sentiment",
        "method": "POST",
        "path": "/api/predict",
        "data": {"text": "It was okay, nothing special. Good acting but slow story."},
        "expected_keys": ["success", "label", "confidence"]
    },
    {
        "name": "Web UI",
        "method": "GET",
        "path": "/",
        "expected_keys": ["html", "DistilBERT"]  # Check for HTML content and title
    },
]

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_success(text):
    """Print success message"""
    print(f"  ✅ {text}")

def print_error(text):
    """Print error message"""
    print(f"  ❌ {text}")

def print_info(text):
    """Print info message"""
    print(f"  ℹ️  {text}")

def test_health():
    """Test health endpoint"""
    print_header("1. HEALTH CHECK")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print_info(f"Status Code: {response.status_code}")
        
        data = response.json()
        print_info(f"Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 200 and data.get("model_loaded"):
            print_success("Model is loaded and ready!")
            return True
        else:
            print_error("Model not loaded or health check failed")
            return False
            
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to {BASE_URL}")
        print_info("Is the Flask app running? Try: python app.py")
        return False
    except Exception as e:
        print_error(f"Health check failed: {e}")
        return False

def test_predictions():
    """Test prediction endpoints"""
    print_header("2. PREDICTION TESTS")
    
    all_passed = True
    
    for test in ENDPOINTS_TO_TEST[1:]:  # Skip health check (already tested)
        if test["method"] == "POST":
            test_prediction_single(test)

def test_prediction_single(test_case):
    """Test a single prediction"""
    print(f"\n  Test: {test_case['name']}")
    print(f"  Text: \"{test_case['data']['text'][:50]}...\"")
    
    try:
        response = requests.post(
            f"{BASE_URL}{test_case['path']}",
            json=test_case['data'],
            timeout=10
        )
        
        print(f"  Status: {response.status_code}")
        data = response.json()
        
        # Validate response
        if not data.get("success"):
            print_error(f"Prediction failed: {data.get('error')}")
            return False
        
        label = data.get("label")
        confidence = data.get("confidence")
        
        print_success(f"Label: {label}, Confidence: {confidence:.2%}")
        
        # Show probabilities
        probs = data.get("probabilities", {})
        if probs:
            print_info(f"Probabilities: NEG={probs.get('NEGATIVE', 0):.2%}, POS={probs.get('POSITIVE', 0):.2%}")
        
        return True
        
    except requests.exceptions.Timeout:
        print_error("Request timed out (model might be loading)")
        return False
    except Exception as e:
        print_error(f"Prediction failed: {e}")
        return False

def test_web_ui():
    """Test web UI endpoint"""
    print_header("3. WEB UI TEST")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            if "html" in response.text.lower() or "distilbert" in response.text.lower():
                print_success("Web UI loaded successfully!")
                print_info(f"HTML size: {len(response.text)} bytes")
                return True
            else:
                print_error("Web UI response is not HTML")
                return False
        else:
            print_error(f"Web UI returned status {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Web UI test failed: {e}")
        return False

def test_error_handling():
    """Test error handling"""
    print_header("4. ERROR HANDLING TESTS")
    
    # Test missing text
    print("\n  Test: Missing text parameter")
    try:
        response = requests.post(
            f"{BASE_URL}/api/predict",
            json={},
            timeout=5
        )
        
        if response.status_code == 400:
            data = response.json()
            if not data.get("success"):
                print_success(f"Correctly rejected empty request: {data.get('error')}")
                return True
        
        print_error("Should reject empty text")
        return False
        
    except Exception as e:
        print_error(f"Error handling test failed: {e}")
        return False

def verify_files():
    """Verify deployment files exist"""
    print_header("5. DEPLOYMENT FILES CHECK")
    
    project_root = Path(__file__).parent
    files_to_check = [
        ("app.py", "Flask app"),
        ("requirements.txt", "Dependencies"),
        ("Procfile", "Render startup"),
        ("runtime.txt", "Python version"),
        ("models/best_model/config.json", "Model config"),
        ("src/config.py", "Configuration"),
        ("predict.py", "Predictor"),
    ]
    
    all_exist = True
    for filename, description in files_to_check:
        filepath = project_root / filename
        if filepath.exists():
            print_success(f"{description}: {filename}")
        else:
            print_error(f"{description}: {filename} NOT FOUND")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests"""
    print("\n")
    print_header("FLASK + DISTILBERT API - LOCAL TESTING")
    print("  This script tests all endpoints for deployment readiness")
    
    print("\n⏳ Starting tests in 2 seconds... (make sure Flask app is running!)")
    print("   Command: python app.py")
    time.sleep(2)
    
    # Run tests
    tests_passed = []
    
    tests_passed.append(("Files Check", verify_files()))
    tests_passed.append(("Health Check", test_health()))
    
    if tests_passed[-1][1]:  # Only test predictions if health check passed
        test_predictions()
        test_web_ui()
        test_error_handling()
    
    # Summary
    print_header("TEST SUMMARY")
    
    successful = sum(1 for _, passed in tests_passed if passed)
    total = len(tests_passed)
    
    print(f"\n  Tests Passed: {successful}/{total}")
    
    if successful == total:
        print_success("All tests passed! Ready for deployment. 🚀")
        return 0
    else:
        print_error("Some tests failed. Review errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
