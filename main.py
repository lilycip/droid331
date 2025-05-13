#!/usr/bin/env python3
"""
Main entry point for the Droid AI Agent.
"""
import os
import sys
import argparse
import logging

from droid.core.agent import Agent
from droid.utils.logger import setup_logging
from droid.utils.config_manager import ConfigManager

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Droid AI Agent")
    
    parser.add_argument(
        "--config", "-c",
        help="Path to configuration file",
        default=os.environ.get("DROID_CONFIG", "config/config.yaml")
    )
    
    parser.add_argument(
        "--task", "-t",
        help="Task to execute",
        default=None
    )
    
    parser.add_argument(
        "--params", "-p",
        help="Parameters for the task (JSON string)",
        default="{}"
    )
    
    parser.add_argument(
        "--log-level",
        help="Logging level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO"
    )
    
    return parser.parse_args()

def main():
    """Main entry point."""
    # Parse command line arguments
    args = parse_args()
    
    # Load configuration
    config_manager = ConfigManager(args.config)
    config = config_manager.get_config()
    
    # Set up logging
    logging_config = config.get("logging", {})
    logging_config["level"] = args.log_level
    setup_logging(logging_config)
    
    # Create the agent
    agent = Agent(args.config)
    
    # Execute a specific task or run the agent's main loop
    if args.task:
        import json
        params = json.loads(args.params)
        result = agent.execute_task(args.task, params)
        print(f"Task result: {result}")
    else:
        # Run the agent's main loop
        agent.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    except Exception as e:
        logging.critical(f"Unhandled exception: {str(e)}", exc_info=True)
        sys.exit(1)