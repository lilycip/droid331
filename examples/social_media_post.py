#!/usr/bin/env python3
"""
Example script to post to social media using the Droid agent.
"""
import os
import sys
import json

# Add the parent directory to the path so we can import the droid package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from droid.core.agent import Agent
from droid.utils.logger import setup_logging

def main():
    """Social media posting example."""
    # Set up logging
    setup_logging({"level": "INFO"})
    
    # Create the agent
    agent = Agent("config/config.yaml")
    
    # First, generate content
    content_params = {
        "content_type": "text",
        "prompt": "Write a short, engaging tweet about the future of AI."
    }
    
    print("Generating content...")
    content_result = agent.execute_task("generate_content", content_params)
    
    if not content_result.get("success", False):
        print(f"Error generating content: {content_result.get('error', 'Unknown error')}")
        return
    
    content = content_result.get("text", "Check out this amazing AI agent!")
    
    # Post to Twitter
    twitter_params = {
        "platform": "twitter",
        "content_type": "text",
        "content": content
    }
    
    print(f"Posting to Twitter: {content}")
    twitter_result = agent.execute_task("post_content", twitter_params)
    print(f"Twitter result: {json.dumps(twitter_result, indent=2)}\n")
    
    # Post to Instagram with an image
    # First, generate an image
    image_params = {
        "content_type": "image",
        "prompt": "A futuristic AI assistant, digital art style."
    }
    
    print("Generating image for Instagram...")
    image_result = agent.execute_task("generate_content", image_params)
    
    if not image_result.get("success", False):
        print(f"Error generating image: {image_result.get('error', 'Unknown error')}")
        return
    
    # Post to Instagram
    instagram_params = {
        "platform": "instagram",
        "content_type": "image",
        "content": "AI is transforming our world! #AI #Technology #Future",
        "media_urls": [image_result.get("filepath")]
    }
    
    print("Posting to Instagram...")
    instagram_result = agent.execute_task("post_content", instagram_params)
    print(f"Instagram result: {json.dumps(instagram_result, indent=2)}")

if __name__ == "__main__":
    main()