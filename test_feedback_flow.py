#!/usr/bin/env python3
"""
Test the complete feedback flow for AI Interview Platform
Tests Round 0 → Round 1 → Feedback Chat
"""

import requests
import json
import os
import time
import random

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

def test_round0_registration():
    """Test Round 0 candidate registration"""
    try:
        # Create a dummy PDF file for testing
        test_file_path = "test_resume.pdf"
        with open(test_file_path, "wb") as f:
            # Create a minimal PDF header
            f.write(b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n")
        
        # Test the registration endpoint
        files = {"resume": open(test_file_path, "rb")}
        data = {
            "full_name": "Test Candidate",
            "email": "test@example.com",
            "technology_track": "python"
        }
        
        response = requests.post("http://localhost:8000/start-interview", files=files, data=data)
        files["resume"].close()
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Round 0 registration test passed")
            print(f"   Response: {result}")
            return True
        else:
            print(f"❌ Round 0 registration test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Round 0 registration test failed: {e}")
        return False
    finally:
        # Clean up test file
        if os.path.exists("test_resume.pdf"):
            os.remove("test_resume.pdf")

def test_round1_questions():
    """Test Round 1 question fetching"""
    try:
        response = requests.get("http://localhost:8000/round1-questions?email=test@example.com")
        
        if response.status_code == 200:
            questions = response.json()
            if isinstance(questions, list) and len(questions) > 0:
                print(f"✅ Round 1 questions test passed - {len(questions)} questions loaded")
                print(f"   Sample question: {questions[0].get('question_text', 'N/A')[:50]}...")
                return True
            else:
                print("❌ Round 1 questions test failed - no questions returned")
                return False
        else:
            print(f"❌ Round 1 questions test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Round 1 questions test failed: {e}")
        return False

def test_round1_submission():
    """Test Round 1 answer submission"""
    try:
        # Create mock answers
        mock_answers = {
            "1": "A",
            "2": "B", 
            "3": "C",
            "4": "D",
            "5": "A",
            "6": "B",
            "7": "C",
            "8": "D",
            "9": "A",
            "10": "B"
        }
        
        data = {
            "email": "test@example.com",
            "answers": mock_answers,
            "duration": 1200  # 20 minutes
        }
        
        response = requests.post("http://localhost:8000/round1-submit", 
                              json=data,
                              headers={"Content-Type": "application/json"})
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Round 1 submission test passed")
            print(f"   Result: {result}")
            return result  # Return the result for feedback testing
        else:
            print(f"❌ Round 1 submission test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Round 1 submission test failed: {e}")
        return None

def test_feedback_chat(assessment_result):
    """Test the AI feedback chat functionality"""
    try:
        # Test different types of feedback requests
        test_messages = [
            "How can I improve my performance?",
            "What are my next steps?",
            "Tell me about my career options",
            "Analyze my performance"
        ]
        
        for message in test_messages:
            data = {
                "message": message,
                "assessment_result": assessment_result,
                "conversation_history": []
            }
            
            response = requests.post("http://localhost:8000/feedback-chat",
                                  json=data,
                                  headers={"Content-Type": "application/json"})
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Feedback chat test passed for: '{message[:30]}...'")
                print(f"   Response length: {len(result.get('response', ''))} characters")
            else:
                print(f"❌ Feedback chat test failed for: '{message[:30]}...'")
                print(f"   Status: {response.status_code}")
                return False
        
        print("✅ All feedback chat tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Feedback chat test failed: {e}")
        return False

def test_anticheat_logging():
    """Test anti-cheat event logging"""
    try:
        data = {
            "email": "test@example.com",
            "event_type": "blur"
        }
        
        response = requests.post("http://localhost:8000/round1-log",
                            json=data,
                            headers={"Content-Type": "application/json"})
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Anti-cheat logging test passed")
            print(f"   Response: {result}")
            return True
        else:
            print(f"❌ Anti-cheat logging test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Anti-cheat logging test failed: {e}")
        return False

def main():
    print("🧪 Complete Feedback Flow Test for AI Interview Platform")
    print("=" * 70)
    
    tests = [
        ("Backend Health", test_backend_health),
        ("Frontend Access", test_frontend),
        ("Round 0 Registration", test_round0_registration),
        ("Round 1 Questions", test_round1_questions),
        ("Anti-cheat Logging", test_anticheat_logging)
    ]
    
    results = []
    
    # Run basic tests first
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Test Round 1 submission and get results
    print(f"\n🔍 Testing Round 1 Submission...")
    assessment_result = test_round1_submission()
    if assessment_result:
        results.append(("Round 1 Submission", True))
        
        # Test feedback chat with the assessment results
        print(f"\n🔍 Testing AI Feedback Chat...")
        feedback_success = test_feedback_chat(assessment_result)
        results.append(("AI Feedback Chat", feedback_success))
    else:
        results.append(("Round 1 Submission", False))
        results.append(("AI Feedback Chat", False))
    
    print("\n" + "=" * 70)
    print("📊 Complete Test Results:")
    print("=" * 70)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {test_name:<25} {status}")
        if success:
            passed += 1
    
    print("=" * 70)
    print(f"📈 Summary: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 ALL TESTS PASSED! Your complete feedback flow is working!")
        print("   🚀 Complete flow: Round 0 → Round 1 → AI Feedback Chat")
        print("   🤖 AI feedback system is fully functional")
        print("   📱 Ready for demo: http://localhost:3000")
        print("\n💡 Demo Flow:")
        print("   1. Fill out registration form")
        print("   2. Complete Round 1 assessment")
        print("   3. Chat with AI for personalized feedback")
        print("   4. Get career advice based on your performance")
    else:
        print(f"\n⚠️  {len(results) - passed} tests failed. Please check the issues above.")
        print("\nTroubleshooting:")
        print("   1. Make sure both servers are running")
        print("   2. Check database connection (or use mock data)")
        print("   3. Verify all dependencies are installed")
        print("   4. Check server logs for errors")

if __name__ == "__main__":
    main()
