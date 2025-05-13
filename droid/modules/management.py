"""
Management Module - Provides team management capabilities using CrewAI Lite.
"""
import logging
import os
import uuid
import json
import time
from typing import Dict, List, Any, Optional, Callable, Union
from datetime import datetime

from droid.core.model_manager import ModelManager
from droid.core.memory import MemorySystem
from droid.utils.crewai_lite import Agent as CrewAgent
from droid.utils.crewai_lite import Task as CrewTask
from droid.utils.crewai_lite import Crew, Process, Tool as CrewTool

logger = logging.getLogger(__name__)

class CustomTool(CrewTool):
    """Custom tool for CrewAI agents to use."""
    
    def __init__(self, name: str, description: str, func: Callable):
        """Initialize the custom tool."""
        super().__init__(name=name, description=description, func=func)


class Management:
    """
    Management module for team coordination and task delegation using CrewAI Lite.
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
        self.crews = {}
        self.tools = {}
        
        # Default process type
        self.default_process = Process.SEQUENTIAL
        if self.config.get("process") == "hierarchical":
            self.default_process = Process.HIERARCHICAL
        
        logger.info("Management module initialized with CrewAI Lite")
    
    def register_tool(self, name: str, description: str, func: Callable) -> None:
        """
        Register a custom tool for agents to use.
        
        Args:
            name: Name of the tool
            description: Description of the tool
            func: Function to execute when the tool is used
        """
        self.tools[name] = CustomTool(name=name, description=description, func=func)
        logger.info(f"Registered tool: {name}")
    
    def create_agent(self, name: str, role: str, goal: str, backstory: str = None, 
                     verbose: bool = False, allow_delegation: bool = False,
                     tools: List[str] = None) -> str:
        """
        Create a CrewAI agent.
        
        Args:
            name: Unique identifier for the agent
            role: Role of the agent
            goal: Goal of the agent
            backstory: Backstory of the agent
            verbose: Whether to enable verbose output
            allow_delegation: Whether to allow task delegation
            tools: List of tool names to assign to the agent
            
        Returns:
            The agent ID (same as name)
        """
        # Get the LLM from model manager if available
        llm = None
        if self.model_manager.has_model("llm"):
            llm = self.model_manager.get_model("llm")
        
        # Get the tools for this agent
        agent_tools = []
        if tools:
            for tool_name in tools:
                if tool_name in self.tools:
                    agent_tools.append(self.tools[tool_name])
        
        # Create the agent
        agent = CrewAgent(
            role=role,
            goal=goal,
            backstory=backstory or f"You are an AI agent named {name} with the role of {role}.",
            verbose=verbose,
            allow_delegation=allow_delegation,
            tools=agent_tools if agent_tools else None,
            llm=llm
        )
        
        self.agents[name] = agent
        logger.info(f"Created agent: {name}")
        
        return name
    
    def create_task(self, name: str, description: str, agent_name: str, 
                   expected_output: str = None, context: List[str] = None) -> str:
        """
        Create a CrewAI task.
        
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
        
        task = CrewTask(
            description=description,
            expected_output=expected_output,
            agent=self.agents[agent_name],
            context=context
        )
        
        self.tasks[name] = task
        logger.info(f"Created task: {name} assigned to agent: {agent_name}")
        
        return name
    
    def create_crew(self, name: str, task_names: List[str], process: str = None, 
                   verbose: bool = True, memory: bool = True) -> str:
        """
        Create a CrewAI crew with tasks.
        
        Args:
            name: Unique identifier for the crew
            task_names: List of task names to assign to the crew
            process: Process type (sequential or hierarchical)
            verbose: Whether to enable verbose output
            memory: Whether to enable memory
            
        Returns:
            The crew ID (same as name)
        """
        # Validate tasks
        tasks = []
        for task_name in task_names:
            if task_name not in self.tasks:
                raise ValueError(f"Task {task_name} does not exist")
            tasks.append(self.tasks[task_name])
        
        # Determine process type
        process_type = self.default_process
        if process == "sequential":
            process_type = Process.SEQUENTIAL
        elif process == "hierarchical":
            process_type = Process.HIERARCHICAL
        
        # Get unique agents from tasks
        agents = []
        for task in tasks:
            if task.agent not in agents:
                agents.append(task.agent)
        
        # Create the crew
        crew = Crew(
            agents=agents,
            tasks=tasks,
            verbose=verbose,
            process=process_type,
            memory=memory
        )
        
        self.crews[name] = crew
        logger.info(f"Created crew: {name} with {len(tasks)} tasks")
        
        return name
    
    def run_crew(self, name: str, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run a CrewAI crew.
        
        Args:
            name: Name of the crew to run
            inputs: Input parameters for the crew
            
        Returns:
            Results of the crew execution
        """
        if name not in self.crews:
            raise ValueError(f"Crew {name} does not exist")
        
        crew = self.crews[name]
        
        # Run the crew
        logger.info(f"Running crew: {name}")
        result = crew.kickoff(inputs=inputs)
        
        # Store the result in memory
        self.memory.add(
            json.dumps({
                "crew": name,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }),
            category=f"crew_result_{name}"
        )
        
        return {"result": result}
    
    def get_agent(self, name: str) -> Optional[CrewAgent]:
        """
        Get a CrewAI agent by name.
        
        Args:
            name: Name of the agent
            
        Returns:
            The agent or None if not found
        """
        return self.agents.get(name)
    
    def get_task(self, name: str) -> Optional[CrewTask]:
        """
        Get a CrewAI task by name.
        
        Args:
            name: Name of the task
            
        Returns:
            The task or None if not found
        """
        return self.tasks.get(name)
    
    def get_crew(self, name: str) -> Optional[Crew]:
        """
        Get a CrewAI crew by name.
        
        Args:
            name: Name of the crew
            
        Returns:
            The crew or None if not found
        """
        return self.crews.get(name)
    
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
    
    def list_crews(self) -> List[str]:
        """
        List all crew names.
        
        Returns:
            List of crew names
        """
        return list(self.crews.keys())
    
    # Alias for backward compatibility
    list_teams = list_crews
    get_team = get_crew
    run_team = run_crew
    create_team = create_crew
    
    def create_social_media_crew(self) -> str:
        """
        Create a predefined social media crew with agents and tasks.
        
        Returns:
            The crew ID
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
        
        # Create the crew
        crew_name = "social_media_crew"
        self.create_crew(
            name=crew_name,
            task_names=["analyze_trends", "create_content", "optimize_engagement"],
            process="sequential"
        )
        
        return crew_name
    
    # Alias for backward compatibility
    create_social_media_team = create_social_media_crew
    
    def create_content_research_crew(self) -> str:
        """
        Create a predefined content research crew with agents and tasks.
        
        Returns:
            The crew ID
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
        
        # Create the crew
        crew_name = "content_research_crew"
        self.create_crew(
            name=crew_name,
            task_names=["research_topic", "write_content", "edit_content"],
            process="sequential"
        )
        
        return crew_name
    
    # Alias for backward compatibility
    create_content_research_team = create_content_research_crew