#!/usr/bin/env python3
"""Test script for file upload functionality."""

import requests
import os
from pathlib import Path
from PIL import Image
import io

# Configuration
BASE_URL = "http://localhost:8006"

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*50)
    print(f" {title}")
    print("="*50)


def create_sample_image(filename="sample_invoice.jpg"):
    """Create a sample image file for testing."""
    # Create a simple image with PIL
    img = Image.new('RGB', (800, 600), color='white')
    img.save(filename)
    return filename


def register_and_login():
    """Register a test user and get auth token."""
    print_section("Authentication Setup")

    # Register
    register_url = f"{BASE_URL}/api/auth/register"
    register_data = {
        "email": "filetest@example.com",
        "username": "filetester",
        "password": "TestPassword123!",
        "full_name": "File Test User",
        "is_active": True,
        "is_superuser": False
    }

    print("Registering test user...")
    response = requests.post(register_url, json=register_data)
    if response.status_code != 200:
        print(f"Note: User may already exist ({response.status_code})")

    # Login
    login_url = f"{BASE_URL}/api/auth/login"
    login_data = {
        "username": "filetest@example.com",
        "password": "TestPassword123!"
    }

    print("Logging in...")
    response = requests.post(login_url, data=login_data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Authentication successful!")
        return token
    else:
        print(f"❌ Login failed: {response.text}")
        return None


def test_file_upload(token, file_path):
    """Test file upload functionality."""
    print_section("Testing File Upload")

    url = f"{BASE_URL}/api/invoices/upload"
    headers = {"Authorization": f"Bearer {token}"}

    with open(file_path, "rb") as f:
        files = {"file": (file_path, f, "image/jpeg")}
        print(f"Uploading file: {file_path}")
        response = requests.post(url, files=files, headers=headers)

    if response.status_code == 200:
        print("✅ File uploaded successfully!")
        invoice = response.json()
        print(f"Invoice ID: {invoice['id']}")
        print(f"Filename: {invoice['filename']}")
        print(f"Original filename: {invoice['original_filename']}")
        print(f"File size: {invoice['file_size']} bytes")
        print(f"Status: {invoice['status']}")
        return invoice['id']
    else:
        print(f"❌ Upload failed: {response.status_code}")
        print(f"Error: {response.text}")
        return None


def test_get_invoices(token):
    """Test getting list of invoices."""
    print_section("Testing Get Invoices List")

    url = f"{BASE_URL}/api/invoices/"
    headers = {"Authorization": f"Bearer {token}"}

    print("Getting invoices list...")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("✅ Successfully retrieved invoices!")
        data = response.json()
        print(f"Total invoices: {data['total']}")
        for invoice in data['invoices']:
            print(f"  - ID: {invoice['id']}, File: {invoice['original_filename']}, Status: {invoice['status']}")
        return True
    else:
        print(f"❌ Failed to get invoices: {response.status_code}")
        print(f"Error: {response.text}")
        return False


def test_get_single_invoice(token, invoice_id):
    """Test getting a single invoice."""
    print_section("Testing Get Single Invoice")

    url = f"{BASE_URL}/api/invoices/{invoice_id}"
    headers = {"Authorization": f"Bearer {token}"}

    print(f"Getting invoice {invoice_id}...")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("✅ Successfully retrieved invoice!")
        invoice = response.json()
        print(f"Invoice ID: {invoice['id']}")
        print(f"Status: {invoice['status']}")
        print(f"Created at: {invoice['created_at']}")
        return True
    else:
        print(f"❌ Failed to get invoice: {response.status_code}")
        print(f"Error: {response.text}")
        return False


def test_delete_invoice(token, invoice_id):
    """Test deleting an invoice."""
    print_section("Testing Delete Invoice")

    url = f"{BASE_URL}/api/invoices/{invoice_id}"
    headers = {"Authorization": f"Bearer {token}"}

    print(f"Deleting invoice {invoice_id}...")
    response = requests.delete(url, headers=headers)

    if response.status_code == 200:
        print("✅ Invoice deleted successfully!")
        return True
    else:
        print(f"❌ Failed to delete invoice: {response.status_code}")
        print(f"Error: {response.text}")
        return False


def test_invalid_file_type(token):
    """Test uploading invalid file type."""
    print_section("Testing Invalid File Type")

    # Create a text file
    txt_file = "test.txt"
    with open(txt_file, "w") as f:
        f.write("This is not an invoice image")

    url = f"{BASE_URL}/api/invoices/upload"
    headers = {"Authorization": f"Bearer {token}"}

    with open(txt_file, "rb") as f:
        files = {"file": (txt_file, f, "text/plain")}
        print(f"Attempting to upload invalid file: {txt_file}")
        response = requests.post(url, files=files, headers=headers)

    os.remove(txt_file)

    if response.status_code == 400:
        print("✅ Correctly rejected invalid file type!")
        print(f"Error message: {response.json()['detail']}")
        return True
    else:
        print(f"❌ Unexpected response: {response.status_code}")
        return False


def test_unauthorized_access():
    """Test accessing protected routes without token."""
    print_section("Testing Unauthorized Access")

    url = f"{BASE_URL}/api/invoices/"

    print("Attempting to access invoices without authentication...")
    response = requests.get(url)

    if response.status_code == 401:
        print("✅ Correctly rejected unauthorized access!")
        return True
    else:
        print(f"❌ Unexpected response: {response.status_code}")
        return False


def main():
    """Run all file upload tests."""
    print("\n" + "📁"*20)
    print(" File Upload Test Suite")
    print("📁"*20)

    # Create sample image
    sample_file = create_sample_image()

    try:
        # Get authentication token
        token = register_and_login()
        if not token:
            print("\n⚠️  Cannot continue without authentication")
            return

        # Run tests
        invoice_id = test_file_upload(token, sample_file)
        if invoice_id:
            test_get_single_invoice(token, invoice_id)

        test_get_invoices(token)

        if invoice_id:
            test_delete_invoice(token, invoice_id)

        test_invalid_file_type(token)
        test_unauthorized_access()

        print_section("Test Suite Complete")
        print("\n✨ File upload functionality has been tested!")

    finally:
        # Clean up sample file
        if os.path.exists(sample_file):
            os.remove(sample_file)
            print(f"\nCleaned up test file: {sample_file}")


if __name__ == "__main__":
    # Check if PIL is installed
    try:
        from PIL import Image
        main()
    except ImportError:
        print("Please install Pillow: pip install Pillow")
        print("For now, let's create a simple test without image generation...")

        # Simple fallback test
        token = register_and_login()
        if token:
            test_get_invoices(token)
            test_unauthorized_access()