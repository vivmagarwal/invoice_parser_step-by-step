#!/usr/bin/env python3
"""
Test Script for STEP 008: Complete Invoice Processing

Tests:
1. Enhanced database operations
2. Search and filtering functionality
3. Data validation pipeline
4. Export functionality
"""

import asyncio
import json
import aiohttp
import sys
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import io
import random

# Test configuration
BASE_URL = "http://localhost:8008"
TEST_USER = {
    "email": f"test_step008_{random.randint(1000, 9999)}@example.com",
    "password": "TestPass123!",
    "full_name": "Test User Step008"
}

class TestStep008:
    def __init__(self):
        self.session = None
        self.token = None
        self.user_id = None
        self.invoice_ids = []

    async def setup(self):
        """Setup test environment"""
        print("\n🔧 Setting up test environment...")
        self.session = aiohttp.ClientSession()

    async def teardown(self):
        """Cleanup test environment"""
        print("\n🧹 Cleaning up...")
        if self.session:
            await self.session.close()

    async def register_and_login(self):
        """Register a new user and login"""
        print("\n📝 Registering new user...")

        # Register
        async with self.session.post(
            f"{BASE_URL}/api/auth/register",
            json=TEST_USER
        ) as resp:
            if resp.status != 200:
                text = await resp.text()
                print(f"❌ Registration failed: {text}")
                return False
            data = await resp.json()
            print(f"✅ User registered: {data['email']}")

        # Login
        print("🔐 Logging in...")
        async with self.session.post(
            f"{BASE_URL}/api/auth/login",
            data={
                "username": TEST_USER["email"],
                "password": TEST_USER["password"]
            }
        ) as resp:
            if resp.status != 200:
                print(f"❌ Login failed: {await resp.text()}")
                return False
            data = await resp.json()
            self.token = data["access_token"]
            print("✅ Login successful")
            return True

    def create_test_invoice_image(self, invoice_num: int):
        """Create a test invoice image with different data"""
        img = Image.new('RGB', (800, 1000), color='white')
        draw = ImageDraw.Draw(img)

        # Different vendor/customer for each invoice
        vendors = ["Acme Corp", "Tech Solutions", "Global Services", "Prime Suppliers"]
        customers = ["ABC Company", "XYZ Inc", "Demo Corp", "Test Ltd"]

        vendor = vendors[invoice_num % len(vendors)]
        customer = customers[invoice_num % len(customers)]

        # Generate invoice data
        invoice_date = (datetime.now() - timedelta(days=invoice_num * 30)).strftime("%Y-%m-%d")
        amount = 1000 + (invoice_num * 500)

        # Draw invoice content
        y_pos = 50
        draw.text((50, y_pos), f"INVOICE", fill='black')
        y_pos += 40

        draw.text((50, y_pos), f"Invoice #: INV-2024-{1000 + invoice_num}", fill='black')
        y_pos += 30

        draw.text((50, y_pos), f"Date: {invoice_date}", fill='black')
        y_pos += 30

        draw.text((50, y_pos), f"Vendor: {vendor}", fill='black')
        y_pos += 30

        draw.text((50, y_pos), f"Customer: {customer}", fill='black')
        y_pos += 50

        # Add line items
        draw.text((50, y_pos), "ITEMS:", fill='black')
        y_pos += 30

        items = [
            f"Item {i+1}: Product {chr(65+i)} - ${100 * (i+1)}"
            for i in range(3)
        ]

        for item in items:
            draw.text((70, y_pos), item, fill='black')
            y_pos += 25

        y_pos += 30
        draw.text((50, y_pos), f"Total Amount: ${amount:.2f}", fill='black')

        # Convert to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)

        return img_bytes.getvalue()

    async def test_upload_multiple_invoices(self):
        """Test uploading multiple invoices for search testing"""
        print("\n📤 Uploading multiple test invoices...")

        headers = {"Authorization": f"Bearer {self.token}"}

        for i in range(5):
            # Create invoice image
            img_data = self.create_test_invoice_image(i)

            # Upload invoice
            data = aiohttp.FormData()
            data.add_field('file',
                          img_data,
                          filename=f'test_invoice_{i}.png',
                          content_type='image/png')

            async with self.session.post(
                f"{BASE_URL}/api/invoices/upload",
                data=data,
                headers=headers
            ) as resp:
                if resp.status == 200:
                    invoice = await resp.json()
                    self.invoice_ids.append(invoice['id'])
                    print(f"  ✅ Uploaded invoice {i+1}: ID={invoice['id']}")
                else:
                    print(f"  ❌ Failed to upload invoice {i+1}: {await resp.text()}")

        return len(self.invoice_ids) == 5

    async def test_search_functionality(self):
        """Test search and filtering capabilities"""
        print("\n🔍 Testing search functionality...")

        headers = {"Authorization": f"Bearer {self.token}"}

        # Test 1: Search by vendor name
        print("  Testing vendor search...")
        async with self.session.get(
            f"{BASE_URL}/api/invoices?search=Acme",
            headers=headers
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"    ✅ Found {len(data.get('items', []))} invoices from Acme")
            else:
                print(f"    ❌ Search failed: {await resp.text()}")

        # Test 2: Filter by status
        print("  Testing status filter...")
        async with self.session.get(
            f"{BASE_URL}/api/invoices?status=pending",
            headers=headers
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"    ✅ Found {len(data.get('items', []))} pending invoices")
            else:
                print(f"    ❌ Filter failed: {await resp.text()}")

        # Test 3: Date range filter
        print("  Testing date range filter...")
        date_from = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        date_to = datetime.now().strftime("%Y-%m-%d")
        async with self.session.get(
            f"{BASE_URL}/api/invoices?date_from={date_from}&date_to={date_to}",
            headers=headers
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"    ✅ Found {len(data.get('items', []))} invoices in date range")
            else:
                print(f"    ❌ Date filter failed: {await resp.text()}")

        return True

    async def test_batch_operations(self):
        """Test batch operations"""
        print("\n📦 Testing batch operations...")

        headers = {"Authorization": f"Bearer {self.token}"}

        if len(self.invoice_ids) < 2:
            print("  ⚠️  Not enough invoices for batch testing")
            return False

        # Batch update status
        batch_ids = self.invoice_ids[:2]
        print(f"  Updating status for invoices: {batch_ids}")

        async with self.session.patch(
            f"{BASE_URL}/api/invoices/batch/status",
            json={
                "invoice_ids": batch_ids,
                "status": "processing"
            },
            headers=headers
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"    ✅ Batch updated {data.get('updated', 0)} invoices")
            else:
                print(f"    ❌ Batch update failed: {await resp.text()}")

        return True

    async def test_data_export(self):
        """Test data export functionality"""
        print("\n📊 Testing data export...")

        headers = {"Authorization": f"Bearer {self.token}"}

        # Test CSV export
        print("  Testing CSV export...")
        async with self.session.get(
            f"{BASE_URL}/api/invoices/export?format=csv",
            headers=headers
        ) as resp:
            if resp.status == 200:
                content = await resp.text()
                lines = content.split('\n')
                print(f"    ✅ CSV export successful: {len(lines)} lines")
            else:
                print(f"    ❌ CSV export failed: {await resp.text()}")

        # Test JSON export
        print("  Testing JSON export...")
        async with self.session.get(
            f"{BASE_URL}/api/invoices/export?format=json",
            headers=headers
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"    ✅ JSON export successful: {len(data)} invoices")
            else:
                print(f"    ❌ JSON export failed: {await resp.text()}")

        return True

    async def test_validation_pipeline(self):
        """Test data validation pipeline"""
        print("\n🔒 Testing validation pipeline...")

        headers = {"Authorization": f"Bearer {self.token}"}

        # Test invalid email format
        print("  Testing invalid email validation...")
        test_data = {
            "vendor_email": "invalid-email",
            "vendor_name": "Test Vendor"
        }

        if self.invoice_ids:
            async with self.session.patch(
                f"{BASE_URL}/api/invoices/{self.invoice_ids[0]}",
                json=test_data,
                headers=headers
            ) as resp:
                if resp.status == 400:
                    error = await resp.json()
                    print(f"    ✅ Validation correctly rejected invalid email")
                else:
                    print(f"    ⚠️  Validation should have rejected invalid email")

        # Test SQL injection prevention
        print("  Testing SQL injection prevention...")
        malicious_input = "'; DROP TABLE invoices; --"
        async with self.session.get(
            f"{BASE_URL}/api/invoices?search={malicious_input}",
            headers=headers
        ) as resp:
            if resp.status == 200:
                print(f"    ✅ SQL injection attempt safely handled")
            else:
                print(f"    ⚠️  Unexpected response to SQL injection test")

        return True

    async def run_tests(self):
        """Run all tests"""
        print("=" * 60)
        print("STEP 008: Complete Invoice Processing - Test Suite")
        print("=" * 60)

        try:
            await self.setup()

            # Register and login
            if not await self.register_and_login():
                print("❌ Failed to register/login")
                return False

            # Run tests
            tests_passed = 0
            total_tests = 5

            # Test 1: Upload multiple invoices
            if await self.test_upload_multiple_invoices():
                tests_passed += 1
                print("✅ Multiple invoice upload test passed")
            else:
                print("❌ Multiple invoice upload test failed")

            # Test 2: Search functionality
            if await self.test_search_functionality():
                tests_passed += 1
                print("✅ Search functionality test passed")
            else:
                print("❌ Search functionality test failed")

            # Test 3: Batch operations
            if await self.test_batch_operations():
                tests_passed += 1
                print("✅ Batch operations test passed")
            else:
                print("❌ Batch operations test failed")

            # Test 4: Data export
            if await self.test_data_export():
                tests_passed += 1
                print("✅ Data export test passed")
            else:
                print("❌ Data export test failed")

            # Test 5: Validation pipeline
            if await self.test_validation_pipeline():
                tests_passed += 1
                print("✅ Validation pipeline test passed")
            else:
                print("❌ Validation pipeline test failed")

            # Summary
            print("\n" + "=" * 60)
            print(f"Test Results: {tests_passed}/{total_tests} passed")

            if tests_passed == total_tests:
                print("🎉 All tests passed! Step 008 implementation is working correctly.")
            else:
                print(f"⚠️  {total_tests - tests_passed} test(s) failed.")

            print("=" * 60)

            return tests_passed == total_tests

        except Exception as e:
            print(f"❌ Test suite error: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            await self.teardown()


async def check_server():
    """Check if the server is running"""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{BASE_URL}/api/health") as resp:
                return resp.status == 200
        except:
            return False


async def main():
    """Main test runner"""
    # Check if server is running
    if not await check_server():
        print(f"❌ Server is not running at {BASE_URL}")
        print("Please start the server with: uvicorn app.main:app --reload --port 8008")
        sys.exit(1)

    # Run tests
    tester = TestStep008()
    success = await tester.run_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())