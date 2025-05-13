#!/usr/bin/env python3
"""
Test script for CrewAI Lite implementation.
"""
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add the parent directory to the path so we can import the droid package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from droid.utils.crewai_lite import Agent, Task, Crew, Process, Tool

class TestCrewAILite(unittest.TestCase):
    """Test cases for CrewAI Lite implementation."""
    
    def test_tool(self):
        """Test the Tool class."""
        # Create a mock function
        mock_func = MagicMock(return_value="Tool result")
        
        # Create a tool
        tool = Tool(name="test_tool", description="Test tool", func=mock_func)
        
        # Test the tool
        result = tool.run("arg1", kwarg1="value1")
        
        # Verify the result
        self.assertEqual(result, "Tool result")
        mock_func.assert_called_once_with("arg1", kwarg1="value1")
    
    def test_agent(self):
        """Test the Agent class."""
        # Create a mock LLM
        mock_llm = MagicMock()
        mock_llm.generate.return_value = "Agent response"
        
        # Create an agent
        agent = Agent(
            role="Test Agent",
            goal="Test goal",
            backstory="Test backstory",
            verbose=True,
            llm=mock_llm
        )
        
        # Create a task
        task = Task(
            description="Test task",
            agent=agent,
            expected_output="Test output",
            context=["Context 1", "Context 2"]
        )
        
        # Test the agent
        result = agent.execute_task(task)
        
        # Verify the result
        self.assertEqual(result, "Agent response")
        mock_llm.generate.assert_called_once()
    
    def test_task(self):
        """Test the Task class."""
        # Create a mock agent
        mock_agent = MagicMock()
        mock_agent.execute_task.return_value = "Task result"
        
        # Create a task
        task = Task(
            description="Test task",
            agent=mock_agent,
            expected_output="Test output",
            context=["Context 1", "Context 2"]
        )
        
        # Test the task
        result = task.execute()
        
        # Verify the result
        self.assertEqual(result, "Task result")
        mock_agent.execute_task.assert_called_once_with(task)
    
    def test_crew_sequential(self):
        """Test the Crew class with sequential process."""
        # Create mock agents
        mock_agent1 = MagicMock()
        mock_agent2 = MagicMock()
        
        # Create mock tasks
        mock_task1 = MagicMock()
        mock_task1.agent = mock_agent1
        mock_task1.result = "Task 1 result"
        mock_task1.execute.return_value = "Task 1 result"
        
        mock_task2 = MagicMock()
        mock_task2.agent = mock_agent2
        mock_task2.result = "Task 2 result"
        mock_task2.execute.return_value = "Task 2 result"
        
        # Create a crew
        crew = Crew(
            agents=[mock_agent1, mock_agent2],
            tasks=[mock_task1, mock_task2],
            verbose=True,
            process=Process.SEQUENTIAL,
            memory=True
        )
        
        # Test the crew
        result = crew.kickoff(inputs={"input1": "value1"})
        
        # Verify the result
        self.assertEqual(len(result), 2)
        mock_task1.execute.assert_called_once()
        mock_task2.execute.assert_called_once()
    
    def test_crew_hierarchical(self):
        """Test the Crew class with hierarchical process."""
        # Create mock agents
        mock_agent1 = MagicMock()
        mock_agent2 = MagicMock()
        
        # Create mock tasks
        mock_task1 = MagicMock()
        mock_task1.agent = mock_agent1
        mock_task1.result = "Task 1 result"
        mock_task1.execute.return_value = "Task 1 result"
        
        mock_task2 = MagicMock()
        mock_task2.agent = mock_agent2
        mock_task2.result = "Task 2 result"
        mock_task2.execute.return_value = "Task 2 result"
        
        # Create a crew
        crew = Crew(
            agents=[mock_agent1, mock_agent2],
            tasks=[mock_task1, mock_task2],
            verbose=True,
            process=Process.HIERARCHICAL,
            memory=True
        )
        
        # Test the crew
        result = crew.kickoff(inputs={"input1": "value1"})
        
        # Verify the result
        self.assertEqual(len(result), 2)
        mock_task1.execute.assert_called_once()
        mock_task2.execute.assert_called_once()

if __name__ == "__main__":
    unittest.main()