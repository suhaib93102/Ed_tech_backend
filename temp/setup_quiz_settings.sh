#!/bin/bash

# Initialize Quiz Settings in Django Admin
# This script creates the initial QuizSettings instance with default values

echo "🎯 Initializing Quiz Settings..."

cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "env" ]; then
    source env/bin/activate
fi

# Run Django shell command to create QuizSettings instance
python manage.py shell << EOF
from question_solver.models import QuizSettings

# Get or create the singleton settings instance
settings = QuizSettings.get_settings()

print("\n✅ Quiz Settings initialized successfully!")
print(f"   - Daily Quiz Attempt Bonus: {settings.daily_quiz_attempt_bonus} coins")
print(f"   - Coins per Correct Answer: {settings.daily_quiz_coins_per_correct} coins")
print(f"   - Perfect Score Bonus: {settings.daily_quiz_perfect_score_bonus} coins")
print(f"   - Pair Quiz Enabled: {settings.pair_quiz_enabled}")
print(f"   - Session Timeout: {settings.pair_quiz_session_timeout} minutes")
print(f"   - Max Questions: {settings.pair_quiz_max_questions}")
print(f"   - Coin to Currency Rate: {settings.coin_to_currency_rate}")
print(f"   - Min Coins for Redemption: {settings.min_coins_for_redemption}")
print(f"\n📝 You can edit these settings at: http://127.0.0.1:8003/admin/question_solver/quizsettings/")
EOF

echo ""
echo "✨ Done! Quiz settings are ready to use."
echo ""
echo "To edit settings:"
echo "1. Go to: http://127.0.0.1:8003/admin/"
echo "2. Login with your admin credentials"
echo "3. Navigate to: Question Solver → Quiz Settings"
echo "4. Update values and save"
echo "5. Changes take effect immediately!"
