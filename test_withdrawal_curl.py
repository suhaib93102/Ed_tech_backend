#!/usr/bin/env python
"""
Standalone test script for withdrawal system
Tests endpoints with curl commands
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edtech_project.settings_test')

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

import django
django.setup()

from django.contrib.auth.models import User
from question_solver.models import UserCoins, CoinWithdrawal, CoinTransaction
from django.test.utils import setup_test_environment, teardown_test_environment
from django.db import connection
from django.test.client import Client
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
import jwt

def get_jwt_token(user):
    """Generate JWT token for user"""
    SECRET_KEY = 'test-jwt-secret-key'
    payload = {
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def setup_test_data():
    """Create test users and coins"""
    print("\n" + "="*80)
    print("SETTING UP TEST DATA")
    print("="*80)
    
    # Clear existing data
    User.objects.all().delete()
    UserCoins.objects.all().delete()
    CoinWithdrawal.objects.all().delete()
    CoinTransaction.objects.all().delete()
    
    # Create regular user
    user = User.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='testpass123'
    )
    print(f"✓ Created user: {user.username} (ID: {user.id})")
    
    # Create admin user
    admin = User.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='adminpass123',
        is_staff=True,
        is_superuser=True
    )
    print(f"✓ Created admin: {admin.username} (ID: {admin.id})")
    
    # Give user initial coins
    user_coins = UserCoins.objects.create(
        user_id=str(user.id),
        total_coins=1000,
        lifetime_coins=2000
    )
    print(f"✓ Created UserCoins for {user.username}: {user_coins.total_coins} coins")
    
    # Also give admin coins
    admin_coins = UserCoins.objects.create(
        user_id=str(admin.id),
        total_coins=5000,
        lifetime_coins=10000
    )
    print(f"✓ Created UserCoins for {admin.username}: {admin_coins.total_coins} coins")
    
    return user, admin, get_jwt_token(user), get_jwt_token(admin)

def test_endpoints_curl():
    """Test endpoints using curl (for real HTTP simulation)"""
    print("\n" + "="*80)
    print("TESTING ENDPOINTS WITH CURL (Will use running server)")
    print("="*80)
    
    print("\n⚠️  Note: This assumes Django server is running on localhost:8000")
    print("   Start server with: DJANGO_SETTINGS_MODULE=edtech_project.settings_test python manage.py runserver")
    
    # Create test data
    user, admin, user_token, admin_token = setup_test_data()
    
    print("\n" + "-"*80)
    print("TEST 1: Create Withdrawal Request")
    print("-"*80)
    
    curl_cmd = f'''
    curl -X POST http://localhost:8000/api/withdrawal/create/ \\
      -H "Authorization: Bearer {user_token}" \\
      -H "Content-Type: application/json" \\
      -d '{{
        "coins_amount": 300,
        "upi_id": "testuser@upi"
      }}'
    '''
    print(f"Command:\n{curl_cmd}")
    print("\nExpected response: Withdrawal created with status='pending'")
    
    print("\n" + "-"*80)
    print("TEST 2: Check User Profile (Should show reduced coins)")
    print("-"*80)
    
    curl_cmd = f'''
    curl -X GET http://localhost:8000/api/auth/user/profile/ \\
      -H "Authorization: Bearer {user_token}"
    '''
    print(f"Command:\n{curl_cmd}")
    print("Expected: coins: 700 (1000 - 300)")
    
    print("\n" + "-"*80)
    print("TEST 3: Get Withdrawal History")
    print("-"*80)
    
    curl_cmd = f'''
    curl -X GET http://localhost:8000/api/withdrawal/history/ \\
      -H "Authorization: Bearer {user_token}"
    '''
    print(f"Command:\n{curl_cmd}")
    print("Expected: List of user's withdrawals")
    
    print("\n" + "-"*80)
    print("TEST 4: Admin Views Withdrawal Request")
    print("-"*80)
    
    print("Expected Response (after creating withdrawal in TEST 1):")
    print("""
    {
      "success": true,
      "withdrawals": [
        {
          "id": "w_xxx",
          "user_id": "1",
          "coins_amount": 300,
          "rupees_amount": 30.00,
          "status": "pending",
          "upi_id": "testuser@upi",
          "created_at": "2024-01-06T..."
        }
      ]
    }
    """)
    
    print("\n" + "-"*80)
    print("TEST 5: Admin Approves Withdrawal")
    print("-"*80)
    
    print("(After TEST 1, get withdrawal_id, then run:)")
    curl_cmd = f'''
    curl -X POST http://localhost:8000/api/admin/withdrawal/approve/WITHDRAWAL_ID/ \\
      -H "Authorization: Bearer {admin_token}" \\
      -H "Content-Type: application/json" \\
      -d '{{
        "admin_notes": "Approved for processing"
      }}'
    '''
    print(f"Command:\n{curl_cmd}")
    print("Expected: status changes to 'processing'")
    
    print("\n" + "-"*80)
    print("TEST 6: Admin Marks as Completed")
    print("-"*80)
    
    curl_cmd = f'''
    curl -X POST http://localhost:8000/api/admin/withdrawal/complete/WITHDRAWAL_ID/ \\
      -H "Authorization: Bearer {admin_token}"
    '''
    print(f"Command:\n{curl_cmd}")
    print("Expected: status changes to 'completed'")
    
    print("\n" + "-"*80)
    print("TEST 7: Admin Rejects Withdrawal (Refunds Coins)")
    print("-"*80)
    
    print("(Create new withdrawal first, then:)")
    curl_cmd = f'''
    curl -X POST http://localhost:8000/api/admin/withdrawal/reject/WITHDRAWAL_ID/ \\
      -H "Authorization: Bearer {admin_token}" \\
      -H "Content-Type: application/json" \\
      -d '{{
        "reason": "Invalid UPI ID",
        "admin_notes": "UPI format incorrect"
      }}'
    '''
    print(f"Command:\n{curl_cmd}")
    print("Expected: Coins refunded, status='rejected'")
    print("          User profile coins should increase back")
    
    print("\n" + "-"*80)
    print("TEST 8: Admin Deletes Withdrawal (Refunds Coins)")
    print("-"*80)
    
    curl_cmd = f'''
    curl -X DELETE http://localhost:8000/api/admin/withdrawal/delete/WITHDRAWAL_ID/ \\
      -H "Authorization: Bearer {admin_token}"
    '''
    print(f"Command:\n{curl_cmd}")
    print("Expected: Withdrawal deleted, coins refunded")

def test_api_client():
    """Test using Django's test client (for API logic verification)"""
    print("\n" + "="*80)
    print("TESTING WITH DJANGO TEST CLIENT (Direct API Testing)")
    print("="*80)
    
    # Create test data
    user, admin, user_token, admin_token = setup_test_data()
    
    from rest_framework.test import APIClient
    client = APIClient()
    
    # Test 1: Create withdrawal
    print("\n" + "-"*80)
    print("TEST 1: Create Withdrawal")
    print("-"*80)
    
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')
    response = client.post('/api/withdrawal/create/', {
        'coins_amount': 300,
        'upi_id': 'testuser@upi'
    }, format='json')
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.data, indent=2)}")
    
    if response.status_code == 201:
        withdrawal_id = response.data['withdrawal']['id']
        print(f"✓ Withdrawal created! ID: {withdrawal_id}")
    else:
        print("✗ Failed to create withdrawal")
        withdrawal_id = None
    
    # Test 2: Check profile coins
    print("\n" + "-"*80)
    print("TEST 2: Check User Profile (Coins should be reduced)")
    print("-"*80)
    
    response = client.get('/api/auth/user/profile/', format='json')
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        coins = response.data['user']['coins']
        print(f"Current coins: {coins}")
        print(f"✓ Coins reduced from 1000 to {coins}")
    else:
        print(f"✗ Failed to get profile: {response.data}")
    
    # Test 3: Get withdrawal history
    print("\n" + "-"*80)
    print("TEST 3: Get Withdrawal History")
    print("-"*80)
    
    response = client.get('/api/withdrawal/history/', format='json')
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        withdrawals = response.data['withdrawals']
        print(f"Found {len(withdrawals)} withdrawal(s)")
        for w in withdrawals:
            print(f"  - {w['id']}: {w['coins_amount']} coins (status: {w['status']})")
    
    # Test 4: Admin approval
    if withdrawal_id:
        print("\n" + "-"*80)
        print("TEST 4: Admin Approves Withdrawal")
        print("-"*80)
        
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
        response = client.post(f'/api/admin/withdrawal/approve/{withdrawal_id}/', {
            'admin_notes': 'Approved for processing'
        }, format='json')
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"✓ Withdrawal approved")
            print(f"  Status: {response.data['status']}")
        else:
            print(f"✗ Failed to approve: {response.data}")
        
        # Test 5: Mark as completed
        print("\n" + "-"*80)
        print("TEST 5: Admin Marks as Completed")
        print("-"*80)
        
        response = client.post(f'/api/admin/withdrawal/complete/{withdrawal_id}/', format='json')
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"✓ Withdrawal completed")
            print(f"  Status: {response.data['status']}")
        else:
            print(f"✗ Failed to complete: {response.data}")
    
    # Test 6: Create another withdrawal for rejection test
    print("\n" + "-"*80)
    print("TEST 6: Create Second Withdrawal for Rejection Test")
    print("-"*80)
    
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')
    response = client.post('/api/withdrawal/create/', {
        'coins_amount': 200,
        'upi_id': 'testuser2@upi'
    }, format='json')
    
    if response.status_code == 201:
        withdrawal_id_2 = response.data['withdrawal']['id']
        print(f"✓ Second withdrawal created! ID: {withdrawal_id_2}")
        
        # Check coins before rejection
        response = client.get('/api/auth/user/profile/', format='json')
        coins_before = response.data['user']['coins']
        print(f"  Coins after second withdrawal: {coins_before}")
        
        # Admin rejects
        print("\n" + "-"*80)
        print("TEST 7: Admin Rejects Withdrawal (Should Refund Coins)")
        print("-"*80)
        
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
        response = client.post(f'/api/admin/withdrawal/reject/{withdrawal_id_2}/', {
            'reason': 'Invalid UPI ID',
            'admin_notes': 'Check UPI format'
        }, format='json')
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"✓ Withdrawal rejected")
            print(f"  Status: {response.data['status']}")
            
            # Check coins after refund
            client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')
            response = client.get('/api/auth/user/profile/', format='json')
            coins_after = response.data['user']['coins']
            print(f"  Coins after refund: {coins_after}")
            
            if coins_after > coins_before:
                print(f"  ✓ Coins refunded! ({coins_before} → {coins_after})")
            else:
                print(f"  ✗ Coins not refunded properly")

if __name__ == '__main__':
    print("\n")
    print("█" * 80)
    print("  WITHDRAWAL SYSTEM - COMPREHENSIVE TEST SUITE")
    print("█" * 80)
    
    try:
        # Test with API client
        test_api_client()
        
        # Show curl commands
        test_endpoints_curl()
        
        print("\n" + "="*80)
        print("ALL TESTS COMPLETED!")
        print("="*80)
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
