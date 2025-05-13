#!/usr/bin/env python3
"""
Example of running the Droid agent with a custom configuration.
"""
import os
import sys
import json
import argparse
import logging
import yaml
from droid.core.agent import Agent
from droid.utils.logger import setup_logging

def main():
    """Run the agent with a custom configuration."""
    parser = argparse.ArgumentParser(description="Run the Droid agent with a custom configuration")
    parser.add_argument("--output", type=str, default="custom_config.yaml", help="Path to save the custom configuration")
    parser.add_argument("--run", action="store_true", help="Run the agent with the custom configuration")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = "DEBUG" if args.debug else "INFO"
    setup_logging({"level": log_level})
    logger = logging.getLogger(__name__)
    
    # Create a custom configuration
    custom_config = {
        "agent": {
            "name": "Custom Droid Agent",
            "description": "A custom configuration for the Droid agent",
            "version": "1.0.0"
        },
        "models": {
            "llama": {
                "type": "llama",
                "path": "/path/to/llama/model",
                "context_length": 4096,
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 512
            },
            "stable_diffusion": {
                "type": "stable_diffusion",
                "version": "2.1",
                "path": "/path/to/stable_diffusion/model",
                "width": 512,
                "height": 512,
                "num_inference_steps": 30,
                "guidance_scale": 7.5
            }
        },
        "modules": {
            "content_generator": {
                "enabled": True,
                "default_model": "llama",
                "settings": {
                    "max_length": 1000,
                    "formats": ["text", "image", "meme"]
                }
            },
            "image_generator": {
                "enabled": True,
                "default_model": "stable_diffusion",
                "settings": {
                    "output_dir": "/tmp/droid/images",
                    "formats": ["png", "jpg"]
                }
            },
            "meme_generator": {
                "enabled": True,
                "default_model": "stable_diffusion",
                "settings": {
                    "templates_dir": "/path/to/meme/templates",
                    "output_dir": "/tmp/droid/memes"
                }
            },
            "social_media": {
                "enabled": True,
                "platforms": {
                    "twitter": {
                        "enabled": True,
                        "api_key": "YOUR_API_KEY",
                        "api_secret": "YOUR_API_SECRET",
                        "access_token": "YOUR_ACCESS_TOKEN",
                        "access_token_secret": "YOUR_ACCESS_TOKEN_SECRET"
                    },
                    "instagram": {
                        "enabled": False,
                        "username": "YOUR_USERNAME",
                        "password": "YOUR_PASSWORD"
                    },
                    "facebook": {
                        "enabled": False,
                        "api_key": "YOUR_API_KEY",
                        "api_secret": "YOUR_API_SECRET"
                    }
                }
            }
        },
        "memory": {
            "type": "sqlite",
            "path": "/tmp/droid/memory.db",
            "max_size": 1000
        },
        "scheduler": {
            "enabled": True,
            "max_tasks": 10,
            "default_priority": 5
        },
        "logging": {
            "level": "INFO",
            "file": "/tmp/droid/droid.log",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    }
    
    # Save the custom configuration
    with open(args.output, "w") as f:
        yaml.dump(custom_config, f, default_flow_style=False)
    
    logger.info(f"Custom configuration saved to {args.output}")
    
    # Run the agent with the custom configuration
    if args.run:
        logger.info(f"Running agent with custom configuration from {args.output}")
        agent = Agent(config=custom_config)
        agent.run()
    else:
        print(f"Custom configuration saved to {args.output}")
        print("To run the agent with this configuration, use:")
        print(f"  python main.py --config {args.output}")
        print("Or run this script with the --run flag:")
        print(f"  python {sys.argv[0]} --output {args.output} --run")

if __name__ == "__main__":
    main()