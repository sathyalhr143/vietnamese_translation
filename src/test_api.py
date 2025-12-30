"""
Test script for the FastAPI translation service.
Run this to verify all endpoints are working correctly.
"""

import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint."""
    print("✓ Testing health check...")
    response = requests.get(f"{BASE_URL}/api/health")
    assert response.status_code == 200
    data = response.json()
    print(f"  Status: {data['status']}")
    print(f"  Service: {data['service']}\n")

def test_text_translation():
    """Test text translation endpoint."""
    print("✓ Testing text translation...")
    payload = {
        "text": "Xin chào, bạn khỏe không?",
        "source_language": "vi",
        "target_language": "en"
    }
    response = requests.post(f"{BASE_URL}/api/translate/text", json=payload)
    assert response.status_code == 200
    data = response.json()
    print(f"  Source: {data['source_text']}")
    print(f"  Translation: {data['translated_text']}")
    print(f"  Translation ID: {data['translation_id']}\n")
    return data['translation_id']

def test_get_translation(translation_id):
    """Test getting a specific translation."""
    print(f"✓ Testing get translation {translation_id}...")
    response = requests.get(f"{BASE_URL}/api/translation/{translation_id}")
    assert response.status_code == 200
    data = response.json()
    print(f"  Status: {data['status']}")
    print(f"  Timestamp: {data['timestamp']}\n")

def test_history():
    """Test translation history endpoint."""
    print("✓ Testing translation history...")
    response = requests.get(f"{BASE_URL}/api/history?limit=5")
    assert response.status_code == 200
    data = response.json()
    print(f"  Total translations: {data['total_translations']}")
    print(f"  Returned: {data['returned']}")
    if data['translations']:
        print(f"  Latest: {data['translations'][-1]['source_text']}\n")

def test_audio_translation(audio_file="test_audio.wav"):
    """Test audio file translation."""
    print(f"✓ Testing audio translation with {audio_file}...")
    
    # Check if test audio file exists
    if not Path(audio_file).exists():
        print(f"  ⚠ Test audio file '{audio_file}' not found, skipping...\n")
        return None
    
    with open(audio_file, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/api/translate/audio", files=files)
    
    assert response.status_code == 200
    data = response.json()
    print(f"  Transcription: {data['source_text']}")
    print(f"  Translation: {data['translated_text']}")
    print(f"  Duration: {data['duration_seconds']:.2f}s")
    print(f"  Confidence: {data['confidence']:.2%}\n")

def main():
    """Run all tests."""
    print("=" * 60)
    print("Vietnamese Translation API - Test Suite")
    print("=" * 60)
    print(f"Testing against: {BASE_URL}\n")
    
    try:
        # Test basic endpoints
        test_health()
        translation_id = test_text_translation()
        test_get_translation(translation_id)
        test_history()
        
        # Test audio endpoint if file exists
        test_audio_translation()
        
        print("=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Visit http://localhost:8000 to use the web UI")
        print("2. Check API_GUIDE.md for endpoint documentation")
        print("3. Deploy to Render when ready\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to server")
        print(f"   Make sure the app is running at {BASE_URL}")
        print("   Run: python -m uvicorn app:app --reload\n")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}\n")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")

if __name__ == "__main__":
    main()
