#!/usr/bin/env python3
"""
Run the Droid agent with Stable Diffusion model.
"""
import os
import sys
import json
import argparse
import logging
from droid.core.agent import Agent
from droid.utils.logger import setup_logging

def main():
    """Run the agent with Stable Diffusion model."""
    parser = argparse.ArgumentParser(description="Run the Droid agent with Stable Diffusion model")
    parser.add_argument("--model_path", type=str, help="Path to the Stable Diffusion model (optional)")
    parser.add_argument("--model_version", type=str, default="2.1", help="Stable Diffusion version (2.1 or xl)")
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
            "name": f"Droid with Stable Diffusion {args.model_version}"
        },
        "models": {
            "stable_diffusion": {
                "type": "stable_diffusion",
                "version": args.model_version,
                "path": args.model_path if args.model_path else None,
                "width": 512,
                "height": 512,
                "num_inference_steps": 30,
                "guidance_scale": 7.5
            }
        },
        "modules": {
            "image_generator": {
                "enabled": True,
                "default_model": "stable_diffusion"
            },
            "meme_generator": {
                "enabled": True,
                "default_model": "stable_diffusion"
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
        print(f"Droid AI Agent with Stable Diffusion {args.model_version} - Interactive Mode")
        print("Type 'exit' to quit")
        print("Type 'help' for a list of commands")
        
        while True:
            try:
                command = input("\nDroid> ")
                
                if command.lower() == "exit":
                    break
                
                if command.lower() == "help":
                    print("\nAvailable commands:")
                    print("  generate <prompt>         - Generate an image with Stable Diffusion")
                    print("  meme <topic> <style>      - Generate a meme")
                    print("  task <task_name> <params> - Execute a task")
                    print("  exit                      - Exit the program")
                    print("  help                      - Show this help message")
                    continue
                
                if command.lower().startswith("generate "):
                    prompt = command[9:]
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