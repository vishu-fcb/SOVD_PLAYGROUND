#!/usr/bin/env python3
"""Test script for SOVD token service JWT validation."""

import requests
import json
import jwt

def test_token_generation():
    url = "http://localhost:8000/token"
    
    payload = {
        "user_id": "user:tech123",
        "vin": "WVWZZZ1JZXW000000",
        "issuer": "https://auth.oem.example.com",
        "audience": "sovd-api",
        "roles": ["Workshop_Tech"],
        "actions": ["readDTC", "execRoutine"],
        "expires_in": 3600
    }
    
    print("Requesting token:")
    print(json.dumps(payload, indent=2))
    print()
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        token = data["access_token"]
        
        print("Token generated")
        print("First 100 chars:", token[:100] + "...")
        print()
        
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        print("Decoded payload:")
        print(json.dumps(decoded, indent=2))
        print()
        
        expected_fields = {
            "iss": "https://auth.oem.example.com",
            "sub": "user:tech123",
            "aud": "sovd-api",
            "roles": ["Workshop_Tech"]
        }
        
        print("Verification:")
        all_valid = True
        for field, expected_value in expected_fields.items():
            actual_value = decoded.get(field)
            if actual_value == expected_value:
                print(f"  OK {field}: {actual_value}")
            else:
                print(f"  FAIL {field}: expected {expected_value}, got {actual_value}")
                all_valid = False
        
        if "authorization_details" in decoded:
            auth_details = decoded["authorization_details"][0]
            print(f"  OK authorization_details.type: {auth_details.get('type')}")
            print(f"  OK authorization_details.resources: {auth_details.get('resources')}")
            print(f"  OK authorization_details.actions: {auth_details.get('actions')}")
        else:
            print("  FAIL authorization_details missing")
            all_valid = False
        
        print()
        if all_valid:
            print("All checks passed")
        else:
            print("Some checks failed")
            
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_token_generation()
