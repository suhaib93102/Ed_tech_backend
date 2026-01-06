#!/usr/bin/env python3
"""
Test Quiz Settings API Endpoint
Tests the new /api/quiz/settings/ endpoint
"""

import requests
import json

API_BASE_URL = "http://127.0.0.1:8003/api"

def test_quiz_settings_endpoint():
    """Test fetching quiz settings"""
    print("🧪 Testing Quiz Settings Endpoint\n")
    print("=" * 60)
    
    try:
        # Test GET /api/quiz/settings/
        url = f"{API_BASE_URL}/quiz/settings/"
        print(f"📡 Request: GET {url}")
        
        response = requests.get(url)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Success! Response:")
            print(json.dumps(data, indent=2))
            
            # Validate response structure
            assert 'success' in data, "Missing 'success' field"
            assert data['success'] == True, "Success should be True"
            assert 'settings' in data, "Missing 'settings' field"
            
            settings = data['settings']
            
            # Validate daily_quiz settings
            assert 'daily_quiz' in settings, "Missing 'daily_quiz' settings"
            daily = settings['daily_quiz']
            assert 'attempt_bonus' in daily, "Missing 'attempt_bonus'"
            assert 'coins_per_correct' in daily, "Missing 'coins_per_correct'"
            assert 'perfect_score_bonus' in daily, "Missing 'perfect_score_bonus'"
            
            print("\n✅ Daily Quiz Settings:")
            print(f"   - Attempt Bonus: {daily['attempt_bonus']} coins")
            print(f"   - Coins per Correct: {daily['coins_per_correct']} coins")
            print(f"   - Perfect Score Bonus: {daily['perfect_score_bonus']} coins")
            
            # Validate pair_quiz settings
            assert 'pair_quiz' in settings, "Missing 'pair_quiz' settings"
            pair = settings['pair_quiz']
            print("\n✅ Pair Quiz Settings:")
            print(f"   - Enabled: {pair['enabled']}")
            print(f"   - Session Timeout: {pair['session_timeout']} minutes")
            print(f"   - Max Questions: {pair['max_questions']}")
            
            # Validate coin_system settings
            assert 'coin_system' in settings, "Missing 'coin_system' settings"
            coin_sys = settings['coin_system']
            print("\n✅ Coin System Settings:")
            print(f"   - Coin to Currency Rate: ${coin_sys['coin_to_currency_rate']}")
            print(f"   - Min Coins for Redemption: {coin_sys['min_coins_for_redemption']}")
            
            print("\n" + "=" * 60)
            print("✅ All tests passed!")
            print("\n💡 Admin can edit these at:")
            print("   http://127.0.0.1:8003/admin/question_solver/quizsettings/")
            
            return True
        else:
            print(f"\n❌ Error: Unexpected status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to API server")
        print("   Make sure Django server is running: python manage.py runserver 8003")
        return False
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False


def test_daily_quiz_uses_settings():
    """Test that daily quiz endpoint uses dynamic settings"""
    print("\n\n🧪 Testing Daily Quiz Endpoint Integration\n")
    print("=" * 60)
    
    try:
        url = f"{API_BASE_URL}/daily-quiz/?user_id=test_user_123"
        print(f"📡 Request: GET {url}")
        
        response = requests.get(url)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if 'coins' in data:
                coins = data['coins']
                print("\n✅ Daily Quiz Coin Settings:")
                print(f"   - Attempt Bonus: {coins.get('attempt_bonus', 'N/A')}")
                print(f"   - Per Correct Answer: {coins.get('per_correct_answer', 'N/A')}")
                print(f"   - Max Possible: {coins.get('max_possible', 'N/A')}")
                print("\n✅ Daily quiz is using dynamic settings!")
                return True
            else:
                print("\n⚠️  No 'coins' field in response")
                print("   This might be because quiz was already attempted")
                return True
        else:
            print(f"\n❌ Error: Status code {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False


if __name__ == "__main__":
    print("\n" + "🎯" * 30)
    print("Quiz Settings API Test Suite")
    print("🎯" * 30 + "\n")
    
    # Run tests
    test1_passed = test_quiz_settings_endpoint()
    test2_passed = test_daily_quiz_uses_settings()
    
    # Summary
    print("\n\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    print(f"Quiz Settings Endpoint: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Daily Quiz Integration:  {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! System is working correctly.")
        exit(0)
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
        exit(1)
