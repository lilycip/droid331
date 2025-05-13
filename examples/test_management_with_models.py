#!/usr/bin/env python3
"""
Example script demonstrating the use of the Management module with AI models.
"""
import os
import sys
import argparse
import logging
import json
from typing import Dict, Any

# Add the parent directory to the path so we can import the droid package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from droid.core.agent import Agent
from droid.core.model_manager import ModelManager
from droid.core.memory import MemorySystem
from droid.modules.management import Management, CustomTool
from droid.utils.config_manager import ConfigManager
from droid.utils.logger import setup_logging

def generate_text(prompt: str) -> str:
    """
    Generate text using the LLM model.
    
    Args:
        prompt: Text generation prompt
        
    Returns:
        Generated text
    """
    # This function will be replaced with the actual model call
    return f"Generated text for prompt: {prompt}"

def generate_image(prompt: str) -> str:
    """
    Generate an image using the diffusion model.
    
    Args:
        prompt: Image generation prompt
        
    Returns:
        Path to the generated image
    """
    # This function will be replaced with the actual model call
    return f"Generated image at '/tmp/image_{prompt.replace(' ', '_')}.png'"

def setup_management_module() -> Management:
    """Set up the management module with configuration."""
    # Load configuration
    config_manager = ConfigManager()
    config = config_manager.get_config()
    
    # Initialize model manager and memory system
    model_manager = ModelManager(config.get("models", {}))
    memory = MemorySystem(config.get("memory", {}))
    
    # Initialize management module
    management_config = config.get("modules", {}).get("management", {})
    management = Management(management_config, model_manager, memory)
    
    # Create wrapper functions that use the model manager
    def text_generation_tool(prompt: str) -> str:
        """Generate text using the LLM model."""
        return model_manager.run_model("llama-3.1", prompt)
    
    def image_generation_tool(prompt: str) -> Dict[str, Any]:
        """Generate an image using the diffusion model."""
        return model_manager.run_model("stable-diffusion-2.1", prompt)
    
    # Register tools
    management.register_tool(
        name="generate_text",
        description="Generate text using the LLM model",
        func=text_generation_tool
    )
    
    management.register_tool(
        name="generate_image",
        description="Generate an image using the diffusion model",
        func=image_generation_tool
    )
    
    return management

def run_content_creation_team(topic: str) -> Dict[str, Any]:
    """
    Create and run a content creation team.
    
    Args:
        topic: Topic to create content about
        
    Returns:
        Results of the team execution
    """
    # Set up the management module
    management = setup_management_module()
    
    # Create agents
    management.create_agent(
        name="writer",
        role="Content Writer",
        goal="Create engaging and informative content",
        tools=["generate_text"]
    )
    
    management.create_agent(
        name="illustrator",
        role="Illustrator",
        goal="Create visually appealing images to accompany the content",
        tools=["generate_image"]
    )
    
    management.create_agent(
        name="editor",
        role="Content Editor",
        goal="Ensure content is accurate, engaging, and well-structured",
        tools=["generate_text"]
    )
    
    # Create tasks
    management.create_task(
        name="write_article",
        description=f"Write an informative article about {topic}",
        agent_name="writer",
        expected_output="A well-written article about the topic"
    )
    
    management.create_task(
        name="create_illustration",
        description=f"Create an illustration for an article about {topic}",
        agent_name="illustrator",
        expected_output="An image that complements the article"
    )
    
    management.create_task(
        name="edit_article",
        description=f"Edit and polish the article about {topic}",
        agent_name="editor",
        expected_output="A polished, publication-ready article"
    )
    
    # Create the team
    team_name = "content_creation_team"
    management.create_team(
        name=team_name,
        task_names=["write_article", "create_illustration", "edit_article"],
        process="sequential"
    )
    
    # Run the team
    return management.run_team(team_name, {
        "topic": topic
    })

def main():
    """Run the example."""
    parser = argparse.ArgumentParser(description="Management module with models example")
    parser.add_argument("--topic", type=str, default="artificial intelligence",
                        help="Topic for content creation")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = "DEBUG" if args.debug else "INFO"
    setup_logging({"level": log_level})
    logger = logging.getLogger(__name__)
    
    try:
        # Run the content creation team
        logger.info(f"Running content creation team for topic '{args.topic}'")
        result = run_content_creation_team(args.topic)
        
        # Print the result
        logger.info("Team execution completed")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        logger.error(f"Error running team: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()