#!/bin/bash

# Test Gemini API Key Status
echo "🔑 Testing Gemini API Key Status"
echo "================================="

# Check if GEMINI_API_KEY is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ GEMINI_API_KEY environment variable not set"
    echo ""
    echo "📝 To fix:"
    echo "1. Get API key from: https://makersuite.google.com/app/apikey"
    echo "2. Set environment variable: export GEMINI_API_KEY=your_key_here"
    echo "3. For production: Update in Render dashboard"
    exit 1
else
    echo "✅ GEMINI_API_KEY environment variable is set"
fi

# Test API key with a simple request
echo ""
echo "🧪 Testing API Key with Gemini..."
cd /Users/vishaljha/Ed_tech_backend

python manage.py shell -c "
import os
from question_solver.services.gemini_service import gemini_service

print('API Key Status Test')
print('==================')
print(f'API Key Set: {bool(os.getenv(\"GEMINI_API_KEY\"))}')
print(f'Model Initialized: {gemini_service.model is not None}')

if gemini_service.model:
    try:
        # Test with a simple prompt
        response = gemini_service.model.generate_content('Say hello in 5 words')
        print(f'API Test: ✅ SUCCESS - {response.text.strip()}')
        print('🎉 Gemini API is working!')
    except Exception as e:
        error_str = str(e)
        if 'API_KEY_INVALID' in error_str or 'API key expired' in error_str:
            print('❌ API Test: FAILED - API key expired or invalid')
            print('🔧 Solution: Get new API key from https://makersuite.google.com/app/apikey')
        else:
            print(f'❌ API Test: FAILED - {error_str}')
else:
    print('❌ Model not initialized')
" 2>/dev/null

echo ""
echo "📋 Next Steps:"
echo "=============="
echo "1. If API key expired: Get new key from Google AI Studio"
echo "2. Update GEMINI_API_KEY in Render environment variables"
echo "3. Redeploy service (happens automatically)"
echo "4. Test daily quiz endpoint works"
echo ""
echo "🔗 Useful Links:"
echo "- Google AI Studio: https://makersuite.google.com/app/apikey"
echo "- Render Dashboard: https://dashboard.render.com/"
echo "- Test Endpoint: https://ed-tech-backend-tzn8.onrender.com/api/daily-quiz/?language=english&user_id=test"