#!/usr/bin/env python3
"""
Example of creating and using a custom plugin system with the Droid agent.
"""
import os
import sys
import importlib
import inspect
import argparse
import logging
from droid.core.agent import Agent
from droid.utils.logger import setup_logging

class PluginBase:
    """Base class for all plugins."""
    
    def __init__(self, agent, config=None):
        """Initialize the plugin."""
        self.agent = agent
        self.config = config or {}
        self.name = self.__class__.__name__
        self.logger = logging.getLogger(f"plugin.{self.name}")
        self.logger.info(f"Initializing plugin: {self.name}")
    
    def initialize(self):
        """Initialize the plugin. Called after all plugins are loaded."""
        pass
    
    def shutdown(self):
        """Shutdown the plugin. Called before the agent shuts down."""
        pass
    
    def get_capabilities(self):
        """Get the capabilities of the plugin."""
        return []
    
    def handle_event(self, event_type, event_data):
        """Handle an event."""
        pass
    
    def execute_action(self, action_name, action_params):
        """Execute an action."""
        pass

class PluginManager:
    """Manager for loading and managing plugins."""
    
    def __init__(self, agent, plugin_dirs=None):
        """Initialize the plugin manager."""
        self.agent = agent
        self.plugin_dirs = plugin_dirs or ["plugins"]
        self.plugins = {}
        self.logger = logging.getLogger("plugin_manager")
        self.logger.info("Initializing plugin manager")
    
    def discover_plugins(self):
        """Discover plugins in the plugin directories."""
        plugin_classes = []
        
        for plugin_dir in self.plugin_dirs:
            if not os.path.exists(plugin_dir):
                self.logger.warning(f"Plugin directory not found: {plugin_dir}")
                continue
            
            self.logger.info(f"Discovering plugins in {plugin_dir}")
            
            # Add the plugin directory to the Python path
            sys.path.insert(0, os.path.abspath(plugin_dir))
            
            # Find all Python files in the plugin directory
            for filename in os.listdir(plugin_dir):
                if filename.endswith(".py") and not filename.startswith("__"):
                    module_name = filename[:-3]
                    try:
                        # Import the module
                        module = importlib.import_module(module_name)
                        
                        # Find all classes in the module that are subclasses of PluginBase
                        for name, obj in inspect.getmembers(module, inspect.isclass):
                            if issubclass(obj, PluginBase) and obj != PluginBase:
                                plugin_classes.append(obj)
                                self.logger.info(f"Discovered plugin: {name}")
                    except Exception as e:
                        self.logger.error(f"Error loading plugin module {module_name}: {str(e)}")
            
            # Remove the plugin directory from the Python path
            sys.path.pop(0)
        
        return plugin_classes
    
    def load_plugins(self, plugin_configs=None):
        """Load plugins."""
        plugin_configs = plugin_configs or {}
        plugin_classes = self.discover_plugins()
        
        for plugin_class in plugin_classes:
            plugin_name = plugin_class.__name__
            plugin_config = plugin_configs.get(plugin_name, {})
            
            try:
                # Create an instance of the plugin
                plugin = plugin_class(self.agent, plugin_config)
                self.plugins[plugin_name] = plugin
                self.logger.info(f"Loaded plugin: {plugin_name}")
            except Exception as e:
                self.logger.error(f"Error loading plugin {plugin_name}: {str(e)}")
        
        # Initialize all plugins
        for plugin_name, plugin in self.plugins.items():
            try:
                plugin.initialize()
                self.logger.info(f"Initialized plugin: {plugin_name}")
            except Exception as e:
                self.logger.error(f"Error initializing plugin {plugin_name}: {str(e)}")
    
    def get_plugin(self, plugin_name):
        """Get a plugin by name."""
        return self.plugins.get(plugin_name)
    
    def get_plugins(self):
        """Get all plugins."""
        return self.plugins
    
    def get_capabilities(self):
        """Get all capabilities from all plugins."""
        capabilities = []
        
        for plugin_name, plugin in self.plugins.items():
            try:
                plugin_capabilities = plugin.get_capabilities()
                capabilities.extend(plugin_capabilities)
            except Exception as e:
                self.logger.error(f"Error getting capabilities from plugin {plugin_name}: {str(e)}")
        
        return capabilities
    
    def handle_event(self, event_type, event_data):
        """Handle an event by dispatching it to all plugins."""
        for plugin_name, plugin in self.plugins.items():
            try:
                plugin.handle_event(event_type, event_data)
            except Exception as e:
                self.logger.error(f"Error handling event {event_type} in plugin {plugin_name}: {str(e)}")
    
    def execute_action(self, action_name, action_params):
        """Execute an action by finding a plugin that can handle it."""
        for plugin_name, plugin in self.plugins.items():
            try:
                result = plugin.execute_action(action_name, action_params)
                if result is not None:
                    return result
            except Exception as e:
                self.logger.error(f"Error executing action {action_name} in plugin {plugin_name}: {str(e)}")
        
        return None
    
    def shutdown(self):
        """Shutdown all plugins."""
        for plugin_name, plugin in self.plugins.items():
            try:
                plugin.shutdown()
                self.logger.info(f"Shutdown plugin: {plugin_name}")
            except Exception as e:
                self.logger.error(f"Error shutting down plugin {plugin_name}: {str(e)}")

# Example plugin implementations
class LoggingPlugin(PluginBase):
    """Plugin for logging events."""
    
    def initialize(self):
        """Initialize the plugin."""
        self.logger.info("LoggingPlugin initialized")
        self.log_file = self.config.get("log_file")
        
        if self.log_file:
            self.logger.info(f"Logging events to {self.log_file}")
            
            # Create the log directory if it doesn't exist
            log_dir = os.path.dirname(self.log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
    
    def get_capabilities(self):
        """Get the capabilities of the plugin."""
        return ["logging"]
    
    def handle_event(self, event_type, event_data):
        """Handle an event."""
        self.logger.info(f"Event: {event_type} - {event_data}")
        
        if self.log_file:
            with open(self.log_file, "a") as f:
                f.write(f"{event_type}: {event_data}\n")
    
    def shutdown(self):
        """Shutdown the plugin."""
        self.logger.info("LoggingPlugin shutdown")

class NotificationPlugin(PluginBase):
    """Plugin for sending notifications."""
    
    def initialize(self):
        """Initialize the plugin."""
        self.logger.info("NotificationPlugin initialized")
        self.notification_method = self.config.get("method", "console")
        self.notification_target = self.config.get("target")
    
    def get_capabilities(self):
        """Get the capabilities of the plugin."""
        return ["notifications"]
    
    def handle_event(self, event_type, event_data):
        """Handle an event."""
        if event_type == "notification":
            self.send_notification(event_data.get("message"), event_data.get("level", "info"))
    
    def execute_action(self, action_name, action_params):
        """Execute an action."""
        if action_name == "send_notification":
            return self.send_notification(
                action_params.get("message"),
                action_params.get("level", "info")
            )
        return None
    
    def send_notification(self, message, level="info"):
        """Send a notification."""
        self.logger.info(f"Sending {level} notification: {message}")
        
        if self.notification_method == "console":
            print(f"[{level.upper()}] {message}")
            return True
        elif self.notification_method == "file" and self.notification_target:
            with open(self.notification_target, "a") as f:
                f.write(f"[{level.upper()}] {message}\n")
            return True
        
        return False
    
    def shutdown(self):
        """Shutdown the plugin."""
        self.logger.info("NotificationPlugin shutdown")

class SchedulerPlugin(PluginBase):
    """Plugin for scheduling tasks."""
    
    def initialize(self):
        """Initialize the plugin."""
        self.logger.info("SchedulerPlugin initialized")
        self.tasks = {}
        self.next_task_id = 1
    
    def get_capabilities(self):
        """Get the capabilities of the plugin."""
        return ["scheduling"]
    
    def execute_action(self, action_name, action_params):
        """Execute an action."""
        if action_name == "schedule_task":
            return self.schedule_task(
                action_params.get("name"),
                action_params.get("params", {}),
                action_params.get("delay", 0)
            )
        elif action_name == "cancel_task":
            return self.cancel_task(action_params.get("task_id"))
        elif action_name == "get_tasks":
            return self.get_tasks()
        
        return None
    
    def schedule_task(self, name, params=None, delay=0):
        """Schedule a task."""
        if not name:
            return None
        
        task_id = self.next_task_id
        self.next_task_id += 1
        
        self.tasks[task_id] = {
            "id": task_id,
            "name": name,
            "params": params or {},
            "delay": delay,
            "status": "scheduled"
        }
        
        self.logger.info(f"Scheduled task {task_id}: {name} with delay {delay}")
        
        # In a real implementation, we would use a proper scheduler
        # For this example, we'll just log the task
        
        return task_id
    
    def cancel_task(self, task_id):
        """Cancel a task."""
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = "cancelled"
            self.logger.info(f"Cancelled task {task_id}")
            return True
        
        return False
    
    def get_tasks(self):
        """Get all tasks."""
        return list(self.tasks.values())
    
    def shutdown(self):
        """Shutdown the plugin."""
        self.logger.info("SchedulerPlugin shutdown")

def create_plugin_directory():
    """Create the plugin directory and example plugins."""
    plugin_dir = "plugins"
    
    if not os.path.exists(plugin_dir):
        os.makedirs(plugin_dir)
    
    # Create the logging plugin
    with open(os.path.join(plugin_dir, "logging_plugin.py"), "w") as f:
        f.write("""from examples.custom_plugin import PluginBase

class LoggingPlugin(PluginBase):
    \"\"\"Plugin for logging events.\"\"\"
    
    def initialize(self):
        \"\"\"Initialize the plugin.\"\"\"
        self.logger.info("LoggingPlugin initialized")
        self.log_file = self.config.get("log_file")
        
        if self.log_file:
            self.logger.info(f"Logging events to {self.log_file}")
            
            # Create the log directory if it doesn't exist
            import os
            log_dir = os.path.dirname(self.log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
    
    def get_capabilities(self):
        \"\"\"Get the capabilities of the plugin.\"\"\"
        return ["logging"]
    
    def handle_event(self, event_type, event_data):
        \"\"\"Handle an event.\"\"\"
        self.logger.info(f"Event: {event_type} - {event_data}")
        
        if self.log_file:
            with open(self.log_file, "a") as f:
                f.write(f"{event_type}: {event_data}\\n")
    
    def shutdown(self):
        \"\"\"Shutdown the plugin.\"\"\"
        self.logger.info("LoggingPlugin shutdown")
""")
    
    # Create the notification plugin
    with open(os.path.join(plugin_dir, "notification_plugin.py"), "w") as f:
        f.write("""from examples.custom_plugin import PluginBase

class NotificationPlugin(PluginBase):
    \"\"\"Plugin for sending notifications.\"\"\"
    
    def initialize(self):
        \"\"\"Initialize the plugin.\"\"\"
        self.logger.info("NotificationPlugin initialized")
        self.notification_method = self.config.get("method", "console")
        self.notification_target = self.config.get("target")
    
    def get_capabilities(self):
        \"\"\"Get the capabilities of the plugin.\"\"\"
        return ["notifications"]
    
    def handle_event(self, event_type, event_data):
        \"\"\"Handle an event.\"\"\"
        if event_type == "notification":
            self.send_notification(event_data.get("message"), event_data.get("level", "info"))
    
    def execute_action(self, action_name, action_params):
        \"\"\"Execute an action.\"\"\"
        if action_name == "send_notification":
            return self.send_notification(
                action_params.get("message"),
                action_params.get("level", "info")
            )
        return None
    
    def send_notification(self, message, level="info"):
        \"\"\"Send a notification.\"\"\"
        self.logger.info(f"Sending {level} notification: {message}")
        
        if self.notification_method == "console":
            print(f"[{level.upper()}] {message}")
            return True
        elif self.notification_method == "file" and self.notification_target:
            with open(self.notification_target, "a") as f:
                f.write(f"[{level.upper()}] {message}\\n")
            return True
        
        return False
    
    def shutdown(self):
        \"\"\"Shutdown the plugin.\"\"\"
        self.logger.info("NotificationPlugin shutdown")
""")
    
    # Create the scheduler plugin
    with open(os.path.join(plugin_dir, "scheduler_plugin.py"), "w") as f:
        f.write("""from examples.custom_plugin import PluginBase

class SchedulerPlugin(PluginBase):
    \"\"\"Plugin for scheduling tasks.\"\"\"
    
    def initialize(self):
        \"\"\"Initialize the plugin.\"\"\"
        self.logger.info("SchedulerPlugin initialized")
        self.tasks = {}
        self.next_task_id = 1
    
    def get_capabilities(self):
        \"\"\"Get the capabilities of the plugin.\"\"\"
        return ["scheduling"]
    
    def execute_action(self, action_name, action_params):
        \"\"\"Execute an action.\"\"\"
        if action_name == "schedule_task":
            return self.schedule_task(
                action_params.get("name"),
                action_params.get("params", {}),
                action_params.get("delay", 0)
            )
        elif action_name == "cancel_task":
            return self.cancel_task(action_params.get("task_id"))
        elif action_name == "get_tasks":
            return self.get_tasks()
        
        return None
    
    def schedule_task(self, name, params=None, delay=0):
        \"\"\"Schedule a task.\"\"\"
        if not name:
            return None
        
        task_id = self.next_task_id
        self.next_task_id += 1
        
        self.tasks[task_id] = {
            "id": task_id,
            "name": name,
            "params": params or {},
            "delay": delay,
            "status": "scheduled"
        }
        
        self.logger.info(f"Scheduled task {task_id}: {name} with delay {delay}")
        
        # In a real implementation, we would use a proper scheduler
        # For this example, we'll just log the task
        
        return task_id
    
    def cancel_task(self, task_id):
        \"\"\"Cancel a task.\"\"\"
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = "cancelled"
            self.logger.info(f"Cancelled task {task_id}")
            return True
        
        return False
    
    def get_tasks(self):
        \"\"\"Get all tasks.\"\"\"
        return list(self.tasks.values())
    
    def shutdown(self):
        \"\"\"Shutdown the plugin.\"\"\"
        self.logger.info("SchedulerPlugin shutdown")
""")

def main():
    """Run the agent with a custom plugin system."""
    parser = argparse.ArgumentParser(description="Run the Droid agent with a custom plugin system")
    parser.add_argument("--plugin-dir", type=str, default="plugins", help="Directory containing plugins")
    parser.add_argument("--log-file", type=str, default="/tmp/droid/events.log", help="Log file for events")
    parser.add_argument("--notification-method", type=str, default="console", choices=["console", "file"], help="Notification method")
    parser.add_argument("--notification-target", type=str, help="Notification target (file path for file method)")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = "DEBUG" if args.debug else "INFO"
    setup_logging({"level": log_level})
    logger = logging.getLogger(__name__)
    
    # Create the plugin directory and example plugins
    create_plugin_directory()
    
    # Create the agent
    agent = Agent()
    
    # Create the plugin manager
    plugin_manager = PluginManager(agent, [args.plugin_dir])
    
    # Configure plugins
    plugin_configs = {
        "LoggingPlugin": {
            "log_file": args.log_file
        },
        "NotificationPlugin": {
            "method": args.notification_method,
            "target": args.notification_target
        }
    }
    
    # Load plugins
    plugin_manager.load_plugins(plugin_configs)
    
    # Add the plugin manager to the agent
    agent.plugin_manager = plugin_manager
    
    # Get capabilities
    capabilities = plugin_manager.get_capabilities()
    logger.info(f"Agent capabilities: {capabilities}")
    
    # Send some events
    plugin_manager.handle_event("agent_start", {"timestamp": time.time()})
    plugin_manager.handle_event("notification", {"message": "Agent started", "level": "info"})
    
    # Execute some actions
    plugin_manager.execute_action("send_notification", {"message": "Hello from the agent!", "level": "info"})
    
    task_id = plugin_manager.execute_action("schedule_task", {
        "name": "generate_content",
        "params": {"content_type": "text", "prompt": "Hello world"},
        "delay": 5
    })
    
    if task_id:
        logger.info(f"Scheduled task with ID: {task_id}")
    
    # Get tasks
    tasks = plugin_manager.execute_action("get_tasks", {})
    logger.info(f"Tasks: {tasks}")
    
    # Shutdown plugins
    plugin_manager.shutdown()
    
    logger.info("Agent shutdown")

if __name__ == "__main__":
    import time
    main()