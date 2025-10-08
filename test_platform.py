#!/usr/bin/env python3
"""
Test script for the AI Interview Platform
Run this to verify your setup is working correctly
"""

import requests
import json
import os
import time

def test_backend_health():
    """Test if backend is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running and healthy")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running. Please start it with: uvicorn main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return False

def test_frontend():
    """Test if frontend is accessible"""
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is running")
            return True
        else:
            print(f"❌ Frontend check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Frontend is not running. Please start it with: npm run dev")
        return False
    except Exception as e:
        print(f"❌ Frontend test failed: {e}")
        return False

def test_file_upload():
    """Test file upload functionality"""
    try:
        # Create a dummy PDF file for testing
        test_file_path = "test_resume.pdf"
        with open(test_file_path, "wb") as f:
            # Create a minimal PDF header
            f.write(b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n")
        
        # Test the upload endpoint
        files = {"resume": open(test_file_path, "rb")}
        data = {
            "full_name": "Test User",
            "email": "test@example.com",
            "technology_track": "python"
        }
        
        response = requests.post("http://localhost:8000/start-interview", files=files, data=data)
        files["resume"].close()
        
        if response.status_code == 200:
            result = response.json()
            print("✅ File upload test passed")
            print(f"   Response: {result}")
            return True
        else:
            print(f"❌ File upload test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ File upload test failed: {e}")
        return False
    finally:
        # Clean up test file
        if os.path.exists("test_resume.pdf"):
            os.remove("test_resume.pdf")

def main():
    print("🧪 Testing AI Interview Platform")
    print("=" * 50)
    
    # Test backend
    backend_ok = test_backend_health()
    
    # Test frontend
    frontend_ok = test_frontend()
    
    # Test file upload if backend is running
    upload_ok = False
    if backend_ok:
        upload_ok = test_file_upload()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Backend: {'✅ PASS' if backend_ok else '❌ FAIL'}")
    print(f"   Frontend: {'✅ PASS' if frontend_ok else '❌ FAIL'}")
    print(f"   File Upload: {'✅ PASS' if upload_ok else '❌ FAIL'}")
    
    if backend_ok and frontend_ok and upload_ok:
        print("\n🎉 All tests passed! Your platform is ready for demo.")
        print("   Visit: http://localhost:3000")
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")
        print("\nTo start the servers:")
        print("   Backend: cd backend && uvicorn main:app --reload")
        print("   Frontend: cd frontend && npm run dev")

if __name__ == "__main__":
    main()
