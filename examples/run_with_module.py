#!/usr/bin/env python3
"""
Run the Droid agent with a specific module.
"""
import os
import sys
import json
import argparse
import logging
from droid.core.agent import Agent
from droid.utils.logger import setup_logging

def main():
    """Run the agent with a specific module."""
    parser = argparse.ArgumentParser(description="Run the Droid agent with a specific module")
    parser.add_argument("--module", type=str, required=True, help="Module to use (e.g., content_generator, social_media)")
    parser.add_argument("--config", type=str, default="config/config.yaml", help="Path to the configuration file")
    parser.add_argument("--method", type=str, help="Method to call on the module")
    parser.add_argument("--params", type=str, help="Parameters for the method (JSON string)")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = "DEBUG" if args.debug else "INFO"
    setup_logging({"level": log_level})
    logger = logging.getLogger(__name__)
    
    # Create the agent
    agent = Agent(args.config)
    
    # Check if the module exists
    if args.module not in agent.modules:
        logger.error(f"Module '{args.module}' not found. Available modules: {', '.join(agent.modules.keys())}")
        sys.exit(1)
    
    module = agent.modules[args.module]
    
    # Execute a specific method
    if args.method:
        if not hasattr(module, args.method):
            logger.error(f"Method '{args.method}' not found in module '{args.module}'")
            sys.exit(1)
        
        params = {}
        if args.params:
            try:
                params = json.loads(args.params)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON parameters: {args.params}")
                sys.exit(1)
        
        logger.info(f"Executing method: {args.method} on module: {args.module}")
        method = getattr(module, args.method)
        result = method(**params)
        print(json.dumps(result, indent=2) if isinstance(result, (dict, list)) else result)
        return
    
    # Run in interactive mode
    if args.interactive:
        print(f"Droid AI Agent - {args.module.capitalize()} Module Interactive Mode")
        print("Type 'exit' to quit")
        print("Type 'help' for a list of commands")
        
        # Get methods of the module
        methods = [method for method in dir(module) if callable(getattr(module, method)) and not method.startswith('_')]
        
        while True:
            try:
                command = input(f"\n{args.module}> ")
                
                if command.lower() == "exit":
                    break
                
                if command.lower() == "help":
                    print("\nAvailable methods:")
                    for method in methods:
                        print(f"  {method}")
                    print("\nUsage: method_name param1=value1 param2=value2")
                    continue
                
                if command.lower() == "info":
                    print(f"\nModule: {args.module}")
                    print(f"Type: {type(module).__name__}")
                    print(f"Methods: {', '.join(methods)}")
                    continue
                
                # Parse the command
                parts = command.split(" ", 1)
                method_name = parts[0]
                
                if method_name not in methods:
                    print(f"Error: Method '{method_name}' not found")
                    continue
                
                # Parse parameters
                params = {}
                if len(parts) > 1:
                    param_str = parts[1]
                    try:
                        # Try to parse as JSON
                        params = json.loads(param_str)
                    except json.JSONDecodeError:
                        # Try to parse as key=value pairs
                        try:
                            for pair in param_str.split():
                                key, value = pair.split('=', 1)
                                params[key] = value
                        except ValueError:
                            print(f"Error: Invalid parameters format: {param_str}")
                            continue
                
                # Execute the method
                method = getattr(module, method_name)
                result = method(**params)
                print(json.dumps(result, indent=2) if isinstance(result, (dict, list)) else result)
                
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {str(e)}")
        
        return
    
    # Print module information
    print(f"Module: {args.module}")
    print(f"Type: {type(module).__name__}")
    print("Methods:")
    for method in dir(module):
        if callable(getattr(module, method)) and not method.startswith('_'):
            print(f"  {method}")

if __name__ == "__main__":
    main()