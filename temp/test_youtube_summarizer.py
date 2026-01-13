import requests
import json

BASE_URL = 'http://localhost:8000'

def test_summarize_youtube_video():
    """Test YouTube video summarization with real video"""
    print("\n" + "="*70)
    print("TEST 1: YouTube Video Summarization")
    print("="*70)

    payload = {
        'video_url': 'https://www.youtube.com/watch?v=x6HTSdLsgVo'
    }

    print(f"Testing with URL: {payload['video_url']}")
    print("Processing (extracting transcript and generating summary)...")

    response = requests.post(
        f'{BASE_URL}/api/youtube/summarize/',
        json=payload,
        headers={'Content-Type': 'application/json'}
    )

    print(f"\nStatus Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success')}")
        print(f"Video Title: {data.get('video_title')}")
        print(f"Channel: {data.get('channel')}")
        print(f"Transcript Language: {data.get('transcript', {}).get('language')}")
        print(f"Transcript Segments: {data.get('transcript', {}).get('segments_count')}")
        print(f"Summary Type: {data.get('summary_type')}")
        print("\nSUMMARY:")
        print("-" * 70)
        print(data.get('summary', 'No summary available'))
        print("-" * 70)
        return True
    else:
        print(f"Error: {response.json()}")
        return False

def test_invalid_url():
    """Test with invalid URL"""
    print("\n" + "="*70)
    print("TEST 2: Invalid YouTube URL")
    print("="*70)

    payload = {
        'video_url': 'https://invalid-url.com/watch?v=invalid'
    }

    print(f"Testing with invalid URL: {payload['video_url']}")

    response = requests.post(
        f'{BASE_URL}/api/youtube/summarize/',
        json=payload,
        headers={'Content-Type': 'application/json'}
    )

    print(f"Status Code: {response.status_code}")
    if response.status_code == 400:
        print(f"Expected error: {response.json().get('error')}")
        return True
    else:
        print(f"Unexpected response: {response.json()}")
        return False

def test_missing_url():
    """Test with missing URL"""
    print("\n" + "="*70)
    print("TEST 3: Missing video_url Parameter")
    print("="*70)

    payload = {}

    print("Testing with empty payload...")

    response = requests.post(
        f'{BASE_URL}/api/youtube/summarize/',
        json=payload,
        headers={'Content-Type': 'application/json'}
    )

    print(f"Status Code: {response.status_code}")
    if response.status_code == 400:
        print(f"Expected error: {response.json().get('error')}")
        return True
    else:
        print(f"Unexpected response: {response.json()}")
        return False

def test_youtube_short_url():
    """Test with YouTube short URL format"""
    print("\n" + "="*70)
    print("TEST 4: YouTube Short URL Format")
    print("="*70)

    payload = {
        'video_url': 'https://youtu.be/x6HTSdLsgVo'
    }

    print(f"Testing with short URL: {payload['video_url']}")
    print("Processing...")

    response = requests.post(
        f'{BASE_URL}/api/youtube/summarize/',
        json=payload,
        headers={'Content-Type': 'application/json'}
    )

    print(f"\nStatus Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success')}")
        print(f"Video Title: {data.get('video_title')}")
        print(f"Transcript Language: {data.get('transcript', {}).get('language')}")
        print(f"Summary Type: {data.get('summary_type')}")
        return True
    else:
        print(f"Error: {response.json()}")
        return False

def main():
    print("\n" + "="*70)
    print("YouTube Video Summarizer Test Suite")
    print("="*70)

    results = {
        'Summarization': test_summarize_youtube_video(),
        'Invalid URL': test_invalid_url(),
        'Missing URL': test_missing_url(),
        'Short URL': test_youtube_short_url(),
    }

    print("\n" + "="*70)
    print("TEST RESULTS SUMMARY")
    print("="*70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("\nAll tests passed! YouTube summarization feature is working properly.")
    else:
        print(f"\n{total - passed} test(s) failed. Check the output above for details.")

    print("\n" + "="*70)
    print("API Documentation")
    print("="*70)
    print("""
Summarize YouTube Video:
  POST /api/youtube/summarize/
  {
    "video_url": "https://www.youtube.com/watch?v=VIDEO_ID"
  }

Response:
  {
    "success": true,
    "video_url": "...",
    "video_id": "...",
    "video_title": "...",
    "channel": "...",
    "transcript": {
      "language": "en",
      "segments_count": 356,
      "duration_text": "356 text segments"
    },
    "summary": "...",
    "summary_type": "gemini_ai or simple_extraction"
  }

Supported URL Formats:
  - https://www.youtube.com/watch?v=VIDEO_ID
  - https://youtu.be/VIDEO_ID
  - https://www.youtube.com/embed/VIDEO_ID
""")

if __name__ == '__main__':
    main()