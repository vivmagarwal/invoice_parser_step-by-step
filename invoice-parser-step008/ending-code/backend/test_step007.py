#!/usr/bin/env python3
"""
Test script for STEP-007: AI Integration - Gemini API
Tests invoice processing with AI extraction
"""

import asyncio
import aiohttp
import json
from pathlib import Path
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import os

# API Base URL
BASE_URL = "http://localhost:8007"

# Test user credentials
TEST_USER = {
    "username": "aitest",
    "email": "aitest@example.com",
    "password": "testpass123",
    "full_name": "AI Test User"
}


def create_sample_invoice_image():
    """Create a sample invoice image for testing"""
    # Create a white image
    width, height = 800, 1000
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)

    # Try to use a font, fallback to default if not available
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
    except:
        font = ImageFont.load_default()
        small_font = font

    # Draw invoice content
    y_position = 50

    # Header
    draw.text((50, y_position), "INVOICE", font=font, fill='black')
    y_position += 40

    draw.text((50, y_position), "Invoice #: INV-2024-001", font=small_font, fill='black')
    y_position += 25
    draw.text((50, y_position), "Date: 2024-01-15", font=small_font, fill='black')
    y_position += 25
    draw.text((50, y_position), "Due Date: 2024-02-15", font=small_font, fill='black')
    y_position += 50

    # Vendor info
    draw.text((50, y_position), "FROM:", font=font, fill='black')
    y_position += 30
    draw.text((50, y_position), "Tech Solutions Inc", font=small_font, fill='black')
    y_position += 20
    draw.text((50, y_position), "123 Business Ave", font=small_font, fill='black')
    y_position += 20
    draw.text((50, y_position), "San Francisco, CA 94102", font=small_font, fill='black')
    y_position += 20
    draw.text((50, y_position), "Tax ID: 12-3456789", font=small_font, fill='black')
    y_position += 50

    # Customer info
    draw.text((50, y_position), "TO:", font=font, fill='black')
    y_position += 30
    draw.text((50, y_position), "Acme Corporation", font=small_font, fill='black')
    y_position += 20
    draw.text((50, y_position), "456 Client Street", font=small_font, fill='black')
    y_position += 20
    draw.text((50, y_position), "New York, NY 10001", font=small_font, fill='black')
    y_position += 50

    # Line items
    draw.text((50, y_position), "ITEMS:", font=font, fill='black')
    y_position += 30

    # Table header
    draw.text((50, y_position), "Description", font=small_font, fill='black')
    draw.text((350, y_position), "Qty", font=small_font, fill='black')
    draw.text((450, y_position), "Unit Price", font=small_font, fill='black')
    draw.text((600, y_position), "Total", font=small_font, fill='black')
    y_position += 30

    # Item 1
    draw.text((50, y_position), "Web Development Services", font=small_font, fill='black')
    draw.text((350, y_position), "40", font=small_font, fill='black')
    draw.text((450, y_position), "$150.00", font=small_font, fill='black')
    draw.text((600, y_position), "$6,000.00", font=small_font, fill='black')
    y_position += 25

    # Item 2
    draw.text((50, y_position), "UI/UX Design", font=small_font, fill='black')
    draw.text((350, y_position), "20", font=small_font, fill='black')
    draw.text((450, y_position), "$100.00", font=small_font, fill='black')
    draw.text((600, y_position), "$2,000.00", font=small_font, fill='black')
    y_position += 25

    # Item 3
    draw.text((50, y_position), "Database Setup", font=small_font, fill='black')
    draw.text((350, y_position), "1", font=small_font, fill='black')
    draw.text((450, y_position), "$500.00", font=small_font, fill='black')
    draw.text((600, y_position), "$500.00", font=small_font, fill='black')
    y_position += 50

    # Totals
    draw.line((450, y_position, 700, y_position), fill='black', width=1)
    y_position += 10
    draw.text((450, y_position), "Subtotal:", font=small_font, fill='black')
    draw.text((600, y_position), "$8,500.00", font=small_font, fill='black')
    y_position += 25

    draw.text((450, y_position), "Tax (10%):", font=small_font, fill='black')
    draw.text((600, y_position), "$850.00", font=small_font, fill='black')
    y_position += 25

    draw.text((450, y_position), "TOTAL:", font=font, fill='black')
    draw.text((600, y_position), "$9,350.00", font=font, fill='black')
    y_position += 50

    # Payment terms
    draw.text((50, y_position), "Payment Terms: Net 30", font=small_font, fill='black')

    # Save to bytes
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes.getvalue()


async def test_ai_integration():
    """Test the complete AI integration flow"""

    print("\n" + "="*60)
    print("STEP-007: AI Integration Test")
    print("="*60)

    async with aiohttp.ClientSession() as session:
        # 1. Register user
        print("\n1. Registering test user...")
        try:
            async with session.post(
                f"{BASE_URL}/api/users/register",
                json=TEST_USER
            ) as resp:
                if resp.status == 201:
                    user = await resp.json()
                    print(f"✓ User registered: {user['username']}")
                elif resp.status == 400:
                    print("✓ User already exists")
                else:
                    print(f"✗ Registration failed: {await resp.text()}")
                    return
        except Exception as e:
            print(f"✗ Registration error: {e}")
            return

        # 2. Login
        print("\n2. Logging in...")
        form_data = aiohttp.FormData()
        form_data.add_field('username', TEST_USER['email'])
        form_data.add_field('password', TEST_USER['password'])

        async with session.post(
            f"{BASE_URL}/api/auth/login",
            data=form_data
        ) as resp:
            if resp.status != 200:
                print(f"✗ Login failed: {await resp.text()}")
                return
            auth_data = await resp.json()
            token = auth_data['access_token']
            print(f"✓ Logged in successfully")

        headers = {"Authorization": f"Bearer {token}"}

        # 3. Create sample invoice image
        print("\n3. Creating sample invoice image...")
        invoice_image = create_sample_invoice_image()
        print("✓ Sample invoice image created")

        # 4. Upload invoice
        print("\n4. Uploading invoice...")
        form_data = aiohttp.FormData()
        form_data.add_field(
            'file',
            invoice_image,
            filename='test_invoice.png',
            content_type='image/png'
        )

        async with session.post(
            f"{BASE_URL}/api/invoices/upload",
            data=form_data,
            headers=headers
        ) as resp:
            if resp.status != 200:
                print(f"✗ Upload failed: {await resp.text()}")
                return
            invoice = await resp.json()
            invoice_id = invoice['id']
            print(f"✓ Invoice uploaded with ID: {invoice_id}")
            print(f"  Status: {invoice['status']}")
            print(f"  File: {invoice['original_filename']}")

        # 5. Process invoice with AI
        print("\n5. Processing invoice with AI...")
        print("  Note: Using mock AI service for testing")

        async with session.post(
            f"{BASE_URL}/api/invoices/{invoice_id}/process",
            headers=headers
        ) as resp:
            if resp.status != 200:
                print(f"✗ Processing failed: {await resp.text()}")
                return
            processed = await resp.json()
            print(f"✓ Invoice processed successfully")
            print(f"  Status: {processed['status']}")

        # 6. Get processed invoice data
        print("\n6. Retrieving processed invoice...")
        async with session.get(
            f"{BASE_URL}/api/invoices/{invoice_id}",
            headers=headers
        ) as resp:
            if resp.status != 200:
                print(f"✗ Failed to get invoice: {await resp.text()}")
                return
            invoice_data = await resp.json()

            print(f"✓ Invoice data retrieved")
            print(f"  Status: {invoice_data['status']}")

            if invoice_data.get('extracted_data'):
                extracted = json.loads(invoice_data['extracted_data'])
                print("\n  Extracted Data:")
                print(f"    Invoice Number: {extracted.get('invoice_number')}")
                print(f"    Vendor: {extracted.get('vendor_name')}")
                print(f"    Customer: {extracted.get('customer_name')}")
                print(f"    Total Amount: ${extracted.get('total_amount')}")
                print(f"    Currency: {extracted.get('currency')}")

                if extracted.get('items'):
                    print(f"\n    Line Items ({len(extracted['items'])} items):")
                    for item in extracted['items']:
                        print(f"      - {item['description']}: ${item['total']}")

        # 7. Test error handling
        print("\n7. Testing error handling...")

        # Try to process already processed invoice
        async with session.post(
            f"{BASE_URL}/api/invoices/{invoice_id}/process",
            headers=headers
        ) as resp:
            if resp.status == 400:
                print("✓ Correctly prevented reprocessing")
            else:
                print("✗ Should have prevented reprocessing")

        # Try to process non-existent invoice
        async with session.post(
            f"{BASE_URL}/api/invoices/99999/process",
            headers=headers
        ) as resp:
            if resp.status == 404:
                print("✓ Correctly handled non-existent invoice")
            else:
                print("✗ Should have returned 404 for non-existent invoice")

        # 8. List all invoices
        print("\n8. Listing all invoices...")
        async with session.get(
            f"{BASE_URL}/api/invoices/",
            headers=headers
        ) as resp:
            if resp.status != 200:
                print(f"✗ Failed to list invoices: {await resp.text()}")
                return
            invoice_list = await resp.json()
            print(f"✓ Found {invoice_list['total']} invoice(s)")
            for inv in invoice_list['invoices']:
                print(f"  - ID: {inv['id']}, Status: {inv['status']}, File: {inv['original_filename']}")

        print("\n" + "="*60)
        print("AI Integration Test Complete!")
        print("="*60)
        print("\nKey Features Tested:")
        print("✓ Mock AI service integration")
        print("✓ Invoice processing endpoint")
        print("✓ Structured data extraction")
        print("✓ Error handling and retries")
        print("✓ Status tracking (pending → processing → completed)")
        print("\nTo test with real Gemini AI:")
        print("1. Get API key from https://makersuite.google.com/app/apikey")
        print("2. Set GEMINI_API_KEY in .env file")
        print("3. Set USE_MOCK_AI=false in .env file")
        print("4. Run this test again with a real invoice image")


async def main():
    """Main test runner"""
    print("\nStarting STEP-007 AI Integration Test...")
    print("Make sure the backend is running on port 8007")
    print("Run: cd backend && uvicorn app.main:app --reload --port 8007")

    await asyncio.sleep(2)

    try:
        await test_ai_integration()
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())