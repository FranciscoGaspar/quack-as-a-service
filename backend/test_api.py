#!/usr/bin/env python3
"""
Quick test script to verify the API is working.
Run this after starting the API to test basic functionality.
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint."""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_user_crud():
    """Test user CRUD operations."""
    print("\n🔍 Testing User CRUD...")
    
    # Create user
    user_data = {"name": "Test User"}
    response = requests.post(f"{BASE_URL}/users", json=user_data)
    print(f"Create user: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
        return False
    
    user = response.json()
    user_id = user["id"]
    print(f"Created user: {user}")
    
    # Get user
    response = requests.get(f"{BASE_URL}/users/{user_id}")
    print(f"Get user: {response.status_code}")
    
    # List users
    response = requests.get(f"{BASE_URL}/users")
    print(f"List users: {response.status_code}, count: {len(response.json())}")
    
    # Update user
    update_data = {"name": "Updated User"}
    response = requests.put(f"{BASE_URL}/users/{user_id}", json=update_data)
    print(f"Update user: {response.status_code}")
    
    return True

def test_entry_crud():
    """Test personal entry CRUD operations."""
    print("\n🔍 Testing PersonalEntry CRUD...")
    
    # Create entry
    entry_data = {
        "user_id": 1,
        "room_name": "Test Lab",
        "equipment": {
            "mask": True,
            "right_glove": True,
            "left_glove": False,
            "hairnet": True
        },
        "image_url": "http://example.com/image.jpg"
    }
    
    response = requests.post(f"{BASE_URL}/entries", json=entry_data)
    print(f"Create entry: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
        return False
    
    entry = response.json()
    entry_id = entry["id"]
    print(f"Created entry: {entry}")
    print(f"Compliant: {entry['is_compliant']}")
    print(f"Missing: {entry['missing_equipment']}")
    
    # Get entry
    response = requests.get(f"{BASE_URL}/entries/{entry_id}")
    print(f"Get entry: {response.status_code}")
    
    # List entries
    response = requests.get(f"{BASE_URL}/entries")
    print(f"List entries: {response.status_code}, count: {len(response.json())}")
    
    # Update equipment
    equipment_update = {"left_glove": True}
    response = requests.patch(f"{BASE_URL}/entries/{entry_id}/equipment", json=equipment_update)
    print(f"Update equipment: {response.status_code}")
    if response.status_code == 200:
        updated_entry = response.json()
        print(f"Now compliant: {updated_entry['is_compliant']}")
    
    # Get room entries
    response = requests.get(f"{BASE_URL}/rooms/Test Lab/entries")
    print(f"Room entries: {response.status_code}, count: {len(response.json())}")
    
    return True

def main():
    print("🦆 Testing Quack as a Service API")
    print("=================================")
    
    try:
        # Test health
        if not test_health():
            print("❌ Health check failed!")
            return
        
        # Test user operations
        if not test_user_crud():
            print("❌ User CRUD failed!")
            return
        
        # Test entry operations
        if not test_entry_crud():
            print("❌ Entry CRUD failed!")
            return
        
        print("\n✅ All tests passed!")
        print(f"API Documentation: {BASE_URL}/docs")
        print(f"Health Check: {BASE_URL}/health")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API!")
        print("Make sure the API is running: python run_api.py")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    main()
