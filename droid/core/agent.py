"""
Core Agent Module - Central orchestration system for the AI agent.
"""
import logging
from typing import Dict, List, Optional, Any

from droid.core.model_manager import ModelManager
from droid.core.task_scheduler import TaskScheduler
from droid.core.memory import MemorySystem
from droid.utils.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class Agent:
    """
    Main Agent class that orchestrates all components and modules.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the Agent with configuration.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_config()
        
        # Initialize core components
        self.model_manager = ModelManager(self.config.get('models', {}))
        self.memory = MemorySystem(self.config.get('memory', {}))
        self.task_scheduler = TaskScheduler(self.config.get('tasks', {}))
        
        # Modules dictionary to store loaded modules
        self.modules = {}
        
        # Load modules based on configuration
        self._load_modules()
        
        logger.info("Agent initialized successfully")
    
    def _load_modules(self):
        """Load all modules specified in the configuration."""
        modules_config = self.config.get('modules', {})
        
        for module_name, module_config in modules_config.items():
            if not module_config.get('enabled', True):
                logger.info(f"Module {module_name} is disabled, skipping")
                continue
                
            try:
                # Dynamic import of the module
                module_path = module_config.get('path', f"droid.modules.{module_name}")
                module_class = module_config.get('class', module_name.capitalize())
                
                module = __import__(module_path, fromlist=[module_class])
                module_cls = getattr(module, module_class)
                
                # Initialize the module with its configuration
                self.modules[module_name] = module_cls(
                    config=module_config,
                    model_manager=self.model_manager,
                    memory=self.memory
                )
                logger.info(f"Loaded module: {module_name}")
            except Exception as e:
                logger.error(f"Failed to load module {module_name}: {str(e)}")
    
    def execute_task(self, task_name: str, params: Dict[str, Any] = None) -> Any:
        """
        Execute a specific task.
        
        Args:
            task_name: Name of the task to execute
            params: Parameters for the task
            
        Returns:
            Result of the task execution
        """
        return self.task_scheduler.schedule_task(task_name, params, self.modules, self.model_manager, self.memory)
    
    def run(self):
        """Start the agent's main loop."""
        logger.info("Agent starting main loop")
        self.task_scheduler.run(self.modules, self.model_manager, self.memory)