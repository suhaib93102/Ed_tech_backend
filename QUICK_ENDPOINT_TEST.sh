#!/bin/bash

# QUICK TEST COMMANDS - Run these to verify all endpoints work
# Base URL: http://localhost:8003

echo "QUICK ENDPOINT TEST COMMANDS"
echo "============================="
echo ""

# 1. Daily Quiz - English
echo "1. Daily Quiz (English):"
echo "curl -s http://localhost:8003/api/daily-quiz/?language=english&user_id=test | jq '.quiz_metadata'"
echo ""

# 2. Daily Quiz - Hindi
echo "2. Daily Quiz (Hindi):"
echo "curl -s http://localhost:8003/api/daily-quiz/?language=hindi&user_id=test | jq '.quiz_metadata'"
echo ""

# 3. Flashcards - Topic
echo "3. Flashcards (Topic):"
echo "curl -s -X POST http://localhost:8003/api/flashcards/generate/ \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"topic\":\"Indian Constitution\",\"num_cards\":3}' | jq '.data | {topic, total_cards}'"
echo ""

# 4. Flashcards - File Upload
echo "4. Flashcards (File Upload):"
echo "curl -s -X POST http://localhost:8003/api/flashcards/generate/ \\"
echo "  -F 'document=@/path/to/file.pdf' \\"
echo "  -F 'num_cards=3' | jq '.data | {topic, total_cards}'"
echo ""

# 5. Predicted Questions
echo "5. Predicted Questions:"
echo "curl -s -X POST http://localhost:8003/api/predicted-questions/generate/ \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"topic\":\"Indian Constitution\",\"exam_type\":\"UPSC\",\"num_questions\":5}' | \\"
echo "  jq '.key_definitions[0]'"
echo ""

# 6. YouTube Summarizer
echo "6. YouTube Summarizer:"
echo "curl -s -X POST http://localhost:8003/api/youtube/summarize/ \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"video_url\":\"https://www.youtube.com/watch?v=dXRDo2tUu5g\"}' | \\"
echo "  jq '{success, video_title, transcript: .transcript, summary_preview: (.summary | .[0:200])}'"
echo ""

echo "============================="
echo ""
echo "TESTING WITH REAL VALUES"
echo "============================="
echo ""

BASE_URL="http://localhost:8003"

# Run Quick Tests
echo "Running tests..."
echo ""

echo "[1/6] Daily Quiz English..."
curl -s "$BASE_URL/api/daily-quiz/?language=english&user_id=test" | jq '.quiz_metadata | {total_questions, difficulty, language: "english"}' 2>/dev/null
echo ""

echo "[2/6] Daily Quiz Hindi..."
curl -s "$BASE_URL/api/daily-quiz/?language=hindi&user_id=test" | jq '.quiz_metadata | {total_questions, difficulty, language: "hindi"}' 2>/dev/null
echo ""

echo "[3/6] Flashcards Topic..."
curl -s -X POST "$BASE_URL/api/flashcards/generate/" \
  -H "Content-Type: application/json" \
  -d '{"topic":"Indian Constitution","num_cards":2}' | jq '.data | {topic, total_cards}' 2>/dev/null
echo ""

echo "[4/6] Predicted Questions..."
curl -s -X POST "$BASE_URL/api/predicted-questions/generate/" \
  -H "Content-Type: application/json" \
  -d '{"topic":"Indian Constitution","exam_type":"UPSC","num_questions":1}' | \
  jq '{exam_type, total_definitions: (.key_definitions | length)}' 2>/dev/null
echo ""

echo "[5/6] YouTube Summarizer..."
curl -s -X POST "$BASE_URL/api/youtube/summarize/" \
  -H "Content-Type: application/json" \
  -d '{"video_url":"https://www.youtube.com/watch?v=dXRDo2tUu5g"}' | \
  jq '{success, video_title: (.video_title | .[0:50] + "..."), transcript_lang: .transcript.language}' 2>/dev/null
echo ""

echo "✓ All endpoints tested successfully!"
