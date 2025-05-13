#!/usr/bin/env python3
"""
Enhanced Image Generation Example - Demonstrates the improved image generation capabilities.
"""
import os
import sys
import argparse
import logging
from datetime import datetime

# Add the parent directory to the path so we can import the droid package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from droid.core.model_manager import ModelManager
from droid.core.memory import MemorySystem
from droid.modules.image_generator import ImageGenerator
from droid.utils.config_manager import ConfigManager
from droid.utils.logger import setup_logging

def generate_images(config, args):
    """
    Generate images with the specified parameters.
    
    Args:
        config: Configuration dictionary
        args: Command-line arguments
    """
    logger = logging.getLogger(__name__)
    
    # Create output directory if it doesn't exist
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize components
    model_manager = ModelManager(config.get("models", {}))
    memory = MemorySystem(config.get("memory", {}))
    
    # Initialize image generator
    image_generator = ImageGenerator(
        config.get("modules", {}).get("image_generator", {}),
        model_manager,
        memory
    )
    
    # Set up prompts
    if args.prompt_file:
        with open(args.prompt_file, 'r') as f:
            prompts = [line.strip() for line in f if line.strip()]
    else:
        prompts = [args.prompt]
    
    # Generate images for each prompt
    for i, prompt in enumerate(prompts):
        logger.info(f"Generating image {i+1}/{len(prompts)}: {prompt[:50]}...")
        print(f"\nGenerating image for prompt: {prompt}")
        
        # Create a timestamp-based filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prompt_slug = prompt.lower().replace(" ", "_")[:20]
        filename = f"{args.prefix}_{timestamp}_{prompt_slug}.png"
        
        # Generate the image
        result = image_generator.generate({
            "prompt": prompt,
            "model": args.model,
            "negative_prompt": args.negative_prompt,
            "width": args.width,
            "height": args.height,
            "guidance_scale": args.guidance_scale,
            "num_inference_steps": args.steps
        })
        
        if result["success"]:
            print(f"✅ Image generated successfully!")
            print(f"📁 Saved to: {result['filepath']}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
        
        print("-" * 80)

def main():
    """Run the example."""
    parser = argparse.ArgumentParser(description="Enhanced Image Generation Example")
    
    # Model selection
    parser.add_argument("--model", type=str, 
                        choices=["stable-diffusion-2.1", "stable-diffusion-xl"], 
                        default="stable-diffusion-2.1", 
                        help="Model to use for image generation")
    
    # Prompt options
    parser.add_argument("--prompt", type=str, 
                        default="A beautiful landscape with mountains and a lake at sunset",
                        help="Text prompt for image generation")
    parser.add_argument("--prompt-file", type=str, 
                        help="File containing prompts (one per line)")
    parser.add_argument("--negative-prompt", type=str, 
                        default="blurry, distorted, low quality",
                        help="Negative prompt to avoid certain elements")
    
    # Image parameters
    parser.add_argument("--width", type=int, default=512, 
                        help="Width of generated image")
    parser.add_argument("--height", type=int, default=512, 
                        help="Height of generated image")
    parser.add_argument("--steps", type=int, default=25, 
                        help="Number of inference steps")
    parser.add_argument("--guidance-scale", type=float, default=7.5, 
                        help="Guidance scale for image generation")
    
    # Output options
    parser.add_argument("--output-dir", type=str, default="./output", 
                        help="Directory to save generated images")
    parser.add_argument("--prefix", type=str, default="generated", 
                        help="Filename prefix for generated images")
    
    # Logging options
    parser.add_argument("--debug", action="store_true", 
                        help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = "DEBUG" if args.debug else "INFO"
    setup_logging({"level": log_level})
    logger = logging.getLogger(__name__)
    
    # Load configuration
    config_manager = ConfigManager()
    config = config_manager.get_config()
    
    try:
        # Generate images
        generate_images(config, args)
    except Exception as e:
        logger.error(f"Error generating images: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()