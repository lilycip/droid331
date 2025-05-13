#!/usr/bin/env python3
"""
Run a specific task with the Droid agent.
"""
import os
import sys
import json
import argparse
import logging
from droid.core.agent import Agent
from droid.utils.logger import setup_logging

def main():
    """Run a specific task with the agent."""
    parser = argparse.ArgumentParser(description="Run a specific task with the Droid agent")
    parser.add_argument("--config", type=str, default="config/config.yaml", help="Path to the configuration file")
    parser.add_argument("--task", type=str, required=True, help="Task to execute")
    parser.add_argument("--params", type=str, help="Parameters for the task (JSON string)")
    parser.add_argument("--params-file", type=str, help="Path to a JSON file containing parameters")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = "DEBUG" if args.debug else "INFO"
    setup_logging({"level": log_level})
    logger = logging.getLogger(__name__)
    
    # Get parameters
    params = {}
    if args.params:
        try:
            params = json.loads(args.params)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON parameters: {args.params}")
            sys.exit(1)
    elif args.params_file:
        try:
            with open(args.params_file, 'r') as f:
                params = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error loading parameters file: {str(e)}")
            sys.exit(1)
    
    # Create the agent
    agent = Agent(args.config)
    
    # Execute the task
    logger.info(f"Executing task: {args.task}")
    result = agent.execute_task(args.task, params)
    
    # Print the result
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()