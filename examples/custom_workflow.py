#!/usr/bin/env python3
"""
Example of creating and using a custom workflow with the Droid agent.
"""
import os
import sys
import json
import argparse
import logging
import time
from droid.core.agent import Agent
from droid.utils.logger import setup_logging

class WorkflowStep:
    """Base class for workflow steps."""
    
    def __init__(self, name, config=None):
        """Initialize the workflow step."""
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"workflow.step.{name}")
    
    def execute(self, context):
        """Execute the workflow step."""
        raise NotImplementedError("Subclasses must implement execute()")
    
    def validate(self, context):
        """Validate the workflow step."""
        return True, None

class InputStep(WorkflowStep):
    """Workflow step for getting input."""
    
    def execute(self, context):
        """Execute the workflow step."""
        self.logger.info(f"Executing input step: {self.name}")
        
        prompt = self.config.get("prompt", "Enter input: ")
        default = self.config.get("default")
        required = self.config.get("required", False)
        
        if default:
            prompt = f"{prompt} [{default}]: "
        
        while True:
            value = input(prompt)
            
            if not value and default:
                value = default
            
            if not value and required:
                print("Input is required.")
                continue
            
            break
        
        # Store the input in the context
        context[self.config.get("output_key", self.name)] = value
        
        return context

class GenerateContentStep(WorkflowStep):
    """Workflow step for generating content."""
    
    def execute(self, context):
        """Execute the workflow step."""
        self.logger.info(f"Executing generate content step: {self.name}")
        
        agent = context.get("agent")
        if not agent:
            self.logger.error("Agent not found in context")
            return context
        
        content_type = self.config.get("content_type", "text")
        prompt_template = self.config.get("prompt_template")
        
        if not prompt_template:
            self.logger.error("Prompt template not found in config")
            return context
        
        # Replace variables in the prompt template
        prompt = prompt_template
        for key, value in context.items():
            if isinstance(value, (str, int, float, bool)):
                prompt = prompt.replace(f"{{{key}}}", str(value))
        
        self.logger.info(f"Generating {content_type} content with prompt: {prompt}")
        
        # Generate the content
        if content_type == "text":
            # In a real implementation, we would use the agent to generate text
            # For this example, we'll just create a mock result
            result = f"Generated text for prompt: {prompt}"
        elif content_type == "image":
            # In a real implementation, we would use the agent to generate an image
            # For this example, we'll just create a mock result
            result = f"Generated image for prompt: {prompt}"
        else:
            self.logger.error(f"Unsupported content type: {content_type}")
            return context
        
        # Store the result in the context
        context[self.config.get("output_key", self.name)] = result
        
        return context
    
    def validate(self, context):
        """Validate the workflow step."""
        if not self.config.get("prompt_template"):
            return False, "Prompt template is required"
        
        return True, None

class PostToSocialMediaStep(WorkflowStep):
    """Workflow step for posting to social media."""
    
    def execute(self, context):
        """Execute the workflow step."""
        self.logger.info(f"Executing post to social media step: {self.name}")
        
        agent = context.get("agent")
        if not agent:
            self.logger.error("Agent not found in context")
            return context
        
        platform = self.config.get("platform")
        content_key = self.config.get("content_key")
        
        if not platform:
            self.logger.error("Platform not found in config")
            return context
        
        if not content_key or content_key not in context:
            self.logger.error(f"Content key {content_key} not found in context")
            return context
        
        content = context[content_key]
        
        self.logger.info(f"Posting to {platform}: {content}")
        
        # In a real implementation, we would use the agent to post to social media
        # For this example, we'll just log the post
        
        # Store the result in the context
        context[self.config.get("output_key", f"{platform}_post_id")] = f"post_{int(time.time())}"
        
        return context
    
    def validate(self, context):
        """Validate the workflow step."""
        if not self.config.get("platform"):
            return False, "Platform is required"
        
        if not self.config.get("content_key"):
            return False, "Content key is required"
        
        return True, None

class ConditionalStep(WorkflowStep):
    """Workflow step for conditional execution."""
    
    def execute(self, context):
        """Execute the workflow step."""
        self.logger.info(f"Executing conditional step: {self.name}")
        
        condition = self.config.get("condition")
        if not condition:
            self.logger.error("Condition not found in config")
            return context
        
        # Evaluate the condition
        result = False
        
        if condition.get("type") == "equals":
            left = context.get(condition.get("left"))
            right = condition.get("right")
            result = left == right
        elif condition.get("type") == "contains":
            left = context.get(condition.get("left"))
            right = condition.get("right")
            result = right in left if isinstance(left, str) else False
        elif condition.get("type") == "exists":
            key = condition.get("key")
            result = key in context
        
        self.logger.info(f"Condition result: {result}")
        
        # Execute the appropriate branch
        if result:
            steps = self.config.get("then_steps", [])
        else:
            steps = self.config.get("else_steps", [])
        
        # Create and execute the steps
        for step_config in steps:
            step_type = step_config.get("type")
            step_name = step_config.get("name")
            
            if step_type == "input":
                step = InputStep(step_name, step_config)
            elif step_type == "generate_content":
                step = GenerateContentStep(step_name, step_config)
            elif step_type == "post_to_social_media":
                step = PostToSocialMediaStep(step_name, step_config)
            elif step_type == "conditional":
                step = ConditionalStep(step_name, step_config)
            else:
                self.logger.error(f"Unsupported step type: {step_type}")
                continue
            
            # Validate the step
            valid, error = step.validate(context)
            if not valid:
                self.logger.error(f"Step validation failed: {error}")
                continue
            
            # Execute the step
            context = step.execute(context)
        
        return context
    
    def validate(self, context):
        """Validate the workflow step."""
        if not self.config.get("condition"):
            return False, "Condition is required"
        
        return True, None

class Workflow:
    """A workflow for the Droid agent."""
    
    def __init__(self, name, config=None):
        """Initialize the workflow."""
        self.name = name
        self.config = config or {}
        self.steps = []
        self.logger = logging.getLogger(f"workflow.{name}")
        
        # Create the steps
        for step_config in self.config.get("steps", []):
            step_type = step_config.get("type")
            step_name = step_config.get("name")
            
            if step_type == "input":
                step = InputStep(step_name, step_config)
            elif step_type == "generate_content":
                step = GenerateContentStep(step_name, step_config)
            elif step_type == "post_to_social_media":
                step = PostToSocialMediaStep(step_name, step_config)
            elif step_type == "conditional":
                step = ConditionalStep(step_name, step_config)
            else:
                self.logger.error(f"Unsupported step type: {step_type}")
                continue
            
            self.steps.append(step)
    
    def execute(self, context=None):
        """Execute the workflow."""
        self.logger.info(f"Executing workflow: {self.name}")
        
        context = context or {}
        
        # Add the workflow name to the context
        context["workflow_name"] = self.name
        
        # Execute each step
        for step in self.steps:
            # Validate the step
            valid, error = step.validate(context)
            if not valid:
                self.logger.error(f"Step validation failed: {error}")
                continue
            
            # Execute the step
            context = step.execute(context)
        
        self.logger.info(f"Workflow completed: {self.name}")
        
        return context

class WorkflowManager:
    """Manager for loading and executing workflows."""
    
    def __init__(self, agent):
        """Initialize the workflow manager."""
        self.agent = agent
        self.workflows = {}
        self.logger = logging.getLogger("workflow_manager")
    
    def load_workflow(self, name, config):
        """Load a workflow."""
        self.logger.info(f"Loading workflow: {name}")
        
        workflow = Workflow(name, config)
        self.workflows[name] = workflow
        
        return workflow
    
    def load_workflow_from_file(self, file_path):
        """Load a workflow from a file."""
        self.logger.info(f"Loading workflow from file: {file_path}")
        
        if not os.path.exists(file_path):
            self.logger.error(f"Workflow file not found: {file_path}")
            return None
        
        try:
            with open(file_path, "r") as f:
                config = json.load(f)
            
            name = config.get("name", os.path.basename(file_path))
            return self.load_workflow(name, config)
        except Exception as e:
            self.logger.error(f"Error loading workflow from file: {str(e)}")
            return None
    
    def get_workflow(self, name):
        """Get a workflow by name."""
        return self.workflows.get(name)
    
    def execute_workflow(self, name, context=None):
        """Execute a workflow by name."""
        workflow = self.get_workflow(name)
        
        if not workflow:
            self.logger.error(f"Workflow not found: {name}")
            return None
        
        context = context or {}
        context["agent"] = self.agent
        
        return workflow.execute(context)

def create_example_workflow():
    """Create an example workflow file."""
    workflow_dir = "workflows"
    
    if not os.path.exists(workflow_dir):
        os.makedirs(workflow_dir)
    
    # Create the example workflow
    workflow = {
        "name": "social_media_post",
        "description": "Generate and post content to social media",
        "steps": [
            {
                "type": "input",
                "name": "topic",
                "prompt": "Enter a topic for the post",
                "required": True,
                "output_key": "topic"
            },
            {
                "type": "input",
                "name": "platform",
                "prompt": "Enter the social media platform",
                "default": "twitter",
                "output_key": "platform"
            },
            {
                "type": "conditional",
                "name": "platform_check",
                "condition": {
                    "type": "equals",
                    "left": "platform",
                    "right": "twitter"
                },
                "then_steps": [
                    {
                        "type": "generate_content",
                        "name": "generate_tweet",
                        "content_type": "text",
                        "prompt_template": "Write a tweet about {topic}",
                        "output_key": "tweet_content"
                    },
                    {
                        "type": "post_to_social_media",
                        "name": "post_tweet",
                        "platform": "twitter",
                        "content_key": "tweet_content",
                        "output_key": "tweet_id"
                    }
                ],
                "else_steps": [
                    {
                        "type": "generate_content",
                        "name": "generate_image",
                        "content_type": "image",
                        "prompt_template": "Create an image about {topic}",
                        "output_key": "image_content"
                    },
                    {
                        "type": "generate_content",
                        "name": "generate_caption",
                        "content_type": "text",
                        "prompt_template": "Write a caption for an image about {topic}",
                        "output_key": "caption_content"
                    },
                    {
                        "type": "post_to_social_media",
                        "name": "post_image",
                        "platform": "instagram",
                        "content_key": "image_content",
                        "caption_key": "caption_content",
                        "output_key": "instagram_post_id"
                    }
                ]
            }
        ]
    }
    
    # Write the workflow to a file
    with open(os.path.join(workflow_dir, "social_media_post.json"), "w") as f:
        json.dump(workflow, f, indent=2)
    
    return os.path.join(workflow_dir, "social_media_post.json")

def main():
    """Run the agent with a custom workflow."""
    parser = argparse.ArgumentParser(description="Run the Droid agent with a custom workflow")
    parser.add_argument("--workflow", type=str, help="Path to workflow file")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = "DEBUG" if args.debug else "INFO"
    setup_logging({"level": log_level})
    logger = logging.getLogger(__name__)
    
    # Create the agent
    agent = Agent()
    
    # Create the workflow manager
    workflow_manager = WorkflowManager(agent)
    
    # Create an example workflow if no workflow file is provided
    workflow_file = args.workflow
    if not workflow_file:
        workflow_file = create_example_workflow()
        logger.info(f"Created example workflow: {workflow_file}")
    
    # Load the workflow
    workflow = workflow_manager.load_workflow_from_file(workflow_file)
    
    if not workflow:
        logger.error(f"Failed to load workflow from file: {workflow_file}")
        sys.exit(1)
    
    logger.info(f"Loaded workflow: {workflow.name}")
    
    # Execute the workflow
    result = workflow_manager.execute_workflow(workflow.name)
    
    logger.info(f"Workflow result: {result}")

if __name__ == "__main__":
    main()