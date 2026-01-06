#!/usr/bin/env python3
"""
Complete test for coin flow - Daily Quiz submission and coin update
"""
import os
import sys
import django
import json

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edtech_project.settings')
django.setup()

from question_solver.models import UserCoins, DailyQuiz, DailyQuestion, UserDailyQuizAttempt, QuizSettings
from question_solver.daily_quiz_views import submit_daily_quiz
from django.test import RequestFactory
from rest_framework.request import Request
from datetime import date

def test_coin_flow():
    print("=" * 60)
    print("TESTING COMPLETE COIN FLOW")
    print("=" * 60)
    
    # Test user
    test_user = 'frontend_test_user'
    
    # Clean up previous test data
    UserDailyQuizAttempt.objects.filter(user_id=test_user).delete()
    UserCoins.objects.filter(user_id=test_user).delete()
    
    # Create user with initial coins
    user_coins = UserCoins.objects.create(
        user_id=test_user,
        total_coins=0,
        lifetime_coins=0
    )
    print(f"\n1. Created test user: {test_user}")
    print(f"   Initial coins: {user_coins.total_coins}")
    
    # Get quiz settings
    settings = QuizSettings.get_settings()
    print(f"\n2. Quiz Settings:")
    print(f"   Attempt bonus: {settings.daily_quiz_attempt_bonus} coins")
    print(f"   Per correct answer: {settings.daily_quiz_coins_per_correct} coins")
    
    # Create a test quiz for today
    today = date.today()
    quiz = DailyQuiz.objects.filter(date=today, is_active=True).first()
    
    if not quiz:
        print(f"\n3. Creating test quiz for {today}...")
        quiz = DailyQuiz.objects.create(
            date=today,
            title=f'Test Daily Quiz - {today}',
            description='Test quiz',
            total_questions=5,
            difficulty='medium'
        )
        
        # Add 5 test questions
        for i in range(1, 6):
            DailyQuestion.objects.create(
                daily_quiz=quiz,
                order=i,
                question_text=f'Test question {i}?',
                options=['Option A', 'Option B', 'Option C', 'Option D'],
                correct_answer='A',
                explanation=f'Explanation for question {i}',
                category='general',
                difficulty='medium'
            )
        print(f"   Created quiz with 5 questions")
    else:
        print(f"\n3. Using existing quiz: {quiz.title}")
    
    # Simulate quiz submission - answer 3 questions correctly
    print(f"\n4. Submitting quiz with 3 correct answers...")
    factory = RequestFactory()
    request_data = {
        'user_id': test_user,
        'quiz_id': str(quiz.id),
        'answers': {
            '1': 0,  # Correct (A)
            '2': 0,  # Correct (A)
            '3': 0,  # Correct (A)
            '4': 1,  # Wrong
            '5': 1,  # Wrong
        },
        'time_taken_seconds': 60
    }
    
    django_request = factory.post(
        '/api/daily-quiz/submit/',
        data=json.dumps(request_data),
        content_type='application/json'
    )
    
    # Call the view with django request
    response = submit_daily_quiz(django_request)
    
    print(f"\n5. Response Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.data
        print(f"\n6. Quiz Results:")
        print(f"   Success: {data.get('success')}")
        print(f"   Message: {data.get('message')}")
        
        result = data.get('result', {})
        print(f"\n   Correct: {result.get('correct_count')}/{result.get('total_questions')}")
        print(f"   Score: {result.get('score_percentage')}%")
        print(f"   Coins earned this quiz: {result.get('coins_earned')}")
        
        coin_breakdown = data.get('coin_breakdown', {})
        print(f"\n   Coin Breakdown:")
        print(f"   - Attempt bonus: {coin_breakdown.get('attempt_bonus')}")
        print(f"   - Correct answers: {coin_breakdown.get('correct_answers')} x {coin_breakdown.get('coins_per_correct')} = {coin_breakdown.get('correct_answer_coins')}")
        print(f"   - Total earned: {coin_breakdown.get('total_earned')}")
        
        # THIS IS THE KEY - total_coins from server
        server_total_coins = data.get('total_coins')
        print(f"\n7. TOTAL COINS FROM SERVER: {server_total_coins}")
        
        # Verify in database
        user_coins.refresh_from_db()
        print(f"   Database total coins: {user_coins.total_coins}")
        
        if server_total_coins == user_coins.total_coins:
            print(f"\n✅ SUCCESS! Server response matches database")
            print(f"✅ Frontend should display: {server_total_coins} coins")
        else:
            print(f"\n❌ ERROR! Mismatch:")
            print(f"   Server says: {server_total_coins}")
            print(f"   Database says: {user_coins.total_coins}")
        
        # Expected calculation
        expected_coins = settings.daily_quiz_attempt_bonus + (3 * settings.daily_quiz_coins_per_correct)
        print(f"\n8. Validation:")
        print(f"   Expected coins earned: {expected_coins}")
        print(f"   Actual coins earned: {result.get('coins_earned')}")
        print(f"   Match: {'✅' if expected_coins == result.get('coins_earned') else '❌'}")
        
    else:
        print(f"\n❌ ERROR Response:")
        print(response.data)
    
    print("\n" + "=" * 60)
    print("FRONTEND INTEGRATION INSTRUCTIONS:")
    print("=" * 60)
    print("The backend returns 'total_coins' in the response.")
    print("Frontend should use this value directly:")
    print("")
    print("  const serverTotalCoins = results.total_coins;")
    print("  onComplete(serverTotalCoins);")
    print("")
    print("DO NOT calculate locally by adding coins_earned to previous value!")
    print("=" * 60)

if __name__ == '__main__':
    test_coin_flow()
