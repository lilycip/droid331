#!/usr/bin/env python3
"""
Test the web API for the Droid agent.
"""
import requests
import json
import argparse
import time

def main():
    """Test the web API."""
    parser = argparse.ArgumentParser(description="Test the Droid agent web API")
    parser.add_argument("--host", type=str, default="http://localhost:12000", help="Host of the web API")
    
    args = parser.parse_args()
    
    base_url = args.host
    
    # Test text generation
    print("Testing text generation...")
    text_data = {
        "content_type": "text",
        "prompt": "Write a short, engaging tweet about artificial intelligence.",
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(f"{base_url}/api/generate", json=text_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    except Exception as e:
        print(f"Error: {str(e)}\n")
    
    # Test image generation
    print("Testing image generation...")
    image_data = {
        "content_type": "image",
        "prompt": "A futuristic robot assistant helping humans, digital art style.",
        "width": 512,
        "height": 512
    }
    
    try:
        response = requests.post(f"{base_url}/api/generate", json=image_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    except Exception as e:
        print(f"Error: {str(e)}\n")
    
    # Test meme generation
    print("Testing meme generation...")
    meme_data = {
        "content_type": "meme",
        "prompt": "When AI tries to understand human humor",
        "style": "funny",
        "template": "default"
    }
    
    try:
        response = requests.post(f"{base_url}/api/generate", json=meme_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    except Exception as e:
        print(f"Error: {str(e)}\n")
    
    # Test social media posting
    print("Testing social media posting...")
    post_data = {
        "platform": "twitter",
        "content": "Testing the Droid AI Agent! #AI #Testing"
    }
    
    try:
        response = requests.post(f"{base_url}/api/post", json=post_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    except Exception as e:
        print(f"Error: {str(e)}\n")

if __name__ == "__main__":
    main()