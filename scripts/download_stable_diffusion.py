#!/usr/bin/env python3
"""
Script to download Stable Diffusion models from Hugging Face.
"""
import os
import sys
import argparse
import logging
from diffusers import StableDiffusionPipeline, StableDiffusionXLPipeline

# Add the parent directory to the path so we can import the droid package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from droid.utils.logger import setup_logging

def download_stable_diffusion(model_type="sd", output_dir=None):
    """
    Download Stable Diffusion model from Hugging Face.
    
    Args:
        model_type: Type of model to download (sd or sdxl)
        output_dir: Directory to save the model to
    """
    # Set up logging
    setup_logging({"level": "INFO"})
    logger = logging.getLogger(__name__)
    
    # Determine model ID based on type
    if model_type == "sd":
        model_id = "runwayml/stable-diffusion-v1-5"
        pipeline_class = StableDiffusionPipeline
    elif model_type == "sdxl":
        model_id = "stabilityai/stable-diffusion-xl-base-1.0"
        pipeline_class = StableDiffusionXLPipeline
    else:
        logger.error(f"Invalid model type: {model_type}. Must be 'sd' or 'sdxl'.")
        return False
    
    # Determine output directory
    if output_dir is None:
        if model_type == "sd":
            output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "stable-diffusion-2.1")
        else:
            output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "stable-diffusion-xl")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Download the model
    try:
        logger.info(f"Downloading Stable Diffusion model from {model_id}...")
        
        # Check if the model already exists
        if os.path.exists(os.path.join(output_dir, "model_index.json")):
            logger.info(f"Model already exists at {output_dir}")
            return True
        
        # Download the model
        pipeline = pipeline_class.from_pretrained(
            model_id,
            cache_dir=output_dir,
            local_files_only=False,
            resume_download=True
        )
        
        # Save the model
        pipeline.save_pretrained(output_dir)
        logger.info(f"Model downloaded and saved to {output_dir}")
        return True
        
    except Exception as e:
        logger.error(f"Error downloading model: {str(e)}")
        return False

def main():
    """Run the script."""
    parser = argparse.ArgumentParser(description="Download Stable Diffusion model from Hugging Face")
    parser.add_argument("--model-type", type=str, choices=["sd", "sdxl"], default="sd",
                        help="Type of model to download (sd or sdxl)")
    parser.add_argument("--output-dir", type=str, default=None,
                        help="Directory to save the model to")
    
    args = parser.parse_args()
    
    success = download_stable_diffusion(args.model_type, args.output_dir)
    
    if success:
        print("Model downloaded successfully")
        sys.exit(0)
    else:
        print("Failed to download model")
        sys.exit(1)

if __name__ == "__main__":
    main()