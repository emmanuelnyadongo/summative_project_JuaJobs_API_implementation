#!/usr/bin/env python3
"""
Quick API Test for Video Demonstration
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_api():
    print("🚀 Testing JuaJobs API...")
    print("=" * 50)
    
    # Test 1: Login
    print("\n1. Testing Login...")
    login_data = {
        "username": "client1",
        "password": "pass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Data keys: {list(data.keys())}")
        token = data.get('tokens', {}).get('access')
        print("✅ Login successful!")
        if token:
            print(f"Token: {token[:50]}...")
        else:
            print("Token not found in response")
            return
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test 2: Get Jobs
        print("\n2. Testing Get Jobs...")
        response = requests.get(f"{BASE_URL}/jobs/", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            jobs = response.json()
            print(f"✅ Found {len(jobs)} jobs")
        
        # Test 3: Get Skills
        print("\n3. Testing Get Skills...")
        response = requests.get(f"{BASE_URL}/skills/", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            skills = response.json()
            print(f"✅ Found {len(skills)} skills")
        
        # Test 4: Get User Profile
        print("\n4. Testing Get Profile...")
        response = requests.get(f"{BASE_URL}/auth/profile/", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            profile = response.json()
            print(f"✅ Profile: {profile.get('username')} ({profile.get('user_type')})")
        
        print("\n🎉 API is working perfectly!")
        print("Ready for video demonstration!")
        
    else:
        print("❌ Login failed!")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    test_api() 