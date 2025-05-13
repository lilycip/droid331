#!/usr/bin/env python3
"""
Script to download Llama 3.1 model from Hugging Face.
"""
import os
import sys
import argparse
import logging
from huggingface_hub import hf_hub_download

# Add the parent directory to the path so we can import the droid package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from droid.utils.logger import setup_logging

def download_llama_model(model_size="8b", output_dir=None):
    """
    Download Llama 3.1 model from Hugging Face.
    
    Args:
        model_size: Size of the model to download (8b or 70b)
        output_dir: Directory to save the model to
    """
    # Set up logging
    setup_logging({"level": "INFO"})
    logger = logging.getLogger(__name__)
    
    # Determine model ID based on size
    if model_size == "8b":
        model_id = "meta-llama/Meta-Llama-3-8B-GGUF"
        filename = "Meta-Llama-3-8B.Q4_K_M.gguf"
    elif model_size == "70b":
        model_id = "meta-llama/Meta-Llama-3-70B-GGUF"
        filename = "Meta-Llama-3-70B.Q4_K_M.gguf"
    else:
        logger.error(f"Invalid model size: {model_size}. Must be '8b' or '70b'.")
        return False
    
    # Determine output directory
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", f"llama-3.1-{model_size}")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Download the model
    try:
        logger.info(f"Downloading Llama 3.1 {model_size} model from {model_id}...")
        
        # You need to have a Hugging Face token with access to the model
        # Set the token with: huggingface-cli login
        # or set the HF_TOKEN environment variable
        
        output_path = os.path.join(output_dir, "model.gguf")
        
        # Check if the model already exists
        if os.path.exists(output_path):
            logger.info(f"Model already exists at {output_path}")
            return True
        
        # Download the model
        hf_hub_download(
            repo_id=model_id,
            filename=filename,
            local_dir=output_dir,
            local_dir_use_symlinks=False,
            resume_download=True,
            token=os.environ.get("HF_TOKEN")
        )
        
        # Rename the downloaded file to model.gguf
        downloaded_path = os.path.join(output_dir, filename)
        if os.path.exists(downloaded_path):
            os.rename(downloaded_path, output_path)
            logger.info(f"Model downloaded and saved to {output_path}")
            return True
        else:
            logger.error(f"Downloaded file not found at {downloaded_path}")
            return False
        
    except Exception as e:
        logger.error(f"Error downloading model: {str(e)}")
        return False

def main():
    """Run the script."""
    parser = argparse.ArgumentParser(description="Download Llama 3.1 model from Hugging Face")
    parser.add_argument("--model-size", type=str, choices=["8b", "70b"], default="8b",
                        help="Size of the model to download (8b or 70b)")
    parser.add_argument("--output-dir", type=str, default=None,
                        help="Directory to save the model to")
    
    args = parser.parse_args()
    
    success = download_llama_model(args.model_size, args.output_dir)
    
    if success:
        print("Model downloaded successfully")
        sys.exit(0)
    else:
        print("Failed to download model")
        sys.exit(1)

if __name__ == "__main__":
    main()