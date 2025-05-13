#!/usr/bin/env python3
"""
Example of creating and using a custom API with the Droid agent.
"""
import os
import sys
import json
import argparse
import logging
import threading
import time
from flask import Flask, request, jsonify
from droid.core.agent import Agent
from droid.utils.logger import setup_logging

class CustomAPI:
    """A custom API for the Droid agent."""
    
    def __init__(self, agent, config=None):
        """Initialize the custom API."""
        self.agent = agent
        self.config = config or {}
        self.name = self.config.get("name", "Custom API")
        self.host = self.config.get("host", "0.0.0.0")
        self.port = self.config.get("port", 5000)
        self.debug = self.config.get("debug", False)
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initializing {self.name}")
        
        # Create the Flask app
        self.app = Flask(__name__)
        self.setup_routes()
        
        # API key for authentication
        self.api_key = self.config.get("api_key", "droid-api-key")
        
        # Request counter
        self.request_counter = 0
        self.lock = threading.Lock()
    
    def setup_routes(self):
        """Set up the API routes."""
        # Health check
        self.app.route('/health')(self.health)
        
        # Agent info
        self.app.route('/info')(self.info)
        
        # Generate content
        self.app.route('/generate', methods=['POST'])(self.generate)
        
        # Execute task
        self.app.route('/task', methods=['POST'])(self.execute_task)
        
        # Get task status
        self.app.route('/task/<task_id>', methods=['GET'])(self.get_task)
        
        # List tasks
        self.app.route('/tasks', methods=['GET'])(self.list_tasks)
        
        # Memory operations
        self.app.route('/memory', methods=['POST'])(self.store_memory)
        self.app.route('/memory', methods=['GET'])(self.retrieve_memory)
        self.app.route('/memory/<memory_id>', methods=['GET'])(self.get_memory)
        self.app.route('/memory/<memory_id>', methods=['PUT'])(self.update_memory)
        self.app.route('/memory/<memory_id>', methods=['DELETE'])(self.delete_memory)
    
    def authenticate(self, req):
        """Authenticate the request."""
        api_key = req.headers.get('X-API-Key')
        if not api_key or api_key != self.api_key:
            return False
        return True
    
    def health(self):
        """Health check endpoint."""
        return jsonify({
            "status": "ok",
            "timestamp": time.time()
        })
    
    def info(self):
        """Agent info endpoint."""
        if not self.authenticate(request):
            return jsonify({"error": "Unauthorized"}), 401
        
        with self.lock:
            self.request_counter += 1
        
        return jsonify({
            "name": self.agent.name,
            "version": getattr(self.agent, "version", "1.0.0"),
            "modules": [module.__class__.__name__ for module in self.agent.modules],
            "request_count": self.request_counter
        })
    
    def generate(self):
        """Generate content endpoint."""
        if not self.authenticate(request):
            return jsonify({"error": "Unauthorized"}), 401
        
        with self.lock:
            self.request_counter += 1
        
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        content_type = data.get("type", "text")
        prompt = data.get("prompt")
        
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        try:
            if content_type == "text":
                result = self.agent.generate_text(prompt)
            elif content_type == "image":
                result = self.agent.generate_image(prompt)
            else:
                return jsonify({"error": f"Unsupported content type: {content_type}"}), 400
            
            return jsonify({
                "result": result,
                "type": content_type,
                "prompt": prompt
            })
        except Exception as e:
            self.logger.error(f"Error generating content: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    def execute_task(self):
        """Execute task endpoint."""
        if not self.authenticate(request):
            return jsonify({"error": "Unauthorized"}), 401
        
        with self.lock:
            self.request_counter += 1
        
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        task_name = data.get("task")
        params = data.get("params", {})
        
        if not task_name:
            return jsonify({"error": "No task name provided"}), 400
        
        try:
            task_id = self.agent.scheduler.add_task(task_name, params)
            
            return jsonify({
                "task_id": task_id,
                "status": "pending"
            })
        except Exception as e:
            self.logger.error(f"Error executing task: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    def get_task(self, task_id):
        """Get task status endpoint."""
        if not self.authenticate(request):
            return jsonify({"error": "Unauthorized"}), 401
        
        with self.lock:
            self.request_counter += 1
        
        try:
            task = self.agent.scheduler.get_task(task_id)
            
            if not task:
                return jsonify({"error": f"Task not found: {task_id}"}), 404
            
            result = self.agent.scheduler.get_task_result(task_id)
            
            return jsonify({
                "task_id": task_id,
                "status": task.get("status"),
                "result": result
            })
        except Exception as e:
            self.logger.error(f"Error getting task: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    def list_tasks(self):
        """List tasks endpoint."""
        if not self.authenticate(request):
            return jsonify({"error": "Unauthorized"}), 401
        
        with self.lock:
            self.request_counter += 1
        
        status = request.args.get("status")
        
        try:
            tasks = self.agent.scheduler.get_tasks(status)
            
            return jsonify({
                "tasks": tasks
            })
        except Exception as e:
            self.logger.error(f"Error listing tasks: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    def store_memory(self):
        """Store memory endpoint."""
        if not self.authenticate(request):
            return jsonify({"error": "Unauthorized"}), 401
        
        with self.lock:
            self.request_counter += 1
        
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        key = data.get("key")
        value = data.get("value")
        category = data.get("category")
        importance = data.get("importance", 1)
        
        if not key or value is None:
            return jsonify({"error": "Key and value are required"}), 400
        
        try:
            result = self.agent.memory.store(key, value, category, importance)
            
            return jsonify({
                "memory_id": result.get("id"),
                "key": key,
                "timestamp": result.get("timestamp")
            })
        except Exception as e:
            self.logger.error(f"Error storing memory: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    def retrieve_memory(self):
        """Retrieve memory endpoint."""
        if not self.authenticate(request):
            return jsonify({"error": "Unauthorized"}), 401
        
        with self.lock:
            self.request_counter += 1
        
        key = request.args.get("key")
        category = request.args.get("category")
        limit = request.args.get("limit", 10)
        
        try:
            limit = int(limit)
            memories = self.agent.memory.retrieve(key, category, limit)
            
            return jsonify({
                "memories": memories
            })
        except Exception as e:
            self.logger.error(f"Error retrieving memory: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    def get_memory(self, memory_id):
        """Get memory endpoint."""
        if not self.authenticate(request):
            return jsonify({"error": "Unauthorized"}), 401
        
        with self.lock:
            self.request_counter += 1
        
        try:
            memory_id = int(memory_id)
            memories = self.agent.memory.retrieve(limit=100)
            
            for memory in memories:
                if memory.get("id") == memory_id:
                    return jsonify(memory)
            
            return jsonify({"error": f"Memory not found: {memory_id}"}), 404
        except Exception as e:
            self.logger.error(f"Error getting memory: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    def update_memory(self, memory_id):
        """Update memory endpoint."""
        if not self.authenticate(request):
            return jsonify({"error": "Unauthorized"}), 401
        
        with self.lock:
            self.request_counter += 1
        
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        value = data.get("value")
        category = data.get("category")
        importance = data.get("importance")
        
        try:
            memory_id = int(memory_id)
            result = self.agent.memory.update(memory_id, value, category, importance)
            
            if result:
                return jsonify({"success": True})
            else:
                return jsonify({"error": f"Memory not found: {memory_id}"}), 404
        except Exception as e:
            self.logger.error(f"Error updating memory: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    def delete_memory(self, memory_id):
        """Delete memory endpoint."""
        if not self.authenticate(request):
            return jsonify({"error": "Unauthorized"}), 401
        
        with self.lock:
            self.request_counter += 1
        
        try:
            memory_id = int(memory_id)
            result = self.agent.memory.delete(memory_id)
            
            if result:
                return jsonify({"success": True})
            else:
                return jsonify({"error": f"Memory not found: {memory_id}"}), 404
        except Exception as e:
            self.logger.error(f"Error deleting memory: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    def run(self):
        """Run the API server."""
        self.logger.info(f"Starting API server on {self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, debug=self.debug)

def main():
    """Run the agent with a custom API."""
    parser = argparse.ArgumentParser(description="Run the Droid agent with a custom API")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="API server host")
    parser.add_argument("--port", type=int, default=5000, help="API server port")
    parser.add_argument("--api-key", type=str, default="droid-api-key", help="API key for authentication")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = "DEBUG" if args.debug else "INFO"
    setup_logging({"level": log_level})
    logger = logging.getLogger(__name__)
    
    # Create the agent
    agent = Agent()
    
    # Create the custom API
    api_config = {
        "name": "Droid Custom API",
        "host": args.host,
        "port": args.port,
        "api_key": args.api_key,
        "debug": args.debug
    }
    api = CustomAPI(agent, api_config)
    
    logger.info("Agent initialized with custom API")
    logger.info(f"API server will run on {args.host}:{args.port}")
    logger.info(f"API key: {args.api_key}")
    
    # Run the API server
    api.run()

if __name__ == "__main__":
    main()