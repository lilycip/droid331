#!/usr/bin/env python3
"""
Example script to generate content using the Droid agent.
"""
import os
import sys
import json

# Add the parent directory to the path so we can import the droid package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from droid.core.agent import Agent
from droid.utils.logger import setup_logging

def main():
    """Generate content example."""
    # Set up logging
    setup_logging({"level": "INFO"})
    
    # Create the agent
    agent = Agent("config/config.yaml")
    
    # Generate text content
    text_params = {
        "content_type": "text",
        "prompt": "Write a short, engaging tweet about artificial intelligence."
    }
    
    print("Generating text content...")
    text_result = agent.execute_task("generate_content", text_params)
    print(f"Generated text: {text_result.get('text', 'Error')}\n")
    
    # Generate an image
    image_params = {
        "content_type": "image",
        "prompt": "A futuristic robot assistant helping humans, digital art style."
    }
    
    print("Generating image...")
    image_result = agent.execute_task("generate_content", image_params)
    print(f"Image result: {json.dumps(image_result, indent=2)}\n")
    
    # Generate a meme
    meme_params = {
        "content_type": "meme",
        "topic": "artificial intelligence",
        "style": "funny"
    }
    
    print("Generating meme...")
    meme_result = agent.execute_task("generate_content", meme_params)
    print(f"Meme result: {json.dumps(meme_result, indent=2)}")

if __name__ == "__main__":
    main()