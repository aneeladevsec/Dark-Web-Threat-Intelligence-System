#!/usr/bin/env python3
"""
Dark Web Intelligence API - Comprehensive Test Suite
Tests all API endpoints and features
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:5002"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*50}")
    print(f"  {text}")
    print(f"{'='*50}{Colors.RESET}\n")

def test_endpoint(name, method, endpoint, expected_status=200, params=None, json_data=None):
    """Test a single endpoint"""
    try:
        url = f"{BASE_URL}{endpoint}"
        
        if method.upper() == "GET":
            response = requests.get(url, params=params, timeout=5)
        elif method.upper() == "POST":
            response = requests.post(url, json=json_data, timeout=5)
        else:
            print(f"{Colors.RED}[✗] {name}: Unknown method {method}{Colors.RESET}")
            return False
        
        if response.status_code == expected_status:
            print(f"{Colors.GREEN}[✓] {name}{Colors.RESET}")
            return True
        else:
            print(f"{Colors.RED}[✗] {name}: Expected {expected_status}, got {response.status_code}{Colors.RESET}")
            return False
    except Exception as e:
        print(f"{Colors.RED}[✗] {name}: {str(e)}{Colors.RESET}")
        return False

def main():
    print(f"\n{Colors.BLUE}🌑 Dark Web Intelligence API - Test Suite{Colors.RESET}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Target: {BASE_URL}")
    
    # Check if server is running
    print("\nChecking server connection...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"{Colors.GREEN}[✓] Server is running{Colors.RESET}")
        else:
            print(f"{Colors.RED}[✗] Server not responding correctly{Colors.RESET}")
            sys.exit(1)
    except:
        print(f"{Colors.RED}[✗] Cannot connect to server at {BASE_URL}{Colors.RESET}")
        print("Make sure the API is running: python backend/app.py")
        sys.exit(1)
    
    results = []
    
    # ==========================================
    # Core Endpoints
    # ==========================================
    print_header("CORE ENDPOINTS")
    
    results.append(test_endpoint("Health Check", "GET", "/health"))
    results.append(test_endpoint("API Home", "GET", "/"))
    results.append(test_endpoint("Statistics", "GET", "/stats"))
    results.append(test_endpoint("Geolocation Data", "GET", "/geo"))
    results.append(test_endpoint("Real-Time Feed", "GET", "/feed"))
    
    # ==========================================
    # Threat Management
    # ==========================================
    print_header("THREAT MANAGEMENT")
    
    results.append(test_endpoint("Get All Threats", "GET", "/threats"))
    results.append(test_endpoint("Get Recent Threats (24h)", "GET", "/threats/recent"))
    results.append(test_endpoint("Get Critical Threats", "GET", "/threats/critical"))
    results.append(test_endpoint("Search Threats", "GET", "/search", params={"q": "ransomware"}))
    
    # ==========================================
    # Advanced Analytics
    # ==========================================
    print_header("ADVANCED ANALYTICS")
    
    results.append(test_endpoint("Timeline Analytics", "GET", "/analytics/timeline", params={"days": 7}))
    results.append(test_endpoint("Predictive Insights", "GET", "/analytics/predictive"))
    results.append(test_endpoint("Advanced Metrics", "GET", "/analytics/advanced"))
    results.append(test_endpoint("Metrics by Type", "GET", "/threats/metrics/by-type"))
    results.append(test_endpoint("Metrics by Source", "GET", "/threats/metrics/by-source"))
    
    # ==========================================
    # Data Export
    # ==========================================
    print_header("DATA EXPORT")
    
    results.append(test_endpoint("Export CSV", "GET", "/export/threats/csv"))
    results.append(test_endpoint("Export JSON", "GET", "/export/threats/json"))
    
    # ==========================================
    # System Features
    # ==========================================
    print_header("SYSTEM FEATURES")
    
    results.append(test_endpoint("Get Alerts", "GET", "/alerts", params={"limit": 10}))
    results.append(test_endpoint("Create Incident", "POST", "/incidents", expected_status=201, 
                                json_data={"name": "Test Incident", "severity": "High"}))
    results.append(test_endpoint("API Key Info", "GET", "/api/key"))
    
    # ==========================================
    # Test Threat Correlations
    # ==========================================
    print_header("THREAT CORRELATIONS")
    
    try:
        # First, get a threat ID
        response = requests.get(f"{BASE_URL}/threats", timeout=5)
        if response.status_code == 200:
            threats = response.json()["threats"]
            if threats:
                threat_id = threats[0]["id"]
                results.append(test_endpoint(f"Threat Correlations ({threat_id})", "GET", 
                                           f"/threats/{threat_id}/correlations"))
    except:
        pass
    
    # ==========================================
    # Summary
    # ==========================================
    print_header("TEST SUMMARY")
    
    passed = sum(results)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"Total Tests: {total}")
    print(f"Passed: {Colors.GREEN}{passed}{Colors.RESET}")
    print(f"Failed: {Colors.RED}{total - passed}{Colors.RESET}")
    print(f"Success Rate: {Colors.YELLOW}{percentage:.1f}%{Colors.RESET}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}🎉 ALL TESTS PASSED!{Colors.RESET}")
        print(f"{Colors.GREEN}✓ System is fully operational{Colors.RESET}\n")
        return 0
    else:
        print(f"\n{Colors.RED}⚠ Some tests failed{Colors.RESET}")
        print(f"{Colors.RED}✗ Check the failures above{Colors.RESET}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
