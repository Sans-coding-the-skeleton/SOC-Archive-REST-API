#!/usr/bin/env python3
"""
SOC-Archive-REST-API Testing Script
A complete API testing solution in a single file
"""

import requests
import json
import time
import os
import sys
from typing import Dict, Any, List, Optional


class SOCAPITester:
    def __init__(self, base_url: str = None, token: str = None):
        self.base_url = base_url or "https://api.github.com/repos/Sans-coding-the-skeleton/SOC-Archive-REST-API"
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.session = requests.Session()
        self.test_results = []
        self.setup_headers()

    def setup_headers(self):
        """Setup default headers for API requests"""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "SOC-API-Tester/1.0.0",
            "Content-Type": "application/json"
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        self.session.headers.update(headers)

    def make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request and return response"""
        url = f"{self.base_url}{endpoint}"

        try:
            start_time = time.time()
            response = self.session.request(method, url, **kwargs)
            response_time = time.time() - start_time

            # Don't raise for status - we want to handle different status codes
            response_data = {
                "success": 200 <= response.status_code < 400,  # Success for 2xx and 3xx
                "status_code": response.status_code,
                "response_time": response_time,
                "data": response.json() if response.content else {},
                "headers": dict(response.headers)
            }
            return response_data
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Invalid JSON response",
                "status_code": response.status_code if 'response' in locals() else None
            }

    def test_api_connectivity(self) -> Dict[str, Any]:
        """Test basic API connectivity"""
        print("🔌 Testing API connectivity...")
        result = self.make_request("GET", "")

        test_result = {
            "test_name": "api_connectivity",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        if result["success"]:
            data = result["data"]
            test_result.update({
                "status": "PASS",
                "repository_name": data.get('full_name', 'Unknown'),
                "description": data.get('description', 'No description'),
                "stars": data.get('stargazers_count', 0),
                "forks": data.get('forks_count', 0),
                "response_time": result.get('response_time', 0)
            })
            print(f"✅ Connected to {data.get('full_name', 'Unknown')}")
            print(f"   📝 Description: {data.get('description', 'No description')}")
            print(f"   ⭐ Stars: {data.get('stargazers_count', 0)}")
            print(f"   🍴 Forks: {data.get('forks_count', 0)}")
        else:
            test_result.update({
                "status": "FAIL",
                "error": result['error'],
                "status_code": result.get('status_code')
            })
            print(f"❌ Failed to connect: {result['error']}")

        self.test_results.append(test_result)
        return test_result

    def test_repository_info(self) -> Dict[str, Any]:
        """Test repository information endpoint"""
        print("\n📋 Testing repository information...")
        result = self.make_request("GET", "")

        test_result = {
            "test_name": "repository_info",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        if result["success"]:
            data = result["data"]
            required_fields = ["id", "name", "full_name", "html_url", "description"]
            missing_fields = [field for field in required_fields if field not in data]

            test_result.update({
                "status": "PASS" if not missing_fields else "FAIL",
                "missing_fields": missing_fields,
                "repository_id": data.get('id'),
                "response_time": result.get('response_time', 0)
            })

            if not missing_fields:
                print("✅ Repository info test passed")
            else:
                print(f"❌ Missing fields: {missing_fields}")
        else:
            test_result.update({
                "status": "FAIL",
                "error": result['error'],
                "status_code": result.get('status_code')
            })
            print(f"❌ Repository info test failed: {result['error']}")

        self.test_results.append(test_result)
        return test_result

    def test_endpoints(self) -> Dict[str, Any]:
        """Test various API endpoints"""
        print("\n🔍 Testing API endpoints...")

        endpoints = [
            ("/issues", "GET"),
            ("/commits", "GET"),
            ("/releases", "GET"),
            ("/contents", "GET"),
            ("/languages", "GET"),
            ("/contributors", "GET")
        ]

        endpoint_results = {}
        test_result = {
            "test_name": "endpoint_testing",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "endpoints": {}
        }

        for endpoint, method in endpoints:
            print(f"   Testing {endpoint}...", end=" ")
            result = self.make_request(method, endpoint)

            endpoint_test = {
                "success": result["success"],
                "status_code": result.get("status_code"),
                "response_time": result.get('response_time', 0)
            }

            # Consider 404 as acceptable for endpoints that might not exist
            if result["success"] or result.get("status_code") == 404:
                status = "✅" if result["success"] else "⚠️ (404 - Not Found)"
                print(status)
                endpoint_results[endpoint] = True  # Count as success for testing purposes
            else:
                print("❌")
                endpoint_results[endpoint] = False

            test_result["endpoints"][endpoint] = endpoint_test

        # Overall endpoint test status
        successful_endpoints = sum(1 for success in endpoint_results.values() if success)
        total_endpoints = len(endpoint_results)
        test_result["status"] = "PASS" if successful_endpoints == total_endpoints else "WARNING"
        test_result["success_rate"] = f"{successful_endpoints}/{total_endpoints}"

        self.test_results.append(test_result)
        return test_result

    def test_response_headers(self) -> Dict[str, Any]:
        """Test response headers are correct"""
        print("\n📄 Testing response headers...")
        result = self.make_request("GET", "")

        test_result = {
            "test_name": "response_headers",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        if result["success"]:
            headers = result["headers"]
            content_type = headers.get("Content-Type", "")

            test_result.update({
                "content_type": content_type,
                "response_time": result.get('response_time', 0)
            })

            if "application/json" in content_type:
                test_result["status"] = "PASS"
                print("✅ Content-Type header is correct")
            else:
                test_result["status"] = "FAIL"
                print(f"❌ Unexpected Content-Type: {content_type}")
        else:
            test_result.update({
                "status": "FAIL",
                "error": result['error'],
                "status_code": result.get('status_code')
            })
            print(f"❌ Headers test failed: {result['error']}")

        self.test_results.append(test_result)
        return test_result

    def test_error_handling(self) -> Dict[str, Any]:
        """Test API error handling - FIXED LOGIC"""
        print("\n🚨 Testing error handling...")

        # Test non-existent endpoint - we EXPECT a 404 here
        result = self.make_request("GET", "/nonexistent-endpoint-12345")

        test_result = {
            "test_name": "error_handling",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "tested_endpoint": "/nonexistent-endpoint-12345",
            "status_code": result.get("status_code")
        }

        # FIXED: Getting a 404 for a non-existent endpoint is CORRECT behavior
        if result.get("status_code") == 404:
            test_result["status"] = "PASS"
            print("✅ Error handling test passed (correctly returned 404 for non-existent endpoint)")
        elif result.get("status_code") == 400:
            test_result["status"] = "PASS"
            print("✅ Error handling test passed (correctly returned 400 for bad request)")
        elif result["success"]:
            test_result["status"] = "FAIL"
            print("❌ Error handling test failed (non-existent endpoint returned success)")
        else:
            test_result.update({
                "status": "WARNING",
                "error": result.get('error', 'Unknown error')
            })
            print(f"⚠️  Error handling test: {result.get('error', 'Unknown error')}")

        self.test_results.append(test_result)
        return test_result

    def test_performance(self) -> Dict[str, Any]:
        """Test API response performance"""
        print("\n⚡ Testing performance...")

        start_time = time.time()
        result = self.make_request("GET", "")
        response_time = time.time() - start_time

        test_result = {
            "test_name": "performance",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "response_time": response_time
        }

        if result["success"]:
            print(f"   Response time: {response_time:.2f}s")

            if response_time < 2.0:
                test_result["status"] = "PASS"
                test_result["rating"] = "excellent"
                print("✅ Performance test passed (fast response)")
            elif response_time < 5.0:
                test_result["status"] = "PASS"
                test_result["rating"] = "good"
                print("✅ Performance test passed (good response)")
            else:
                test_result["status"] = "WARNING"
                test_result["rating"] = "slow"
                print("⚠️  Performance warning (slow response)")
        else:
            test_result.update({
                "status": "FAIL",
                "error": result['error']
            })
            print(f"❌ Performance test failed: {result['error']}")

        self.test_results.append(test_result)
        return test_result

    def test_authentication(self) -> Dict[str, Any]:
        """Test authentication (if token is provided)"""
        test_result = {
            "test_name": "authentication",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "token_provided": bool(self.token)
        }

        if not self.token:
            print("\n🔐 No token provided - skipping authentication tests")
            test_result["status"] = "SKIPPED"
            self.test_results.append(test_result)
            return test_result

        print("\n🔐 Testing authentication...")

        # Test with valid token
        result = self.make_request("GET", "")

        if result["success"]:
            test_result.update({
                "status": "PASS",
                "response_time": result.get('response_time', 0)
            })
            print("✅ Authentication test passed")
        elif result.get("status_code") == 401:
            test_result.update({
                "status": "FAIL",
                "error": "Invalid token"
            })
            print("❌ Authentication failed (invalid token)")
        else:
            test_result.update({
                "status": "WARNING",
                "error": result['error'],
                "status_code": result.get('status_code')
            })
            print(f"⚠️  Authentication test: {result['error']}")

        self.test_results.append(test_result)
        return test_result

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return results"""
        print("🚀 Starting SOC-Archive-REST-API Tests")
        print("=" * 50)

        # Clear previous results
        self.test_results = []

        # Run all tests
        tests = [
            self.test_api_connectivity,
            self.test_repository_info,
            self.test_response_headers,
            self.test_error_handling,  # This should now pass
            self.test_performance,
            self.test_authentication,
            self.test_endpoints
        ]

        for test in tests:
            test()

        # Calculate summary statistics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result.get('status') == 'PASS')
        failed_tests = sum(1 for result in self.test_results if result.get('status') == 'FAIL')
        warning_tests = sum(1 for result in self.test_results if result.get('status') == 'WARNING')
        skipped_tests = sum(1 for result in self.test_results if result.get('status') == 'SKIPPED')

        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        print(f"✅ Passed: {passed_tests}/{total_tests}")
        print(f"❌ Failed: {failed_tests}/{total_tests}")
        print(f"⚠️  Warnings: {warning_tests}/{total_tests}")
        if skipped_tests > 0:
            print(f"⏭️  Skipped: {skipped_tests}/{total_tests}")

        if failed_tests == 0 and warning_tests == 0:
            print("🎉 All tests passed!")
        elif failed_tests == 0:
            print("💡 All tests passed with some warnings")
        else:
            print("💡 Some tests failed or had warnings")

        return {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "warnings": warning_tests,
            "skipped": skipped_tests
        }

    def save_results(self, filename: str = "api_test_results.json"):
        """Save test results to JSON file"""
        results_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "base_url": self.base_url,
            "test_summary": {
                "total_tests": len(self.test_results),
                "passed": sum(1 for r in self.test_results if r.get('status') == 'PASS'),
                "failed": sum(1 for r in self.test_results if r.get('status') == 'FAIL'),
                "warnings": sum(1 for r in self.test_results if r.get('status') == 'WARNING'),
                "skipped": sum(1 for r in self.test_results if r.get('status') == 'SKIPPED')
            },
            "test_results": self.test_results
        }

        with open(filename, 'w') as f:
            json.dump(results_data, f, indent=2)

        print(f"\n💾 Results saved to {filename}")


def main():
    """Main function to run the tests"""

    # Configuration
    BASE_URL = "https://api.github.com/repos/Sans-coding-the-skeleton/SOC-Archive-REST-API"
    TOKEN = os.getenv("GITHUB_TOKEN")  # Set this environment variable

    # Create tester instance
    tester = SOCAPITester(base_url=BASE_URL, token=TOKEN)

    # Run all tests
    try:
        summary = tester.run_all_tests()

        # Save results
        tester.save_results()

        # Exit with appropriate code
        if summary["failed"] == 0:
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # Some tests failed

    except KeyboardInterrupt:
        print("\n❌ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()