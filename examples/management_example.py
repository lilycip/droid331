#!/usr/bin/env python3
"""
Example script demonstrating the use of the Management module for team coordination.
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
from droid.modules.management import Management, Tool
from droid.utils.config_manager import ConfigManager
from droid.utils.logger import setup_logging

def search_web(query: str) -> str:
    """
    Mock function to search the web.
    
    Args:
        query: Search query
        
    Returns:
        Search results
    """
    return f"Search results for '{query}': Found information about {query}."

def generate_image(prompt: str) -> str:
    """
    Mock function to generate an image.
    
    Args:
        prompt: Image generation prompt
        
    Returns:
        Path to the generated image
    """
    return f"Generated image at '/tmp/image_{prompt.replace(' ', '_')}.png'"

def post_to_social_media(platform: str, content: str, image_path: str = None) -> str:
    """
    Mock function to post to social media.
    
    Args:
        platform: Social media platform
        content: Post content
        image_path: Path to image to include in the post
        
    Returns:
        Post ID
    """
    return f"Posted to {platform} with ID: post_12345"

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
    
    # Register tools
    management.register_tool(
        name="search_web",
        description="Search the web for information",
        func=search_web
    )
    
    management.register_tool(
        name="generate_image",
        description="Generate an image based on a prompt",
        func=generate_image
    )
    
    management.register_tool(
        name="post_to_social_media",
        description="Post content to social media",
        func=post_to_social_media
    )
    
    return management

def run_predefined_team(team_type: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run a predefined team.
    
    Args:
        team_type: Type of team to run
        inputs: Input parameters for the team
        
    Returns:
        Results of the team execution
    """
    # Set up the management module
    management = setup_management_module()
    
    # Create the team based on the type
    if team_type == "social_media":
        team_name = management.create_social_media_team()
    elif team_type == "content_research":
        team_name = management.create_content_research_team()
    else:
        raise ValueError(f"Unknown team type: {team_type}")
    
    # Run the team
    return management.run_team(team_name, inputs)

def run_custom_team(topic: str, platform: str) -> Dict[str, Any]:
    """
    Create and run a custom team.
    
    Args:
        topic: Topic to create content about
        platform: Social media platform to post to
        
    Returns:
        Results of the team execution
    """
    # Set up the management module
    management = setup_management_module()
    
    # Create agents
    management.create_agent(
        name="researcher",
        role="Research Specialist",
        goal="Find accurate and relevant information about the topic",
        tools=["search_web"]
    )
    
    management.create_agent(
        name="content_creator",
        role="Content Creator",
        goal="Create engaging content based on research",
        tools=["generate_image"]
    )
    
    management.create_agent(
        name="social_media_manager",
        role="Social Media Manager",
        goal="Post content to social media and maximize engagement",
        tools=["post_to_social_media"]
    )
    
    # Create tasks
    management.create_task(
        name="research_topic",
        description=f"Research the topic: {topic}",
        agent_name="researcher",
        expected_output="Comprehensive research notes about the topic"
    )
    
    management.create_task(
        name="create_content",
        description=f"Create engaging content about {topic} for {platform}",
        agent_name="content_creator",
        expected_output="Social media post text and image"
    )
    
    management.create_task(
        name="post_content",
        description=f"Post the content to {platform} and optimize for engagement",
        agent_name="social_media_manager",
        expected_output="Post ID and engagement optimization tips"
    )
    
    # Create the team
    team_name = "custom_content_team"
    management.create_team(
        name=team_name,
        task_names=["research_topic", "create_content", "post_content"],
        process="sequential"
    )
    
    # Run the team
    return management.run_team(team_name, {
        "topic": topic,
        "platform": platform
    })

def main():
    """Run the example."""
    parser = argparse.ArgumentParser(description="Management module example")
    parser.add_argument("--team-type", type=str, choices=["social_media", "content_research", "custom"],
                        default="custom", help="Type of team to run")
    parser.add_argument("--topic", type=str, default="artificial intelligence",
                        help="Topic for content creation")
    parser.add_argument("--platform", type=str, default="twitter",
                        help="Social media platform")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = "DEBUG" if args.debug else "INFO"
    setup_logging({"level": log_level})
    logger = logging.getLogger(__name__)
    
    try:
        # Run the appropriate team
        if args.team_type == "custom":
            logger.info(f"Running custom team for topic '{args.topic}' on platform '{args.platform}'")
            result = run_custom_team(args.topic, args.platform)
        else:
            logger.info(f"Running predefined {args.team_type} team")
            result = run_predefined_team(args.team_type, {
                "topic": args.topic,
                "platform": args.platform
            })
        
        # Print the result
        logger.info("Team execution completed")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        logger.error(f"Error running team: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()