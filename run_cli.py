#!/usr/bin/env python3
"""
Run the Droid agent in CLI mode.
"""
import os
import sys
import json
import argparse
import logging
from droid.core.agent import Agent
from droid.utils.logger import setup_logging

def main():
    """Run the agent in CLI mode."""
    parser = argparse.ArgumentParser(description="Run the Droid agent in CLI mode")
    parser.add_argument("--config", type=str, default="config/config.yaml", help="Path to the configuration file")
    parser.add_argument("--task", type=str, help="Task to execute")
    parser.add_argument("--params", type=str, help="Parameters for the task (JSON string)")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = "DEBUG" if args.debug else "INFO"
    setup_logging({"level": log_level})
    logger = logging.getLogger(__name__)
    
    # Create the agent
    agent = Agent(args.config)
    
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
        print("Droid AI Agent - Interactive Mode")
        print("Type 'exit' to quit")
        print("Type 'help' for a list of commands")
        
        while True:
            try:
                command = input("\nDroid> ")
                
                if command.lower() == "exit":
                    break
                
                if command.lower() == "help":
                    print("\nAvailable commands:")
                    print("  task <task_name> <params>  - Execute a task")
                    print("  list tasks                - List available tasks")
                    print("  list modules              - List loaded modules")
                    print("  exit                      - Exit the program")
                    print("  help                      - Show this help message")
                    continue
                
                if command.lower().startswith("list tasks"):
                    print("\nAvailable tasks:")
                    for task in agent.task_scheduler.task_definitions.keys():
                        print(f"  {task}")
                    continue
                
                if command.lower().startswith("list modules"):
                    print("\nLoaded modules:")
                    for module_name, module in agent.modules.items():
                        print(f"  {module_name}: {type(module).__name__}")
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