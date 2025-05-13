#!/usr/bin/env python3
"""
Example of creating and using a custom module with the Droid agent.
"""
import os
import sys
import json
import argparse
import logging
from droid.core.agent import Agent
from droid.utils.logger import setup_logging

class CustomModule:
    """A custom module for the Droid agent."""
    
    def __init__(self, config=None):
        """Initialize the custom module."""
        self.config = config or {}
        self.name = self.config.get("name", "Custom Module")
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initializing {self.name}")
    
    def hello(self, name="World"):
        """Say hello to someone."""
        message = f"Hello, {name}!"
        self.logger.info(message)
        return {"message": message}
    
    def calculate(self, operation, a, b):
        """Perform a calculation."""
        a = float(a)
        b = float(b)
        
        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            if b == 0:
                raise ValueError("Cannot divide by zero")
            result = a / b
        else:
            raise ValueError(f"Unknown operation: {operation}")
        
        self.logger.info(f"Calculated {a} {operation} {b} = {result}")
        return {"result": result}
    
    def generate_report(self, title, items):
        """Generate a simple report."""
        if not isinstance(items, list):
            raise ValueError("Items must be a list")
        
        report = {
            "title": title,
            "items": items,
            "count": len(items),
            "timestamp": "2025-05-13"  # In a real module, use datetime.now()
        }
        
        self.logger.info(f"Generated report: {title} with {len(items)} items")
        return report

def main():
    """Run the agent with a custom module."""
    parser = argparse.ArgumentParser(description="Run the Droid agent with a custom module")
    parser.add_argument("--config", type=str, default="config/config.yaml", help="Path to the configuration file")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = "DEBUG" if args.debug else "INFO"
    setup_logging({"level": log_level})
    logger = logging.getLogger(__name__)
    
    # Create the agent
    agent = Agent(args.config)
    
    # Register the custom module
    custom_module = CustomModule({"name": "My Custom Module"})
    agent.register_module("custom", custom_module)
    
    logger.info("Custom module registered")
    
    # Run in interactive mode
    if args.interactive:
        print("Droid AI Agent with Custom Module - Interactive Mode")
        print("Type 'exit' to quit")
        print("Type 'help' for a list of commands")
        
        while True:
            try:
                command = input("\nDroid> ")
                
                if command.lower() == "exit":
                    break
                
                if command.lower() == "help":
                    print("\nAvailable commands:")
                    print("  hello <name>              - Say hello to someone")
                    print("  calculate <op> <a> <b>    - Perform a calculation")
                    print("  report <title> <items>    - Generate a report")
                    print("  modules                   - List all modules")
                    print("  exit                      - Exit the program")
                    print("  help                      - Show this help message")
                    continue
                
                if command.lower() == "modules":
                    print("\nLoaded modules:")
                    for module_name, module in agent.modules.items():
                        print(f"  {module_name}: {type(module).__name__}")
                    continue
                
                if command.lower().startswith("hello "):
                    name = command[6:]
                    result = custom_module.hello(name)
                    print(result["message"])
                    continue
                
                if command.lower().startswith("calculate "):
                    parts = command.split(" ")
                    if len(parts) < 4:
                        print("Error: Missing parameters")
                        print("Usage: calculate <operation> <a> <b>")
                        continue
                    
                    operation = parts[1]
                    a = parts[2]
                    b = parts[3]
                    
                    try:
                        result = custom_module.calculate(operation, a, b)
                        print(f"Result: {result['result']}")
                    except ValueError as e:
                        print(f"Error: {str(e)}")
                    continue
                
                if command.lower().startswith("report "):
                    parts = command.split(" ", 2)
                    if len(parts) < 3:
                        print("Error: Missing parameters")
                        print("Usage: report <title> <items>")
                        continue
                    
                    title = parts[1]
                    try:
                        items = json.loads(parts[2])
                    except json.JSONDecodeError:
                        print(f"Error: Invalid JSON items: {parts[2]}")
                        continue
                    
                    try:
                        result = custom_module.generate_report(title, items)
                        print(json.dumps(result, indent=2))
                    except ValueError as e:
                        print(f"Error: {str(e)}")
                    continue
                
                print(f"Unknown command: {command}")
                
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {str(e)}")
        
        return
    
    # Run some example commands
    print("Running example commands with custom module:")
    
    print("\n1. Say hello:")
    result = custom_module.hello("Droid User")
    print(result["message"])
    
    print("\n2. Perform a calculation:")
    result = custom_module.calculate("multiply", 5, 7)
    print(f"Result: {result['result']}")
    
    print("\n3. Generate a report:")
    result = custom_module.generate_report("Test Report", ["Item 1", "Item 2", "Item 3"])
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()