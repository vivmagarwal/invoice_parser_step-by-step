#!/usr/bin/env python3
"""
Comprehensive Test Script for Invoice Parser Teaching Plan
Tests all 10 steps for functionality and continuity
"""

import os
import sys
import subprocess
import json
import time
import asyncio
import aiohttp
from pathlib import Path
import difflib

BASE_DIR = Path(__file__).parent.absolute()

class StepTester:
    def __init__(self):
        self.results = {}
        self.issues = []

    def test_directory_structure(self, step_num):
        """Test that step has correct directory structure"""
        step_dir = BASE_DIR / f"invoice-parser-step{step_num:03d}"

        # Check main directories exist
        checks = {
            "Step directory exists": step_dir.exists(),
            "Starting code exists": (step_dir / "starting-code").exists(),
            "Ending code exists": (step_dir / "ending-code").exists(),
            "Teacher notes exist": (step_dir / "teacher-notes.md").exists()
        }

        # Special case for step 001 - starting code should be empty
        if step_num == 1:
            starting_code = list((step_dir / "starting-code").iterdir())
            checks["Starting code empty (step 001)"] = len(starting_code) == 0

        return all(checks.values()), checks

    def test_continuity(self, step_num):
        """Test continuity between steps"""
        if step_num == 1:
            return True, {"First step": "No previous step to check"}

        prev_ending = BASE_DIR / f"invoice-parser-step{step_num-1:03d}" / "ending-code"
        curr_starting = BASE_DIR / f"invoice-parser-step{step_num:03d}" / "starting-code"

        if not prev_ending.exists() or not curr_starting.exists():
            return False, {"Error": "Directories don't exist"}

        # Compare directories
        result = subprocess.run(
            ["diff", "-r", "-q", str(prev_ending), str(curr_starting)],
            capture_output=True,
            text=True
        )

        is_identical = result.returncode == 0
        return is_identical, {
            "Continuity": "Maintained" if is_identical else "Broken",
            "Differences": result.stdout if not is_identical else "None"
        }

    async def test_step_002_api(self):
        """Test Step 002: FastAPI Backend Foundation"""
        try:
            async with aiohttp.ClientSession() as session:
                # Test health endpoint
                async with session.get("http://localhost:8002/api/health") as resp:
                    if resp.status == 200:
                        return True, {"Health endpoint": "Working"}
                    else:
                        return False, {"Health endpoint": f"Failed with status {resp.status}"}
        except Exception as e:
            return False, {"API Test": f"Error: {str(e)}"}

    async def test_step_003_database(self):
        """Test Step 003: Database Models"""
        try:
            # Check if database file was created
            db_path = BASE_DIR / "invoice-parser-step003" / "ending-code" / "backend" / "invoice_parser.db"
            if db_path.exists():
                return True, {"Database": "Created successfully"}
            else:
                # Try to trigger database creation
                async with aiohttp.ClientSession() as session:
                    await session.get("http://localhost:8003/api/health")
                if db_path.exists():
                    return True, {"Database": "Created after API call"}
                return False, {"Database": "Not created"}
        except Exception as e:
            return False, {"Database Test": f"Error: {str(e)}"}

    async def test_step_004_auth(self):
        """Test Step 004: User Authentication"""
        try:
            async with aiohttp.ClientSession() as session:
                # Test registration
                test_user = {
                    "email": f"test_{int(time.time())}@example.com",
                    "password": "TestPass123!",
                    "full_name": "Test User"
                }

                async with session.post(
                    "http://localhost:8004/api/auth/register",
                    json=test_user
                ) as resp:
                    if resp.status != 200:
                        return False, {"Registration": f"Failed with status {resp.status}"}

                # Test login
                async with session.post(
                    "http://localhost:8004/api/auth/login",
                    data={
                        "username": test_user["email"],
                        "password": test_user["password"]
                    }
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if "access_token" in data:
                            return True, {"Authentication": "Working", "Token": "Generated"}
                    return False, {"Login": "Failed"}

        except Exception as e:
            return False, {"Auth Test": f"Error: {str(e)}"}

    async def test_step_006_frontend(self):
        """Test Step 006: React Frontend"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:5173") as resp:
                    if resp.status == 200:
                        content = await resp.text()
                        if "root" in content or "React" in content:
                            return True, {"Frontend": "Running", "React": "Loaded"}
                    return False, {"Frontend": f"Status {resp.status}"}
        except Exception as e:
            return False, {"Frontend Test": f"Error: {str(e)}"}

    async def test_step_007_ai(self):
        """Test Step 007: AI Integration"""
        test_script = BASE_DIR / "invoice-parser-step007" / "ending-code" / "backend" / "test_step007.py"
        if test_script.exists():
            # Run the test script
            result = subprocess.run(
                ["python", str(test_script)],
                capture_output=True,
                text=True,
                cwd=str(test_script.parent)
            )
            if result.returncode == 0:
                return True, {"AI Integration": "Test passed"}
            else:
                return False, {"AI Integration": "Test failed", "Error": result.stderr[:200]}
        return False, {"Test script": "Not found"}

    async def test_step_010_completeness(self):
        """Test that Step 010 has all features from invoice_parser-main"""
        step010_dir = BASE_DIR / "invoice-parser-step010" / "ending-code"
        main_dir = BASE_DIR / "invoice_parser-main"

        # Check key files and directories
        key_paths = [
            "backend/app/services/ai_service.py",
            "backend/app/services/database_service.py",
            "backend/app/services/search_service.py",
            "backend/app/core/validation.py",
            "backend/app/api/invoices.py",
            "frontend/src/pages/Dashboard.jsx",
            "frontend/src/components"
        ]

        checks = {}
        for path in key_paths:
            step010_path = step010_dir / path
            main_path = main_dir / path

            if main_path.exists():
                checks[path] = step010_path.exists()

        all_present = all(checks.values())
        return all_present, checks

    async def run_all_tests(self):
        """Run all tests for all steps"""
        print("=" * 80)
        print("INVOICE PARSER TEACHING PLAN - COMPREHENSIVE TEST")
        print("=" * 80)

        # Test each step
        for step_num in range(1, 11):
            print(f"\n📋 Testing STEP-{step_num:03d}")
            print("-" * 40)

            # Test directory structure
            passed, details = self.test_directory_structure(step_num)
            self.results[f"step{step_num:03d}_structure"] = passed
            print(f"  Directory structure: {'✅' if passed else '❌'}")
            if not passed:
                for key, val in details.items():
                    if not val:
                        print(f"    - {key}: Missing")

            # Test continuity
            if step_num > 1:
                passed, details = self.test_continuity(step_num)
                self.results[f"step{step_num:03d}_continuity"] = passed
                print(f"  Continuity with previous: {'✅' if passed else '❌'}")
                if not passed and "Differences" in details:
                    print(f"    - {details['Differences'][:200]}")

            # Step-specific tests
            if step_num == 2:
                print("  Testing API endpoints...")
                passed, details = await self.test_step_002_api()
                self.results["step002_api"] = passed
                print(f"    API: {'✅' if passed else '❌'}")

            elif step_num == 3:
                print("  Testing database...")
                passed, details = await self.test_step_003_database()
                self.results["step003_database"] = passed
                print(f"    Database: {'✅' if passed else '❌'}")

            elif step_num == 4:
                print("  Testing authentication...")
                passed, details = await self.test_step_004_auth()
                self.results["step004_auth"] = passed
                print(f"    Auth: {'✅' if passed else '❌'}")

            elif step_num == 6:
                print("  Testing frontend...")
                passed, details = await self.test_step_006_frontend()
                self.results["step006_frontend"] = passed
                print(f"    Frontend: {'✅' if passed else '❌'}")

            elif step_num == 7:
                print("  Testing AI integration...")
                passed, details = await self.test_step_007_ai()
                self.results["step007_ai"] = passed
                print(f"    AI: {'✅' if passed else '❌'}")

            elif step_num == 10:
                print("  Testing completeness...")
                passed, details = await self.test_step_010_completeness()
                self.results["step010_complete"] = passed
                print(f"    Feature completeness: {'✅' if passed else '❌'}")
                if not passed:
                    for path, exists in details.items():
                        if not exists:
                            print(f"      Missing: {path}")

        # Generate summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)

        total_tests = len(self.results)
        passed_tests = sum(1 for v in self.results.values() if v)

        print(f"\nTotal Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")

        # List failures
        failures = [k for k, v in self.results.items() if not v]
        if failures:
            print("\n❌ Failed Tests:")
            for test_name in failures:
                print(f"  - {test_name}")

        # Save results to file
        with open(BASE_DIR / "test_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\n📄 Results saved to test_results.json")

        return passed_tests == total_tests

def main():
    """Main test runner"""
    print("🚀 Starting comprehensive test suite...")
    print("Note: Make sure all backend servers are running on their respective ports")
    print("Step 002: Port 8002")
    print("Step 003: Port 8003")
    print("Step 004: Port 8004")
    print("Step 005: Port 8005")
    print("Step 006: Frontend on 5173")
    print("Step 007: Port 8007")
    print("Step 008: Port 8008")
    print("Step 009: Port 8009")
    print("Step 010: Port 8010")

    input("\nPress Enter to continue...")

    tester = StepTester()
    success = asyncio.run(tester.run_all_tests())

    if success:
        print("\n🎉 ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Review the results above.")
        sys.exit(1)

if __name__ == "__main__":
    main()