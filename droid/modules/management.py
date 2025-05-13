"""
Management Module - Provides team management capabilities for coordinating multiple agents.
"""
import logging
import os
import uuid
import json
import time
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime

from droid.core.model_manager import ModelManager
from droid.core.memory import MemorySystem

logger = logging.getLogger(__name__)

class Tool:
    """Custom tool for agents to use."""
    
    def __init__(self, name: str, description: str, func: Callable):
        """Initialize the custom tool."""
        self.name = name
        self.description = description
        self.func = func
    
    def run(self, *args, **kwargs) -> str:
        """Run the tool."""
        return self.func(*args, **kwargs)

class Agent:
    """Agent class for the Management module."""
    
    def __init__(self, name: str, role: str, goal: str, backstory: str = None, 
                 tools: List[Tool] = None, model=None):
        """
        Initialize an agent.
        
        Args:
            name: Unique identifier for the agent
            role: Role of the agent
            goal: Goal of the agent
            backstory: Backstory of the agent
            tools: List of tools available to the agent
            model: Language model to use for the agent
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory or f"You are an AI agent named {name} with the role of {role}."
        self.tools = tools or []
        self.model = model
        self.memory = []
        
    def add_memory(self, content: str) -> None:
        """Add a memory item to the agent's memory."""
        self.memory.append({
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
    def get_prompt(self, task_description: str, context: List[str] = None) -> str:
        """Generate a prompt for the agent based on its role, goal, and the task."""
        memories = "\n".join([f"- {m['content']}" for m in self.memory[-5:]])
        context_str = "\n".join(context) if context else ""
        
        prompt = f"""
        # Agent: {self.name}
        ## Role: {self.role}
        ## Goal: {self.goal}
        ## Backstory: {self.backstory}
        
        ## Task Description:
        {task_description}
        
        ## Context:
        {context_str}
        
        ## Recent Memories:
        {memories}
        
        ## Available Tools:
        """
        
        for tool in self.tools:
            prompt += f"- {tool.name}: {tool.description}\n"
            
        prompt += "\nPlease complete the task based on your role and goal. Be thorough and creative."
        
        return prompt
        
    def execute_task(self, task_description: str, context: List[str] = None) -> str:
        """Execute a task using the agent's model."""
        prompt = self.get_prompt(task_description, context)
        
        if self.model:
            response = self.model.generate(prompt)
            self.add_memory(f"Completed task: {task_description}")
            return response
        else:
            return f"[Agent {self.name} has no model assigned. Cannot execute task.]"


class Task:
    """Task class for the Management module."""
    
    def __init__(self, name: str, description: str, agent: Agent, 
                 expected_output: str = None, context: List[str] = None):
        """
        Initialize a task.
        
        Args:
            name: Unique identifier for the task
            description: Description of the task
            agent: Agent assigned to the task
            expected_output: Expected output format
            context: Additional context for the task
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.agent = agent
        self.expected_output = expected_output
        self.context = context or []
        self.status = "pending"  # pending, in_progress, completed, failed
        self.result = None
        self.created_at = datetime.now().isoformat()
        self.completed_at = None
        
    def execute(self) -> str:
        """Execute the task using the assigned agent."""
        try:
            self.status = "in_progress"
            self.result = self.agent.execute_task(self.description, self.context)
            self.status = "completed"
            self.completed_at = datetime.now().isoformat()
            return self.result
        except Exception as e:
            self.status = "failed"
            self.result = f"Error: {str(e)}"
            return self.result


class Team:
    """Team class for the Management module (equivalent to Crew in CrewAI)."""
    
    def __init__(self, name: str, agents: List[Agent], tasks: List[Task], 
                 process_type: str = "sequential"):
        """
        Initialize a team.
        
        Args:
            name: Unique identifier for the team
            agents: List of agents in the team
            tasks: List of tasks assigned to the team
            process_type: Process type (sequential or hierarchical)
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.agents = agents
        self.tasks = tasks
        self.process_type = process_type
        self.results = {}
        self.status = "pending"  # pending, in_progress, completed, failed
        
    def run(self, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run the team's tasks.
        
        Args:
            inputs: Input parameters for the tasks
            
        Returns:
            Results of the team execution
        """
        self.status = "in_progress"
        results = {}
        
        # Add inputs to context for all tasks if provided
        if inputs:
            input_context = [f"{k}: {v}" for k, v in inputs.items()]
            for task in self.tasks:
                task.context.extend(input_context)
        
        if self.process_type == "sequential":
            # Run tasks in sequence, passing results to next task
            for i, task in enumerate(self.tasks):
                # Add results from previous tasks to context
                if i > 0:
                    prev_results = [f"Result from {prev_task.name}: {prev_task.result}" 
                                   for prev_task in self.tasks[:i] if prev_task.result]
                    task.context.extend(prev_results)
                
                result = task.execute()
                results[task.name] = result
                
        elif self.process_type == "hierarchical":
            # First task is the manager that delegates to other agents
            manager_task = self.tasks[0]
            manager_result = manager_task.execute()
            results[manager_task.name] = manager_result
            
            # Parse manager result to get instructions for other tasks
            # This is a simplified implementation
            for task in self.tasks[1:]:
                task.context.append(f"Manager instructions: {manager_result}")
                result = task.execute()
                results[task.name] = result
                
        else:
            # Default to parallel execution (simplified)
            for task in self.tasks:
                result = task.execute()
                results[task.name] = result
        
        self.results = results
        self.status = "completed"
        return results


class Management:
    """
    Management module for team coordination and task delegation.
    """
    
    def __init__(self, config: Dict[str, Any], model_manager: ModelManager, memory: MemorySystem):
        """
        Initialize the Management module.
        
        Args:
            config: Configuration for the module
            model_manager: Model manager instance
            memory: Memory system instance
        """
        self.config = config
        self.model_manager = model_manager
        self.memory = memory
        self.agents = {}
        self.tasks = {}
        self.teams = {}
        self.tools = {}
        
        # Default process type
        self.default_process = "sequential"
        if self.config.get("process") == "hierarchical":
            self.default_process = "hierarchical"
        
        logger.info("Management module initialized")
    
    def register_tool(self, name: str, description: str, func: Callable) -> None:
        """
        Register a custom tool for agents to use.
        
        Args:
            name: Name of the tool
            description: Description of the tool
            func: Function to execute when the tool is used
        """
        self.tools[name] = Tool(name=name, description=description, func=func)
        logger.info(f"Registered tool: {name}")
    
    def create_agent(self, name: str, role: str, goal: str, backstory: str = None, 
                     tools: List[str] = None) -> str:
        """
        Create an agent.
        
        Args:
            name: Unique identifier for the agent
            role: Role of the agent
            goal: Goal of the agent
            backstory: Backstory of the agent
            tools: List of tool names to assign to the agent
            
        Returns:
            The agent ID (same as name)
        """
        # Get the LLM from model manager if available
        model = None
        if self.model_manager.has_model("llm"):
            model = self.model_manager.get_model("llm")
        
        # Get the tools for this agent
        agent_tools = []
        if tools:
            for tool_name in tools:
                if tool_name in self.tools:
                    agent_tools.append(self.tools[tool_name])
        
        # Create the agent
        agent = Agent(
            name=name,
            role=role,
            goal=goal,
            backstory=backstory,
            tools=agent_tools,
            model=model
        )
        
        self.agents[name] = agent
        logger.info(f"Created agent: {name}")
        
        return name
    
    def create_task(self, name: str, description: str, agent_name: str, 
                   expected_output: str = None, context: List[str] = None) -> str:
        """
        Create a task.
        
        Args:
            name: Unique identifier for the task
            description: Description of the task
            agent_name: Name of the agent to assign the task to
            expected_output: Expected output format
            context: Additional context for the task
            
        Returns:
            The task ID (same as name)
        """
        if agent_name not in self.agents:
            raise ValueError(f"Agent {agent_name} does not exist")
        
        task = Task(
            name=name,
            description=description,
            agent=self.agents[agent_name],
            expected_output=expected_output,
            context=context
        )
        
        self.tasks[name] = task
        logger.info(f"Created task: {name} assigned to agent: {agent_name}")
        
        return name
    
    def create_team(self, name: str, task_names: List[str], process: str = None) -> str:
        """
        Create a team with tasks.
        
        Args:
            name: Unique identifier for the team
            task_names: List of task names to assign to the team
            process: Process type (sequential or hierarchical)
            
        Returns:
            The team ID (same as name)
        """
        # Validate tasks
        tasks = []
        for task_name in task_names:
            if task_name not in self.tasks:
                raise ValueError(f"Task {task_name} does not exist")
            tasks.append(self.tasks[task_name])
        
        # Determine process type
        process_type = self.default_process
        if process:
            process_type = process
        
        # Get unique agents from tasks
        agents = []
        for task in tasks:
            if task.agent not in agents:
                agents.append(task.agent)
        
        # Create the team
        team = Team(
            name=name,
            agents=agents,
            tasks=tasks,
            process_type=process_type
        )
        
        self.teams[name] = team
        logger.info(f"Created team: {name} with {len(tasks)} tasks")
        
        return name
    
    def run_team(self, name: str, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run a team.
        
        Args:
            name: Name of the team to run
            inputs: Input parameters for the team
            
        Returns:
            Results of the team execution
        """
        if name not in self.teams:
            raise ValueError(f"Team {name} does not exist")
        
        team = self.teams[name]
        
        # Run the team
        logger.info(f"Running team: {name}")
        results = team.run(inputs=inputs)
        
        # Store the result in memory
        self.memory.add(f"team_result_{name}", {
            "team": name,
            "results": results,
            "timestamp": datetime.now().isoformat()
        })
        
        return {"results": results}
    
    def get_agent(self, name: str) -> Optional[Agent]:
        """
        Get an agent by name.
        
        Args:
            name: Name of the agent
            
        Returns:
            The agent or None if not found
        """
        return self.agents.get(name)
    
    def get_task(self, name: str) -> Optional[Task]:
        """
        Get a task by name.
        
        Args:
            name: Name of the task
            
        Returns:
            The task or None if not found
        """
        return self.tasks.get(name)
    
    def get_team(self, name: str) -> Optional[Team]:
        """
        Get a team by name.
        
        Args:
            name: Name of the team
            
        Returns:
            The team or None if not found
        """
        return self.teams.get(name)
    
    def list_agents(self) -> List[str]:
        """
        List all agent names.
        
        Returns:
            List of agent names
        """
        return list(self.agents.keys())
    
    def list_tasks(self) -> List[str]:
        """
        List all task names.
        
        Returns:
            List of task names
        """
        return list(self.tasks.keys())
    
    def list_teams(self) -> List[str]:
        """
        List all team names.
        
        Returns:
            List of team names
        """
        return list(self.teams.keys())
    
    def create_social_media_team(self) -> str:
        """
        Create a predefined social media team with agents and tasks.
        
        Returns:
            The team ID
        """
        # Create agents
        content_creator = self.create_agent(
            name="content_creator",
            role="Content Creator",
            goal="Create engaging social media content",
            backstory="You are a creative content creator who specializes in creating viral social media posts."
        )
        
        trend_analyst = self.create_agent(
            name="trend_analyst",
            role="Trend Analyst",
            goal="Identify trending topics and hashtags",
            backstory="You are an expert at spotting trends before they go viral."
        )
        
        engagement_manager = self.create_agent(
            name="engagement_manager",
            role="Engagement Manager",
            goal="Maximize engagement on social media posts",
            backstory="You know exactly how to get people to like, comment, and share content."
        )
        
        # Create tasks
        analyze_trends = self.create_task(
            name="analyze_trends",
            description="Identify the top 3 trending topics in the specified niche",
            agent_name="trend_analyst",
            expected_output="A list of trending topics with hashtags and brief explanations"
        )
        
        create_content = self.create_task(
            name="create_content",
            description="Create social media content based on the trending topics",
            agent_name="content_creator",
            expected_output="Social media post text, image description, and hashtags"
        )
        
        optimize_engagement = self.create_task(
            name="optimize_engagement",
            description="Optimize the content for maximum engagement",
            agent_name="engagement_manager",
            expected_output="Optimized social media post with posting schedule recommendations"
        )
        
        # Create the team
        team_name = "social_media_team"
        self.create_team(
            name=team_name,
            task_names=["analyze_trends", "create_content", "optimize_engagement"],
            process="sequential"
        )
        
        return team_name
    
    def create_content_research_team(self) -> str:
        """
        Create a predefined content research team with agents and tasks.
        
        Returns:
            The team ID
        """
        # Create agents
        researcher = self.create_agent(
            name="researcher",
            role="Research Specialist",
            goal="Find accurate and relevant information",
            backstory="You are a meticulous researcher who leaves no stone unturned."
        )
        
        writer = self.create_agent(
            name="writer",
            role="Content Writer",
            goal="Create informative and engaging content",
            backstory="You can explain complex topics in an accessible and engaging way."
        )
        
        editor = self.create_agent(
            name="editor",
            role="Content Editor",
            goal="Ensure content is accurate, engaging, and well-structured",
            backstory="You have a keen eye for detail and know how to make content shine."
        )
        
        # Create tasks
        research_topic = self.create_task(
            name="research_topic",
            description="Research the specified topic thoroughly",
            agent_name="researcher",
            expected_output="Comprehensive research notes with sources"
        )
        
        write_content = self.create_task(
            name="write_content",
            description="Write a comprehensive article based on the research",
            agent_name="writer",
            expected_output="Draft article with headings, paragraphs, and citations"
        )
        
        edit_content = self.create_task(
            name="edit_content",
            description="Edit and polish the article",
            agent_name="editor",
            expected_output="Final polished article ready for publication"
        )
        
        # Create the team
        team_name = "content_research_team"
        self.create_team(
            name=team_name,
            task_names=["research_topic", "write_content", "edit_content"],
            process="sequential"
        )
        
        return team_name