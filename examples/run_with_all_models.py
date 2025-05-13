#!/usr/bin/env python3
"""
Run the Droid agent with all supported models.
"""
import os
import sys
import json
import argparse
import logging
from droid.core.agent import Agent
from droid.utils.logger import setup_logging

def main():
    """Run the agent with all supported models."""
    parser = argparse.ArgumentParser(description="Run the Droid agent with all supported models")
    parser.add_argument("--llama_path", type=str, help="Path to the Llama 3.1 model")
    parser.add_argument("--sd_path", type=str, help="Path to the Stable Diffusion model")
    parser.add_argument("--sd_version", type=str, default="2.1", help="Stable Diffusion version (2.1 or xl)")
    parser.add_argument("--task", type=str, help="Task to execute")
    parser.add_argument("--params", type=str, help="Parameters for the task (JSON string)")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = "DEBUG" if args.debug else "INFO"
    setup_logging({"level": log_level})
    logger = logging.getLogger(__name__)
    
    # Create a custom configuration
    config = {
        "agent": {
            "name": "Droid with All Models"
        },
        "models": {
            "llama": {
                "type": "llama",
                "path": args.llama_path,
                "context_length": 4096,
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 512
            },
            "stable_diffusion": {
                "type": "stable_diffusion",
                "version": args.sd_version,
                "path": args.sd_path if args.sd_path else None,
                "width": 512,
                "height": 512,
                "num_inference_steps": 30,
                "guidance_scale": 7.5
            }
        },
        "modules": {
            "content_generator": {
                "enabled": True,
                "default_model": "llama"
            },
            "image_generator": {
                "enabled": True,
                "default_model": "stable_diffusion"
            },
            "meme_generator": {
                "enabled": True,
                "default_model": "stable_diffusion"
            },
            "social_media": {
                "enabled": True
            }
        }
    }
    
    # Create the agent with the custom configuration
    agent = Agent(config=config)
    
    # Execute a specific task
    if args.task:
        params = {}
        if args.params:
            try:
                params = json.loads(args.params)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON parameters: {args.params}")
                sys.exit(1)
        
        logger.info(f"Executing task: {args.task}")
        result = agent.execute_task(args.task, params)
        print(json.dumps(result, indent=2))
        return
    
    # Run in interactive mode
    if args.interactive:
        print("Droid AI Agent with All Models - Interactive Mode")
        print("Type 'exit' to quit")
        print("Type 'help' for a list of commands")
        
        while True:
            try:
                command = input("\nDroid> ")
                
                if command.lower() == "exit":
                    break
                
                if command.lower() == "help":
                    print("\nAvailable commands:")
                    print("  text <prompt>             - Generate text with Llama 3.1")
                    print("  image <prompt>            - Generate an image with Stable Diffusion")
                    print("  meme <topic> <style>      - Generate a meme")
                    print("  post <platform> <content> - Post content to social media")
                    print("  task <task_name> <params> - Execute a task")
                    print("  exit                      - Exit the program")
                    print("  help                      - Show this help message")
                    continue
                
                if command.lower().startswith("text "):
                    prompt = command[5:]
                    params = {
                        "content_type": "text",
                        "prompt": prompt,
                        "model": "llama"
                    }
                    
                    print(f"Generating text with prompt: {prompt}")
                    result = agent.execute_task("generate_content", params)
                    if result and "text" in result:
                        print(f"\nGenerated text:\n{result['text']}")
                    else:
                        print("Error generating text")
                    continue
                
                if command.lower().startswith("image "):
                    prompt = command[6:]
                    params = {
                        "content_type": "image",
                        "prompt": prompt,
                        "model": "stable_diffusion"
                    }
                    
                    print(f"Generating image with prompt: {prompt}")
                    result = agent.execute_task("generate_content", params)
                    if result and "filepath" in result:
                        print(f"\nImage generated at: {result['filepath']}")
                    else:
                        print("Error generating image")
                    continue
                
                if command.lower().startswith("meme "):
                    parts = command.split(" ", 2)
                    if len(parts) < 2:
                        print("Error: Missing meme topic")
                        continue
                    
                    topic = parts[1]
                    style = "funny"
                    if len(parts) > 2:
                        style = parts[2]
                    
                    params = {
                        "content_type": "meme",
                        "topic": topic,
                        "style": style
                    }
                    
                    print(f"Generating meme about {topic} in {style} style")
                    result = agent.execute_task("generate_content", params)
                    if result and "filepath" in result:
                        print(f"\nMeme generated at: {result['filepath']}")
                        if "caption" in result:
                            print(f"Caption: {result['caption']}")
                    else:
                        print("Error generating meme")
                    continue
                
                if command.lower().startswith("post "):
                    parts = command.split(" ", 2)
                    if len(parts) < 3:
                        print("Error: Missing platform or content")
                        continue
                    
                    platform = parts[1]
                    content = parts[2]
                    
                    params = {
                        "platform": platform,
                        "content": content
                    }
                    
                    print(f"Posting to {platform}: {content}")
                    result = agent.execute_task("post_content", params)
                    print(json.dumps(result, indent=2))
                    continue
                
                if command.lower().startswith("task "):
                    parts = command.split(" ", 2)
                    if len(parts) < 2:
                        print("Error: Missing task name")
                        continue
                    
                    task_name = parts[1]
                    params = {}
                    
                    if len(parts) > 2:
                        try:
                            params = json.loads(parts[2])
                        except json.JSONDecodeError:
                            print(f"Error: Invalid JSON parameters: {parts[2]}")
                            continue
                    
                    print(f"Executing task: {task_name}")
                    result = agent.execute_task(task_name, params)
                    print(json.dumps(result, indent=2))
                    continue
                
                print(f"Unknown command: {command}")
                
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {str(e)}")
        
        return
    
    # Run the agent
    logger.info("Starting the agent")
    agent.run()

if __name__ == "__main__":
    main()