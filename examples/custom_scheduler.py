#!/usr/bin/env python3
"""
Example of creating and using a custom task scheduler with the Droid agent.
"""
import os
import sys
import json
import time
import argparse
import logging
import threading
import queue
from datetime import datetime, timedelta
from droid.core.agent import Agent
from droid.core.task_scheduler import TaskScheduler
from droid.utils.logger import setup_logging

class CustomScheduler(TaskScheduler):
    """A custom task scheduler for the Droid agent."""
    
    def __init__(self, config=None):
        """Initialize the custom task scheduler."""
        super().__init__(config)
        self.config = config or {}
        self.name = self.config.get("name", "Custom Scheduler")
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initializing {self.name}")
        
        # Initialize the task queue
        self.task_queue = queue.PriorityQueue()
        self.scheduled_tasks = {}
        self.recurring_tasks = {}
        self.task_results = {}
        self.next_task_id = 1
        self.running = False
        self.thread = None
        self.lock = threading.Lock()
    
    def add_task(self, task_name, params=None, priority=5, scheduled_time=None, task_id=None):
        """Add a task to the scheduler."""
        with self.lock:
            if task_id is None:
                task_id = f"task_{self.next_task_id}"
                self.next_task_id += 1
            
            params = params or {}
            scheduled_time = scheduled_time or datetime.now()
            
            task = {
                "id": task_id,
                "name": task_name,
                "params": params,
                "priority": priority,
                "scheduled_time": scheduled_time,
                "status": "pending"
            }
            
            # Add to the queue
            self.task_queue.put((priority, scheduled_time, task_id))
            self.scheduled_tasks[task_id] = task
            
            self.logger.info(f"Added task: {task_id} ({task_name}) with priority {priority}")
            return task_id
    
    def add_recurring_task(self, task_name, params=None, priority=5, interval_minutes=60, task_id=None):
        """Add a recurring task to the scheduler."""
        with self.lock:
            if task_id is None:
                task_id = f"recurring_{self.next_task_id}"
                self.next_task_id += 1
            
            params = params or {}
            next_run = datetime.now()
            
            task = {
                "id": task_id,
                "name": task_name,
                "params": params,
                "priority": priority,
                "interval_minutes": interval_minutes,
                "next_run": next_run,
                "status": "pending"
            }
            
            # Add to recurring tasks
            self.recurring_tasks[task_id] = task
            
            # Add to the queue
            self.add_task(task_name, params, priority, next_run, task_id)
            
            self.logger.info(f"Added recurring task: {task_id} ({task_name}) with interval {interval_minutes} minutes")
            return task_id
    
    def get_task(self, task_id):
        """Get a task by ID."""
        with self.lock:
            if task_id in self.scheduled_tasks:
                return self.scheduled_tasks[task_id]
            
            if task_id in self.recurring_tasks:
                return self.recurring_tasks[task_id]
            
            return None
    
    def get_tasks(self, status=None):
        """Get all tasks, optionally filtered by status."""
        with self.lock:
            tasks = []
            
            for task_id, task in self.scheduled_tasks.items():
                if status is None or task["status"] == status:
                    tasks.append(task)
            
            return tasks
    
    def get_recurring_tasks(self):
        """Get all recurring tasks."""
        with self.lock:
            return list(self.recurring_tasks.values())
    
    def get_task_result(self, task_id):
        """Get the result of a task."""
        with self.lock:
            if task_id in self.task_results:
                return self.task_results[task_id]
            
            return None
    
    def update_task_status(self, task_id, status, result=None):
        """Update the status of a task."""
        with self.lock:
            if task_id in self.scheduled_tasks:
                self.scheduled_tasks[task_id]["status"] = status
                
                if result is not None:
                    self.task_results[task_id] = result
                
                self.logger.info(f"Updated task status: {task_id} -> {status}")
                return True
            
            return False
    
    def cancel_task(self, task_id):
        """Cancel a task."""
        with self.lock:
            if task_id in self.scheduled_tasks:
                self.scheduled_tasks[task_id]["status"] = "cancelled"
                self.logger.info(f"Cancelled task: {task_id}")
                return True
            
            if task_id in self.recurring_tasks:
                del self.recurring_tasks[task_id]
                
                if task_id in self.scheduled_tasks:
                    self.scheduled_tasks[task_id]["status"] = "cancelled"
                
                self.logger.info(f"Cancelled recurring task: {task_id}")
                return True
            
            return False
    
    def run(self, agent):
        """Run the scheduler."""
        self.running = True
        self.agent = agent
        
        if self.thread is None or not self.thread.is_alive():
            self.thread = threading.Thread(target=self._run_loop)
            self.thread.daemon = True
            self.thread.start()
        
        self.logger.info("Scheduler started")
    
    def stop(self):
        """Stop the scheduler."""
        self.running = False
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        
        self.logger.info("Scheduler stopped")
    
    def _run_loop(self):
        """Run the scheduler loop."""
        while self.running:
            try:
                # Check for due tasks
                now = datetime.now()
                
                # Check recurring tasks
                with self.lock:
                    for task_id, task in list(self.recurring_tasks.items()):
                        if task["next_run"] <= now:
                            # Schedule the next run
                            next_run = now + timedelta(minutes=task["interval_minutes"])
                            task["next_run"] = next_run
                            
                            # Add to the queue
                            self.add_task(
                                task["name"],
                                task["params"],
                                task["priority"],
                                now,
                                f"{task_id}_{now.strftime('%Y%m%d%H%M%S')}"
                            )
                
                # Process the queue
                try:
                    priority, scheduled_time, task_id = self.task_queue.get(block=False)
                    
                    with self.lock:
                        if task_id in self.scheduled_tasks:
                            task = self.scheduled_tasks[task_id]
                            
                            if task["status"] == "pending" and scheduled_time <= now:
                                # Execute the task
                                self.logger.info(f"Executing task: {task_id} ({task['name']})")
                                self.update_task_status(task_id, "running")
                                
                                try:
                                    result = self.agent.execute_task(task["name"], task["params"])
                                    self.update_task_status(task_id, "completed", result)
                                except Exception as e:
                                    self.logger.error(f"Error executing task {task_id}: {str(e)}")
                                    self.update_task_status(task_id, "failed", {"error": str(e)})
                            else:
                                # Put it back in the queue
                                self.task_queue.put((priority, scheduled_time, task_id))
                    
                    self.task_queue.task_done()
                    
                except queue.Empty:
                    # No tasks in the queue
                    pass
                
                # Sleep for a bit
                time.sleep(1.0)
                
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {str(e)}")
                time.sleep(5.0)

def main():
    """Run the agent with a custom task scheduler."""
    parser = argparse.ArgumentParser(description="Run the Droid agent with a custom task scheduler")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = "DEBUG" if args.debug else "INFO"
    setup_logging({"level": log_level})
    logger = logging.getLogger(__name__)
    
    # Create the custom scheduler
    scheduler_config = {
        "name": "Custom Task Scheduler"
    }
    scheduler = CustomScheduler(scheduler_config)
    
    # Create the agent with the custom scheduler
    agent = Agent()
    agent.scheduler = scheduler
    
    # Start the scheduler
    scheduler.run(agent)
    
    logger.info("Agent initialized with custom task scheduler")
    
    # Run in interactive mode
    if args.interactive:
        print("Droid AI Agent with Custom Scheduler - Interactive Mode")
        print("Type 'exit' to quit")
        print("Type 'help' for a list of commands")
        
        while True:
            try:
                command = input("\nScheduler> ")
                
                if command.lower() == "exit":
                    break
                
                if command.lower() == "help":
                    print("\nAvailable commands:")
                    print("  add <task_name> <params> [priority]           - Add a task")
                    print("  recurring <task_name> <params> <interval>     - Add a recurring task")
                    print("  list [status]                                 - List tasks")
                    print("  recurring_list                                - List recurring tasks")
                    print("  get <task_id>                                 - Get task details")
                    print("  result <task_id>                              - Get task result")
                    print("  cancel <task_id>                              - Cancel a task")
                    print("  exit                                          - Exit the program")
                    print("  help                                          - Show this help message")
                    continue
                
                if command.lower().startswith("add "):
                    parts = command.split(" ", 3)
                    if len(parts) < 3:
                        print("Error: Missing task name or parameters")
                        print("Usage: add <task_name> <params> [priority]")
                        continue
                    
                    task_name = parts[1]
                    
                    try:
                        params = json.loads(parts[2])
                    except json.JSONDecodeError:
                        print(f"Error: Invalid JSON parameters: {parts[2]}")
                        continue
                    
                    priority = int(parts[3]) if len(parts) > 3 else 5
                    
                    task_id = scheduler.add_task(task_name, params, priority)
                    print(f"Task added with ID: {task_id}")
                    continue
                
                if command.lower().startswith("recurring "):
                    parts = command.split(" ", 4)
                    if len(parts) < 4:
                        print("Error: Missing task name, parameters, or interval")
                        print("Usage: recurring <task_name> <params> <interval> [priority]")
                        continue
                    
                    task_name = parts[1]
                    
                    try:
                        params = json.loads(parts[2])
                    except json.JSONDecodeError:
                        print(f"Error: Invalid JSON parameters: {parts[2]}")
                        continue
                    
                    interval = int(parts[3])
                    priority = int(parts[4]) if len(parts) > 4 else 5
                    
                    task_id = scheduler.add_recurring_task(task_name, params, priority, interval)
                    print(f"Recurring task added with ID: {task_id}")
                    continue
                
                if command.lower().startswith("list "):
                    parts = command.split(" ")
                    status = parts[1]
                    tasks = scheduler.get_tasks(status)
                    
                    print(f"Tasks with status '{status}':")
                    for task in tasks:
                        scheduled_time = task["scheduled_time"].strftime("%Y-%m-%d %H:%M:%S") if isinstance(task["scheduled_time"], datetime) else task["scheduled_time"]
                        print(f"  ID: {task['id']}, Name: {task['name']}, Priority: {task['priority']}, Scheduled: {scheduled_time}")
                    continue
                
                if command.lower() == "list":
                    tasks = scheduler.get_tasks()
                    
                    print("All tasks:")
                    for task in tasks:
                        scheduled_time = task["scheduled_time"].strftime("%Y-%m-%d %H:%M:%S") if isinstance(task["scheduled_time"], datetime) else task["scheduled_time"]
                        print(f"  ID: {task['id']}, Name: {task['name']}, Status: {task['status']}, Priority: {task['priority']}, Scheduled: {scheduled_time}")
                    continue
                
                if command.lower() == "recurring_list":
                    tasks = scheduler.get_recurring_tasks()
                    
                    print("Recurring tasks:")
                    for task in tasks:
                        next_run = task["next_run"].strftime("%Y-%m-%d %H:%M:%S") if isinstance(task["next_run"], datetime) else task["next_run"]
                        print(f"  ID: {task['id']}, Name: {task['name']}, Interval: {task['interval_minutes']} minutes, Next run: {next_run}")
                    continue
                
                if command.lower().startswith("get "):
                    parts = command.split(" ")
                    task_id = parts[1]
                    task = scheduler.get_task(task_id)
                    
                    if task:
                        print(f"Task {task_id}:")
                        for key, value in task.items():
                            if key in ["scheduled_time", "next_run"] and isinstance(value, datetime):
                                value = value.strftime("%Y-%m-%d %H:%M:%S")
                            print(f"  {key}: {value}")
                    else:
                        print(f"Task {task_id} not found")
                    continue
                
                if command.lower().startswith("result "):
                    parts = command.split(" ")
                    task_id = parts[1]
                    result = scheduler.get_task_result(task_id)
                    
                    if result:
                        print(f"Result of task {task_id}:")
                        print(json.dumps(result, indent=2))
                    else:
                        print(f"No result found for task {task_id}")
                    continue
                
                if command.lower().startswith("cancel "):
                    parts = command.split(" ")
                    task_id = parts[1]
                    result = scheduler.cancel_task(task_id)
                    
                    if result:
                        print(f"Task {task_id} cancelled")
                    else:
                        print(f"Task {task_id} not found")
                    continue
                
                print(f"Unknown command: {command}")
                
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {str(e)}")
        
        # Stop the scheduler
        scheduler.stop()
        return
    
    # Run some example tasks
    print("Running example tasks with custom scheduler:")
    
    print("\n1. Add a simple task:")
    task_id = scheduler.add_task("generate_content", {"content_type": "text", "prompt": "Hello, world!"})
    print(f"Task added with ID: {task_id}")
    
    print("\n2. Add a recurring task:")
    recurring_id = scheduler.add_recurring_task("generate_content", {"content_type": "text", "prompt": "Recurring task"}, 5, 5)
    print(f"Recurring task added with ID: {recurring_id}")
    
    print("\n3. Wait for tasks to execute...")
    time.sleep(10)
    
    print("\n4. Check task results:")
    result = scheduler.get_task_result(task_id)
    if result:
        print(f"Result of task {task_id}:")
        print(json.dumps(result, indent=2))
    else:
        print(f"No result found for task {task_id}")
    
    print("\n5. List all tasks:")
    tasks = scheduler.get_tasks()
    for task in tasks:
        scheduled_time = task["scheduled_time"].strftime("%Y-%m-%d %H:%M:%S") if isinstance(task["scheduled_time"], datetime) else task["scheduled_time"]
        print(f"  ID: {task['id']}, Name: {task['name']}, Status: {task['status']}, Priority: {task['priority']}, Scheduled: {scheduled_time}")
    
    print("\n6. Cancel the recurring task:")
    scheduler.cancel_task(recurring_id)
    print(f"Recurring task {recurring_id} cancelled")
    
    # Stop the scheduler
    scheduler.stop()

if __name__ == "__main__":
    main()