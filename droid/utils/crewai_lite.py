"""
CrewAI Lite - A simplified version of CrewAI for team coordination.
This module provides the core functionality of CrewAI without the complex dependencies.
"""
import logging
import uuid
import json
import time
from typing import Dict, List, Any, Optional, Callable, Union
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)

class Process(str, Enum):
    """Process types for crew execution."""
    SEQUENTIAL = "sequential"
    HIERARCHICAL = "hierarchical"

class BaseTool:
    """Base class for tools that agents can use."""
    
    def __init__(self, name: str, description: str):
        """Initialize the tool."""
        self.name = name
        self.description = description
    
    def _run(self, *args, **kwargs) -> str:
        """Run the tool."""
        raise NotImplementedError("Subclasses must implement this method")
    
    def run(self, *args, **kwargs) -> str:
        """Run the tool with logging."""
        logger.info(f"Running tool: {self.name}")
        start_time = time.time()
        try:
            result = self._run(*args, **kwargs)
            logger.info(f"Tool {self.name} completed in {time.time() - start_time:.2f}s")
            return result
        except Exception as e:
            logger.error(f"Tool {self.name} failed: {str(e)}")
            raise

class Tool(BaseTool):
    """Custom tool for agents to use."""
    
    def __init__(self, name: str, description: str, func: Callable):
        """Initialize the custom tool."""
        super().__init__(name, description)
        self.func = func
    
    def _run(self, *args, **kwargs) -> str:
        """Run the tool."""
        return self.func(*args, **kwargs)

class Agent:
    """Agent class for CrewAI Lite."""
    
    def __init__(
        self,
        role: str,
        goal: str,
        backstory: str = None,
        verbose: bool = False,
        allow_delegation: bool = False,
        tools: List[BaseTool] = None,
        llm: Any = None,
        model_manager: Any = None,
        memory_system: Any = None
    ):
        """
        Initialize an agent.
        
        Args:
            role: Role of the agent
            goal: Goal of the agent
            backstory: Backstory of the agent
            verbose: Whether to enable verbose output
            allow_delegation: Whether to allow task delegation
            tools: List of tools available to the agent
            llm: Language model to use for the agent
            model_manager: Model manager to use for the agent
            memory_system: Memory system to use for the agent
        """
        self.id = str(uuid.uuid4())
        self.role = role
        self.goal = goal
        self.backstory = backstory or f"You are an AI agent with the role of {role}."
        self.verbose = verbose
        self.allow_delegation = allow_delegation
        self.tools = tools or []
        self.llm = llm
        self.model_manager = model_manager
        self.memory_system = memory_system
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
        # Agent Role: {self.role}
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
        
    def execute_task(self, task: 'Task') -> str:
        """Execute a task using the agent's model."""
        if self.verbose:
            logger.info(f"Agent {self.role} executing task: {task.description}")
            
        prompt = self.get_prompt(task.description, task.context)
        
        # First try to use the model manager if available
        if self.model_manager and hasattr(self.model_manager, 'run_model'):
            try:
                # Check if the model manager has a default LLM model
                if self.model_manager.has_model("llama-3.1"):
                    response = self.model_manager.run_model("llama-3.1", prompt)
                    
                    # Store in memory system if available
                    if self.memory_system and hasattr(self.memory_system, 'add'):
                        self.memory_system.add(f"task_result_{task.id}", response)
                    
                    self.add_memory(f"Completed task: {task.description}")
                    
                    if self.verbose:
                        logger.info(f"Agent {self.role} completed task using model manager")
                    
                    return response
            except Exception as e:
                logger.error(f"Error using model manager: {str(e)}")
                # Fall back to other methods
        
        # Fall back to using the LLM directly if available
        if self.llm:
            # Check if the LLM has a generate method
            if hasattr(self.llm, 'generate'):
                response = self.llm.generate(prompt)
            # Check if it's a dictionary with a type field (our placeholder)
            elif isinstance(self.llm, dict) and self.llm.get('type') == 'llm_placeholder':
                response = f"[Simulated response from {self.llm.get('name', 'LLM')} for task: {task.description}]"
            # Otherwise, try to use it as a callable
            elif callable(self.llm):
                response = self.llm(prompt)
            else:
                response = f"[Unable to use LLM of type {type(self.llm)}. Using simulated response for task: {task.description}]"
                
            self.add_memory(f"Completed task: {task.description}")
            
            if self.verbose:
                logger.info(f"Agent {self.role} completed task: {task.description}")
                
            return response
        else:
            return f"[Agent {self.role} has no model assigned. Using simulated response for task: {task.description}]"

class Task:
    """Task class for CrewAI Lite."""
    
    def __init__(
        self,
        description: str,
        agent: Agent,
        expected_output: str = None,
        context: List[str] = None,
        async_execution: bool = False,
        callback: Callable = None
    ):
        """
        Initialize a task.
        
        Args:
            description: Description of the task
            agent: Agent assigned to the task
            expected_output: Expected output format
            context: Additional context for the task
            async_execution: Whether to execute the task asynchronously
            callback: Callback function to call when the task is completed
        """
        self.id = str(uuid.uuid4())
        self.description = description
        self.agent = agent
        self.expected_output = expected_output
        self.context = context or []
        self.async_execution = async_execution
        self.callback = callback
        self.status = "pending"  # pending, in_progress, completed, failed
        self.result = None
        self.created_at = datetime.now().isoformat()
        self.completed_at = None
        
    def execute(self) -> str:
        """Execute the task using the assigned agent."""
        try:
            self.status = "in_progress"
            self.result = self.agent.execute_task(self)
            self.status = "completed"
            self.completed_at = datetime.now().isoformat()
            
            if self.callback:
                self.callback(self)
                
            return self.result
        except Exception as e:
            self.status = "failed"
            self.result = f"Error: {str(e)}"
            return self.result

class Crew:
    """Crew class for CrewAI Lite."""
    
    def __init__(
        self,
        agents: List[Agent],
        tasks: List[Task],
        verbose: bool = True,
        process: Process = Process.SEQUENTIAL,
        memory: bool = True
    ):
        """
        Initialize a crew.
        
        Args:
            agents: List of agents in the crew
            tasks: List of tasks assigned to the crew
            verbose: Whether to enable verbose output
            process: Process type (sequential or hierarchical)
            memory: Whether to enable memory
        """
        self.id = str(uuid.uuid4())
        self.agents = agents
        self.tasks = tasks
        self.verbose = verbose
        self.process = process
        self.memory_enabled = memory
        self.results = {}
        self.status = "pending"  # pending, in_progress, completed, failed
        self.memory = []
        
    def add_memory(self, content: str) -> None:
        """Add a memory item to the crew's memory."""
        if self.memory_enabled:
            self.memory.append({
                "content": content,
                "timestamp": datetime.now().isoformat()
            })
        
    def kickoff(self, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run the crew's tasks.
        
        Args:
            inputs: Input parameters for the tasks
            
        Returns:
            Results of the crew execution
        """
        self.status = "in_progress"
        results = {}
        
        # Add inputs to context for all tasks if provided
        if inputs:
            input_context = [f"{k}: {v}" for k, v in inputs.items()]
            for task in self.tasks:
                task.context.extend(input_context)
        
        if self.verbose:
            logger.info(f"Starting crew execution with {len(self.tasks)} tasks")
            logger.info(f"Process type: {self.process}")
        
        if self.process == Process.SEQUENTIAL:
            # Run tasks in sequence, passing results to next task
            for i, task in enumerate(self.tasks):
                # Add results from previous tasks to context
                if i > 0:
                    prev_results = [f"Result from {prev_task.agent.role}: {prev_task.result}" 
                                   for prev_task in self.tasks[:i] if prev_task.result]
                    task.context.extend(prev_results)
                
                if self.verbose:
                    logger.info(f"Executing task {i+1}/{len(self.tasks)}: {task.description}")
                    
                result = task.execute()
                results[task.agent.role] = result
                
                self.add_memory(f"Task completed by {task.agent.role}: {task.description}")
                
        elif self.process == Process.HIERARCHICAL:
            # First task is the manager that delegates to other agents
            manager_task = self.tasks[0]
            
            if self.verbose:
                logger.info(f"Executing manager task: {manager_task.description}")
                
            manager_result = manager_task.execute()
            results[manager_task.agent.role] = manager_result
            
            self.add_memory(f"Manager task completed by {manager_task.agent.role}: {manager_task.description}")
            
            # Parse manager result to get instructions for other tasks
            for task in self.tasks[1:]:
                task.context.append(f"Manager instructions: {manager_result}")
                
                if self.verbose:
                    logger.info(f"Executing task based on manager instructions: {task.description}")
                    
                result = task.execute()
                results[task.agent.role] = result
                
                self.add_memory(f"Task completed by {task.agent.role}: {task.description}")
        
        self.results = results
        self.status = "completed"
        
        if self.verbose:
            logger.info("Crew execution completed")
            
        return results