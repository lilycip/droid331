#!/usr/bin/env python3
"""
Example script to test image generation with Stable Diffusion.
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

def test_image_generation(model_manager, model_name="stable-diffusion-2.1", output_dir=None):
    """
    Test image generation with Stable Diffusion.
    
    Args:
        model_manager: ModelManager instance
        model_name: Name of the model to test
        output_dir: Directory to save generated images
    """
    logger = logging.getLogger(__name__)
    
    # Create output directory if it doesn't exist
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
    
    os.makedirs(output_dir, exist_ok=True)
    
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
            # Run the model with fewer steps for faster inference
            prompt_slug = prompt.lower().replace(" ", "_")[:20]
            filename = f"test_{model_name}_{i+1}_{prompt_slug}.png"
            result = model_manager.run_model(
                model_name, 
                prompt, 
                output_dir=output_dir, 
                num_inference_steps=10,
                filename=filename
            )
            
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
            logger.error(f"Error generating image: {str(e)}")

def main():
    """Run the example."""
    parser = argparse.ArgumentParser(description="Test image generation with Stable Diffusion")
    parser.add_argument("--model", type=str, choices=["stable-diffusion-2.1", "stable-diffusion-xl"], 
                        default="stable-diffusion-2.1", help="Model to use for image generation")
    parser.add_argument("--output-dir", type=str, default=None, help="Directory to save generated images")
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
        # Test image generation
        logger.info(f"Testing image generation with model: {args.model}")
        test_image_generation(model_manager, args.model, args.output_dir)
    except Exception as e:
        logger.error(f"Error testing image generation: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()