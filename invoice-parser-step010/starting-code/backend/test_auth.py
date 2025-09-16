#!/usr/bin/env python3
"""Test script for JWT authentication flow."""

import requests
import json
import random
import string

# Configuration
BASE_URL = "http://localhost:8005"

# Generate unique test data
unique_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
test_email = f"testuser_{unique_suffix}@example.com"
test_username = f"testuser_{unique_suffix}"
test_password = "SecurePassword123!"


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*50)
    print(f" {title}")
    print("="*50)


def test_register():
    """Test user registration."""
    print_section("Testing User Registration")

    url = f"{BASE_URL}/api/auth/register"
    data = {
        "email": test_email,
        "username": test_username,
        "password": test_password,
        "full_name": "Test User",
        "is_active": True,
        "is_superuser": False
    }

    print(f"Registering user: {test_email}")
    response = requests.post(url, json=data)

    if response.status_code == 200:
        print("✅ Registration successful!")
        user = response.json()
        print(f"User ID: {user['id']}")
        print(f"Username: {user['username']}")
        return user
    else:
        print(f"❌ Registration failed: {response.status_code}")
        print(f"Error: {response.text}")
        return None


def test_login():
    """Test user login and token generation."""
    print_section("Testing User Login")

    url = f"{BASE_URL}/api/auth/login"

    # OAuth2PasswordRequestForm expects form data, not JSON
    data = {
        "username": test_email,  # Can be email or username
        "password": test_password
    }

    print(f"Logging in as: {test_email}")
    response = requests.post(url, data=data)  # Note: data, not json

    if response.status_code == 200:
        print("✅ Login successful!")
        token_data = response.json()
        print(f"Token type: {token_data['token_type']}")
        print(f"Access token (first 20 chars): {token_data['access_token'][:20]}...")
        return token_data['access_token']
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"Error: {response.text}")
        return None


def test_get_current_user(token):
    """Test getting current user info with token."""
    print_section("Testing Get Current User")

    url = f"{BASE_URL}/api/auth/me"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    print("Getting current user info with token...")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("✅ Successfully retrieved user info!")
        user = response.json()
        print(f"User ID: {user['id']}")
        print(f"Email: {user['email']}")
        print(f"Username: {user['username']}")
        return user
    else:
        print(f"❌ Failed to get user info: {response.status_code}")
        print(f"Error: {response.text}")
        return None


def test_protected_route(token, user_id):
    """Test accessing a protected route."""
    print_section("Testing Protected Route (Update User)")

    url = f"{BASE_URL}/api/users/{user_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "full_name": "Updated Test User"
    }

    print(f"Updating user {user_id} (protected route)...")
    response = requests.put(url, json=data, headers=headers)

    if response.status_code == 200:
        print("✅ Successfully accessed protected route!")
        user = response.json()
        print(f"Updated full name: {user['full_name']}")
        return True
    else:
        print(f"❌ Failed to access protected route: {response.status_code}")
        print(f"Error: {response.text}")
        return False


def test_unauthorized_access():
    """Test accessing protected route without token."""
    print_section("Testing Unauthorized Access")

    url = f"{BASE_URL}/api/auth/me"

    print("Attempting to access protected route without token...")
    response = requests.get(url)

    if response.status_code == 401:
        print("✅ Correctly rejected unauthorized access!")
        return True
    else:
        print(f"❌ Unexpected response: {response.status_code}")
        print(f"Response: {response.text}")
        return False


def main():
    """Run all authentication tests."""
    print("\n" + "🔐"*20)
    print(" JWT Authentication Test Suite")
    print("🔐"*20)

    # Test registration
    user = test_register()
    if not user:
        print("\n⚠️  Cannot continue without successful registration")
        return

    # Test login
    token = test_login()
    if not token:
        print("\n⚠️  Cannot continue without successful login")
        return

    # Test getting current user
    current_user = test_get_current_user(token)
    if not current_user:
        print("\n⚠️  Cannot retrieve current user")

    # Test protected route
    if current_user:
        test_protected_route(token, current_user['id'])

    # Test unauthorized access
    test_unauthorized_access()

    print_section("Test Suite Complete")
    print("\n✨ All authentication flows have been tested!")


if __name__ == "__main__":
    main()