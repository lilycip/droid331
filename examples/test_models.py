#!/usr/bin/env python3
"""
Example script to test the models.
"""
import os
import sys
import argparse
import logging

# Add the parent directory to the path so we can import the droid package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from droid.core.model_manager import ModelManager
from droid.utils.config_manager import ConfigManager
from droid.utils.logger import setup_logging

def test_llm(model_manager, model_name="llama-3.1"):
    """
    Test an LLM model.
    
    Args:
        model_manager: ModelManager instance
        model_name: Name of the model to test
    """
    logger = logging.getLogger(__name__)
    
    # Test prompts
    prompts = [
        "Write a short poem about artificial intelligence.",
        "Explain the concept of neural networks in simple terms.",
        "What are the ethical considerations of AI development?",
        "Write a short story about a robot that becomes sentient."
    ]
    
    # Test the model
    for i, prompt in enumerate(prompts):
        logger.info(f"Testing prompt {i+1}: {prompt[:30]}...")
        
        try:
            response = model_manager.run_model(model_name, prompt)
            logger.info(f"Response: {response[:100]}...")
            print(f"\nPrompt: {prompt}\n")
            print(f"Response: {response}\n")
            print("-" * 80)
        except Exception as e:
            logger.error(f"Error running model: {str(e)}")

def test_diffusion(model_manager, model_name="stable-diffusion-2.1"):
    """
    Test a diffusion model.
    
    Args:
        model_manager: ModelManager instance
        model_name: Name of the model to test
    """
    logger = logging.getLogger(__name__)
    
    # Test prompts
    prompts = [
        "A beautiful landscape with mountains and a lake",
        "A futuristic city with flying cars",
        "A cute robot playing with a cat",
        "A photorealistic portrait of a cyberpunk character"
    ]
    
    # Test the model
    for i, prompt in enumerate(prompts):
        logger.info(f"Testing prompt {i+1}: {prompt[:30]}...")
        
        try:
            result = model_manager.run_model(model_name, prompt)
            
            if isinstance(result, dict) and "image_path" in result:
                logger.info(f"Image generated at: {result['image_path']}")
                print(f"\nPrompt: {prompt}")
                print(f"Image saved to: {result['image_path']}\n")
            else:
                logger.info(f"Result: {result}")
                print(f"\nPrompt: {prompt}")
                print(f"Result: {result}\n")
                
            print("-" * 80)
        except Exception as e:
            logger.error(f"Error running model: {str(e)}")

def main():
    """Run the example."""
    parser = argparse.ArgumentParser(description="Test AI models")
    parser.add_argument("--model-type", type=str, choices=["llm", "diffusion", "all"], default="all",
                        help="Type of model to test")
    parser.add_argument("--model-name", type=str, default=None,
                        help="Name of the model to test")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = "DEBUG" if args.debug else "INFO"
    setup_logging({"level": log_level})
    logger = logging.getLogger(__name__)
    
    # Load configuration
    config_manager = ConfigManager()
    config = config_manager.get_config()
    
    # Initialize model manager
    model_manager = ModelManager(config.get("models", {}))
    
    try:
        # Test models based on type
        if args.model_type == "llm" or args.model_type == "all":
            model_name = args.model_name if args.model_name else "llama-3.1"
            logger.info(f"Testing LLM model: {model_name}")
            test_llm(model_manager, model_name)
        
        if args.model_type == "diffusion" or args.model_type == "all":
            model_name = args.model_name if args.model_name else "stable-diffusion-2.1"
            logger.info(f"Testing diffusion model: {model_name}")
            test_diffusion(model_manager, model_name)
            
    except Exception as e:
        logger.error(f"Error testing models: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()