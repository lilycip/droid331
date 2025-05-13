#!/usr/bin/env python3
"""
Example of testing the custom API with the Droid agent.
"""
import os
import sys
import json
import time
import argparse
import requests
import logging
from droid.utils.logger import setup_logging

def test_api(base_url, api_key):
    """Test the custom API."""
    logger = logging.getLogger(__name__)
    
    # Set up the headers
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key
    }
    
    # Test the health endpoint
    logger.info("Testing health endpoint...")
    response = requests.get(f"{base_url}/health")
    logger.info(f"Response: {response.status_code} {response.json()}")
    
    # Test the info endpoint
    logger.info("\nTesting info endpoint...")
    response = requests.get(f"{base_url}/info", headers=headers)
    logger.info(f"Response: {response.status_code} {response.json()}")
    
    # Test the generate endpoint
    logger.info("\nTesting generate endpoint...")
    data = {
        "type": "text",
        "prompt": "Write a short poem about AI agents"
    }
    response = requests.post(f"{base_url}/generate", headers=headers, json=data)
    logger.info(f"Response: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        logger.info(f"Generated content: {result.get('result')}")
    
    # Test the task endpoint
    logger.info("\nTesting task endpoint...")
    data = {
        "task": "generate_content",
        "params": {
            "content_type": "text",
            "prompt": "Explain how AI agents can help with social media"
        }
    }
    response = requests.post(f"{base_url}/task", headers=headers, json=data)
    logger.info(f"Response: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        task_id = result.get("task_id")
        logger.info(f"Task ID: {task_id}")
        
        # Wait for the task to complete
        logger.info("Waiting for task to complete...")
        for _ in range(10):
            time.sleep(1)
            response = requests.get(f"{base_url}/task/{task_id}", headers=headers)
            if response.status_code == 200:
                task_result = response.json()
                if task_result.get("status") == "completed":
                    logger.info(f"Task completed: {task_result.get('result')}")
                    break
                elif task_result.get("status") == "failed":
                    logger.info(f"Task failed: {task_result.get('result')}")
                    break
                else:
                    logger.info(f"Task status: {task_result.get('status')}")
            else:
                logger.info(f"Error getting task status: {response.status_code}")
    
    # Test the tasks endpoint
    logger.info("\nTesting tasks endpoint...")
    response = requests.get(f"{base_url}/tasks", headers=headers)
    logger.info(f"Response: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        logger.info(f"Tasks: {len(result.get('tasks', []))} found")
    
    # Test the memory endpoints
    logger.info("\nTesting memory endpoints...")
    
    # Store a memory
    data = {
        "key": "test_memory",
        "value": "This is a test memory",
        "category": "test",
        "importance": 3
    }
    response = requests.post(f"{base_url}/memory", headers=headers, json=data)
    logger.info(f"Store memory response: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        memory_id = result.get("memory_id")
        logger.info(f"Memory ID: {memory_id}")
        
        # Get the memory
        response = requests.get(f"{base_url}/memory/{memory_id}", headers=headers)
        logger.info(f"Get memory response: {response.status_code}")
        if response.status_code == 200:
            memory = response.json()
            logger.info(f"Memory: {memory}")
        
        # Update the memory
        data = {
            "value": "This is an updated test memory",
            "importance": 5
        }
        response = requests.put(f"{base_url}/memory/{memory_id}", headers=headers, json=data)
        logger.info(f"Update memory response: {response.status_code}")
        
        # Get the updated memory
        response = requests.get(f"{base_url}/memory/{memory_id}", headers=headers)
        if response.status_code == 200:
            memory = response.json()
            logger.info(f"Updated memory: {memory}")
        
        # Delete the memory
        response = requests.delete(f"{base_url}/memory/{memory_id}", headers=headers)
        logger.info(f"Delete memory response: {response.status_code}")
    
    # Retrieve memories
    response = requests.get(f"{base_url}/memory", headers=headers)
    logger.info(f"Retrieve memories response: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        logger.info(f"Memories: {len(result.get('memories', []))} found")
    
    logger.info("\nAPI tests completed")

def main():
    """Run the API tests."""
    parser = argparse.ArgumentParser(description="Test the Droid agent custom API")
    parser.add_argument("--url", type=str, default="http://localhost:5000", help="API server URL")
    parser.add_argument("--api-key", type=str, default="droid-api-key", help="API key for authentication")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = "DEBUG" if args.debug else "INFO"
    setup_logging({"level": log_level})
    logger = logging.getLogger(__name__)
    
    logger.info(f"Testing API at {args.url} with key {args.api_key}")
    
    try:
        test_api(args.url, args.api_key)
    except requests.exceptions.ConnectionError:
        logger.error(f"Could not connect to API server at {args.url}")
        logger.error("Make sure the API server is running")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error testing API: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()