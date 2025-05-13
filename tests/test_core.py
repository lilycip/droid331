#!/usr/bin/env python3
"""
Tests for the core components of the Droid agent.
"""
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add the parent directory to the path so we can import the droid package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from droid.core.agent import Agent
from droid.core.model_manager import ModelManager
from droid.core.task_scheduler import TaskScheduler
from droid.core.memory import MemorySystem
from droid.utils.config_manager import ConfigManager

class TestAgent(unittest.TestCase):
    """Tests for the Agent class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock config
        self.config = {
            "agent": {
                "name": "TestAgent",
                "version": "0.1.0"
            },
            "models": {},
            "modules": {},
            "memory": {
                "path": "test_memory"
            },
            "logging": {
                "level": "INFO"
            }
        }
        
        # Mock the ConfigManager
        self.config_manager_mock = MagicMock(spec=ConfigManager)
        self.config_manager_mock.get_config.return_value = self.config
        
        # Patch the ConfigManager constructor
        self.config_manager_patch = patch('droid.core.agent.ConfigManager', return_value=self.config_manager_mock)
        self.config_manager_patch.start()
        
        # Mock the ModelManager
        self.model_manager_mock = MagicMock(spec=ModelManager)
        
        # Patch the ModelManager constructor
        self.model_manager_patch = patch('droid.core.agent.ModelManager', return_value=self.model_manager_mock)
        self.model_manager_patch.start()
        
        # Mock the MemorySystem
        self.memory_mock = MagicMock(spec=MemorySystem)
        
        # Patch the MemorySystem constructor
        self.memory_patch = patch('droid.core.agent.MemorySystem', return_value=self.memory_mock)
        self.memory_patch.start()
        
        # Mock the TaskScheduler
        self.task_scheduler_mock = MagicMock(spec=TaskScheduler)
        
        # Patch the TaskScheduler constructor
        self.task_scheduler_patch = patch('droid.core.agent.TaskScheduler', return_value=self.task_scheduler_mock)
        self.task_scheduler_patch.start()
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Stop all patches
        self.config_manager_patch.stop()
        self.model_manager_patch.stop()
        self.memory_patch.stop()
        self.task_scheduler_patch.stop()
    
    def test_agent_initialization(self):
        """Test that the Agent initializes correctly."""
        agent = Agent()
        
        # Check that the agent has the expected attributes
        self.assertEqual(agent.config_manager, self.config_manager_mock)
        self.assertEqual(agent.config, self.config)
        self.assertEqual(agent.model_manager, self.model_manager_mock)
        self.assertEqual(agent.memory, self.memory_mock)
        self.assertEqual(agent.task_scheduler, self.task_scheduler_mock)
        self.assertEqual(agent.modules, {})
    
    def test_execute_task(self):
        """Test that the Agent can execute a task."""
        agent = Agent()
        
        # Set up the mock task scheduler
        expected_result = {"success": True, "data": "test"}
        self.task_scheduler_mock.schedule_task.return_value = expected_result
        
        # Execute a task
        result = agent.execute_task("test_task", {"param": "value"})
        
        # Check that the task scheduler was called correctly
        self.task_scheduler_mock.schedule_task.assert_called_once_with(
            "test_task",
            {"param": "value"},
            agent.modules,
            agent.model_manager,
            agent.memory
        )
        
        # Check that the result is correct
        self.assertEqual(result, expected_result)
    
    def test_run(self):
        """Test that the Agent can run."""
        agent = Agent()
        
        # Run the agent
        agent.run()
        
        # Check that the task scheduler was called correctly
        self.task_scheduler_mock.run.assert_called_once_with(
            agent.modules,
            agent.model_manager,
            agent.memory
        )

if __name__ == '__main__':
    unittest.main()