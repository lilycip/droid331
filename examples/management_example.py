#!/usr/bin/env python3
"""
Example script demonstrating the use of the Management module with CrewAI.
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

def run_predefined_crew(agent, crew_type: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run a predefined crew.
    
    Args:
        agent: Agent instance
        crew_type: Type of crew to run
        inputs: Input parameters for the crew
        
    Returns:
        Results of the crew execution
    """
    # Get the management module
    management = agent.modules.get("management")
    if not management:
        raise ValueError("Management module not found")
    
    # Create the crew based on the type
    if crew_type == "social_media":
        crew_name = management.create_social_media_crew()
    elif crew_type == "content_research":
        crew_name = management.create_content_research_crew()
    else:
        raise ValueError(f"Unknown crew type: {crew_type}")
    
    # Run the crew
    return management.run_crew(crew_name, inputs)

def run_custom_crew(agent, topic: str, platform: str) -> Dict[str, Any]:
    """
    Create and run a custom crew.
    
    Args:
        agent: Agent instance
        topic: Topic to create content about
        platform: Social media platform to post to
        
    Returns:
        Results of the crew execution
    """
    # Get the management module
    management = agent.modules.get("management")
    if not management:
        raise ValueError("Management module not found")
    
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
    
    # Create the crew
    crew_name = "custom_content_crew"
    management.create_crew(
        name=crew_name,
        task_names=["research_topic", "create_content", "post_content"],
        process="sequential"
    )
    
    # Run the crew
    return management.run_crew(crew_name, {
        "topic": topic,
        "platform": platform
    })

def main():
    """Run the example."""
    parser = argparse.ArgumentParser(description="Management module example")
    parser.add_argument("--config", type=str, help="Path to config file")
    parser.add_argument("--crew-type", type=str, choices=["social_media", "content_research", "custom"],
                        default="custom", help="Type of crew to run")
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
    
    # Create a custom config with the management module enabled
    if not args.config:
        config = {
            "modules": {
                "management": {
                    "enabled": True,
                    "process": "sequential"
                }
            }
        }
        
        # Create a temporary config file
        import tempfile
        import yaml
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config, f)
            config_path = f.name
    else:
        config_path = args.config
    
    try:
        # Initialize the agent with the management module
        logger.info("Initializing agent with management module")
        agent = Agent(config_path=config_path)
        
        # Check if the management module was loaded
        if "management" not in agent.modules:
            logger.error("Management module was not loaded")
            sys.exit(1)
        
        # Run the appropriate crew
        if args.crew_type == "custom":
            logger.info(f"Running custom crew for topic '{args.topic}' on platform '{args.platform}'")
            result = run_custom_crew(agent, args.topic, args.platform)
        else:
            logger.info(f"Running predefined {args.crew_type} crew")
            result = run_predefined_crew(agent, args.crew_type, {
                "topic": args.topic,
                "platform": args.platform
            })
        
        # Print the result
        logger.info("Crew execution completed")
        print(json.dumps(result, indent=2))
        
    finally:
        # Clean up the temporary config file
        if not args.config and 'config_path' in locals():
            try:
                os.unlink(config_path)
            except:
                pass

if __name__ == "__main__":
    main()