"""
Task Scheduler - Manages and prioritizes different tasks.
"""
import logging
import time
from typing import Dict, List, Any, Callable, Optional
from queue import PriorityQueue
from threading import Thread, Event
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass(order=True)
class Task:
    """Task class for scheduling and execution."""
    priority: int
    name: str = field(compare=False)
    params: Dict[str, Any] = field(default_factory=dict, compare=False)
    scheduled_time: float = field(default_factory=time.time, compare=False)
    callback: Optional[Callable] = field(default=None, compare=False)
    
    def __str__(self):
        return f"Task({self.name}, priority={self.priority}, scheduled={datetime.fromtimestamp(self.scheduled_time)})"


class TaskScheduler:
    """
    Manages task scheduling, prioritization, and execution.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the TaskScheduler with configuration.
        
        Args:
            config: Configuration dictionary for task scheduling
        """
        self.config = config
        self.task_queue = PriorityQueue()
        self.running = False
        self.stop_event = Event()
        self.worker_thread = None
        
        # Task definitions with their handlers
        self.task_definitions = {}
        
        # Register built-in tasks
        self._register_builtin_tasks()
        
        logger.info("TaskScheduler initialized")
    
    def _register_builtin_tasks(self):
        """Register built-in task types."""
        self.register_task("post_content", self._handle_post_content)
        self.register_task("interact_with_influencer", self._handle_interact_with_influencer)
        self.register_task("reply_to_comment", self._handle_reply_to_comment)
        self.register_task("generate_content", self._handle_generate_content)
    
    def register_task(self, task_name: str, handler: Callable):
        """
        Register a new task type with its handler.
        
        Args:
            task_name: Name of the task
            handler: Function to handle the task
        """
        self.task_definitions[task_name] = handler
        logger.info(f"Registered task handler for: {task_name}")
    
    def schedule_task(self, task_name: str, params: Dict[str, Any] = None, 
                     modules: Dict[str, Any] = None, model_manager: Any = None, 
                     memory: Any = None, priority: int = 5, 
                     callback: Callable = None) -> Any:
        """
        Schedule a task for execution.
        
        Args:
            task_name: Name of the task to execute
            params: Parameters for the task
            modules: Available modules
            model_manager: Model manager instance
            memory: Memory system instance
            priority: Task priority (lower is higher priority)
            callback: Optional callback function
            
        Returns:
            Result if executed immediately, or None if queued
        """
        if task_name not in self.task_definitions:
            logger.error(f"Unknown task: {task_name}")
            return None
            
        params = params or {}
        
        # If the scheduler is not running, execute immediately
        if not self.running:
            logger.info(f"Executing task immediately: {task_name}")
            result = self.task_definitions[task_name](params, modules, model_manager, memory)
            if callback:
                callback(result)
            return result
            
        # Otherwise, queue the task
        task = Task(
            priority=priority,
            name=task_name,
            params=params,
            scheduled_time=time.time(),
            callback=callback
        )
        
        self.task_queue.put(task)
        logger.info(f"Scheduled task: {task}")
        return None
    
    def run(self, modules: Dict[str, Any], model_manager: Any, memory: Any):
        """
        Start the task scheduler's main loop.
        
        Args:
            modules: Available modules
            model_manager: Model manager instance
            memory: Memory system instance
        """
        if self.running:
            logger.warning("TaskScheduler is already running")
            return
            
        self.running = True
        self.stop_event.clear()
        
        # Start the worker thread
        self.worker_thread = Thread(
            target=self._worker_loop,
            args=(modules, model_manager, memory),
            daemon=True
        )
        self.worker_thread.start()
        
        logger.info("TaskScheduler started")
    
    def stop(self):
        """Stop the task scheduler."""
        if not self.running:
            logger.warning("TaskScheduler is not running")
            return
            
        self.running = False
        self.stop_event.set()
        
        if self.worker_thread:
            self.worker_thread.join(timeout=5.0)
            
        logger.info("TaskScheduler stopped")
    
    def _worker_loop(self, modules: Dict[str, Any], model_manager: Any, memory: Any):
        """
        Main worker loop for processing tasks.
        
        Args:
            modules: Available modules
            model_manager: Model manager instance
            memory: Memory system instance
        """
        while self.running and not self.stop_event.is_set():
            try:
                # Get the next task with a timeout
                try:
                    task = self.task_queue.get(timeout=1.0)
                except Exception:
                    continue
                    
                logger.info(f"Processing task: {task}")
                
                # Execute the task
                handler = self.task_definitions.get(task.name)
                if handler:
                    try:
                        result = handler(task.params, modules, model_manager, memory)
                        if task.callback:
                            task.callback(result)
                    except Exception as e:
                        logger.error(f"Error executing task {task.name}: {str(e)}")
                else:
                    logger.error(f"No handler found for task: {task.name}")
                    
                self.task_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error in task worker loop: {str(e)}")
    
    # Built-in task handlers
    
    def _handle_post_content(self, params: Dict[str, Any], modules: Dict[str, Any], 
                            model_manager: Any, memory: Any) -> Any:
        """Handle posting content task."""
        platform = params.get("platform", "default")
        content_type = params.get("content_type", "text")
        
        # Find the appropriate module
        module_name = f"{platform}_posting"
        if module_name in modules:
            return modules[module_name].post_content(params)
        elif "social_media" in modules:
            return modules["social_media"].post_content(params)
        else:
            logger.error(f"No suitable module found for posting to {platform}")
            return None
    
    def _handle_interact_with_influencer(self, params: Dict[str, Any], modules: Dict[str, Any], 
                                        model_manager: Any, memory: Any) -> Any:
        """Handle influencer interaction task."""
        platform = params.get("platform", "default")
        influencer_id = params.get("influencer_id")
        
        if not influencer_id:
            logger.error("No influencer_id provided")
            return None
            
        # Find the appropriate module
        module_name = f"{platform}_interaction"
        if module_name in modules:
            return modules[module_name].interact_with_influencer(params)
        elif "influencer_interaction" in modules:
            return modules["influencer_interaction"].interact_with_influencer(params)
        else:
            logger.error(f"No suitable module found for interacting on {platform}")
            return None
    
    def _handle_reply_to_comment(self, params: Dict[str, Any], modules: Dict[str, Any], 
                               model_manager: Any, memory: Any) -> Any:
        """Handle comment reply task."""
        platform = params.get("platform", "default")
        comment_id = params.get("comment_id")
        
        if not comment_id:
            logger.error("No comment_id provided")
            return None
            
        # Find the appropriate module
        module_name = f"{platform}_commenting"
        if module_name in modules:
            return modules[module_name].reply_to_comment(params)
        elif "comment_reply" in modules:
            return modules["comment_reply"].reply_to_comment(params)
        else:
            logger.error(f"No suitable module found for commenting on {platform}")
            return None
    
    def _handle_generate_content(self, params: Dict[str, Any], modules: Dict[str, Any], 
                               model_manager: Any, memory: Any) -> Any:
        """Handle content generation task."""
        content_type = params.get("content_type", "text")
        
        # Find the appropriate module based on content type
        if content_type == "meme" and "meme_generator" in modules:
            return modules["meme_generator"].generate(params)
        elif content_type == "gif" and "gif_generator" in modules:
            return modules["gif_generator"].generate(params)
        elif content_type == "image" and "image_generator" in modules:
            return modules["image_generator"].generate(params)
        elif "content_generator" in modules:
            return modules["content_generator"].generate_content(params)
        else:
            logger.error(f"No suitable module found for generating {content_type}")
            return None