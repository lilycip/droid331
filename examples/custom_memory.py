#!/usr/bin/env python3
"""
Example of creating and using a custom memory system with the Droid agent.
"""
import os
import sys
import json
import argparse
import logging
import sqlite3
from datetime import datetime
from droid.core.agent import Agent
from droid.core.memory import MemorySystem
from droid.utils.logger import setup_logging

class CustomMemory(MemorySystem):
    """A custom memory system for the Droid agent."""
    
    def __init__(self, config=None):
        """Initialize the custom memory system."""
        super().__init__(config)
        self.config = config or {}
        self.name = self.config.get("name", "Custom Memory")
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initializing {self.name}")
        
        # Initialize the database
        self.db_path = self.config.get("path", ":memory:")
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        # Create the memory table if it doesn't exist
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            category TEXT,
            timestamp TEXT,
            importance INTEGER DEFAULT 1
        )
        ''')
        self.conn.commit()
    
    def store(self, key, value, category=None, importance=1):
        """Store a memory."""
        timestamp = datetime.now().isoformat()
        
        # Convert value to JSON if it's not a string
        if not isinstance(value, str):
            value = json.dumps(value)
        
        self.cursor.execute(
            "INSERT INTO memory (key, value, category, timestamp, importance) VALUES (?, ?, ?, ?, ?)",
            (key, value, category, timestamp, importance)
        )
        self.conn.commit()
        
        self.logger.info(f"Stored memory: {key} (category: {category}, importance: {importance})")
        return {"id": self.cursor.lastrowid, "key": key, "timestamp": timestamp}
    
    def retrieve(self, key=None, category=None, limit=10):
        """Retrieve memories."""
        query = "SELECT id, key, value, category, timestamp, importance FROM memory WHERE 1=1"
        params = []
        
        if key:
            query += " AND key = ?"
            params.append(key)
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        query += " ORDER BY importance DESC, timestamp DESC LIMIT ?"
        params.append(limit)
        
        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        
        memories = []
        for row in rows:
            memory = {
                "id": row[0],
                "key": row[1],
                "value": row[2],
                "category": row[3],
                "timestamp": row[4],
                "importance": row[5]
            }
            
            # Try to parse the value as JSON
            try:
                memory["value"] = json.loads(memory["value"])
            except json.JSONDecodeError:
                pass
            
            memories.append(memory)
        
        self.logger.info(f"Retrieved {len(memories)} memories")
        return memories
    
    def update(self, memory_id, value=None, category=None, importance=None):
        """Update a memory."""
        query = "UPDATE memory SET "
        params = []
        updates = []
        
        if value is not None:
            # Convert value to JSON if it's not a string
            if not isinstance(value, str):
                value = json.dumps(value)
            
            updates.append("value = ?")
            params.append(value)
        
        if category is not None:
            updates.append("category = ?")
            params.append(category)
        
        if importance is not None:
            updates.append("importance = ?")
            params.append(importance)
        
        if not updates:
            self.logger.warning("No updates provided")
            return False
        
        query += ", ".join(updates)
        query += " WHERE id = ?"
        params.append(memory_id)
        
        self.cursor.execute(query, params)
        self.conn.commit()
        
        self.logger.info(f"Updated memory: {memory_id}")
        return self.cursor.rowcount > 0
    
    def delete(self, memory_id):
        """Delete a memory."""
        self.cursor.execute("DELETE FROM memory WHERE id = ?", (memory_id,))
        self.conn.commit()
        
        self.logger.info(f"Deleted memory: {memory_id}")
        return self.cursor.rowcount > 0
    
    def clear(self, category=None):
        """Clear memories."""
        if category:
            self.cursor.execute("DELETE FROM memory WHERE category = ?", (category,))
        else:
            self.cursor.execute("DELETE FROM memory")
        
        self.conn.commit()
        
        self.logger.info(f"Cleared memories{' for category: ' + category if category else ''}")
        return self.cursor.rowcount
    
    def close(self):
        """Close the memory system."""
        if self.conn:
            self.conn.close()
        
        self.logger.info("Memory system closed")

def main():
    """Run the agent with a custom memory system."""
    parser = argparse.ArgumentParser(description="Run the Droid agent with a custom memory system")
    parser.add_argument("--db-path", type=str, default=":memory:", help="Path to the SQLite database file")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = "DEBUG" if args.debug else "INFO"
    setup_logging({"level": log_level})
    logger = logging.getLogger(__name__)
    
    # Create the custom memory system
    memory_config = {
        "name": "SQLite Memory",
        "path": args.db_path
    }
    memory = CustomMemory(memory_config)
    
    # Create the agent with the custom memory system
    agent = Agent()
    agent.memory = memory
    
    logger.info("Agent initialized with custom memory system")
    
    # Run in interactive mode
    if args.interactive:
        print("Droid AI Agent with Custom Memory - Interactive Mode")
        print("Type 'exit' to quit")
        print("Type 'help' for a list of commands")
        
        while True:
            try:
                command = input("\nMemory> ")
                
                if command.lower() == "exit":
                    break
                
                if command.lower() == "help":
                    print("\nAvailable commands:")
                    print("  store <key> <value> [category] [importance]  - Store a memory")
                    print("  retrieve [key] [category] [limit]            - Retrieve memories")
                    print("  update <id> <value> [category] [importance]  - Update a memory")
                    print("  delete <id>                                  - Delete a memory")
                    print("  clear [category]                             - Clear memories")
                    print("  exit                                         - Exit the program")
                    print("  help                                         - Show this help message")
                    continue
                
                if command.lower().startswith("store "):
                    parts = command.split(" ", 4)
                    if len(parts) < 3:
                        print("Error: Missing key or value")
                        print("Usage: store <key> <value> [category] [importance]")
                        continue
                    
                    key = parts[1]
                    value = parts[2]
                    category = parts[3] if len(parts) > 3 else None
                    importance = int(parts[4]) if len(parts) > 4 else 1
                    
                    result = memory.store(key, value, category, importance)
                    print(f"Memory stored with ID: {result['id']}")
                    continue
                
                if command.lower().startswith("retrieve "):
                    parts = command.split(" ")
                    key = parts[1] if len(parts) > 1 and parts[1] != "_" else None
                    category = parts[2] if len(parts) > 2 and parts[2] != "_" else None
                    limit = int(parts[3]) if len(parts) > 3 else 10
                    
                    memories = memory.retrieve(key, category, limit)
                    print(f"Retrieved {len(memories)} memories:")
                    for mem in memories:
                        print(f"  ID: {mem['id']}, Key: {mem['key']}, Category: {mem['category']}, Importance: {mem['importance']}")
                        print(f"  Value: {mem['value']}")
                        print(f"  Timestamp: {mem['timestamp']}")
                        print()
                    continue
                
                if command.lower() == "retrieve":
                    memories = memory.retrieve()
                    print(f"Retrieved {len(memories)} memories:")
                    for mem in memories:
                        print(f"  ID: {mem['id']}, Key: {mem['key']}, Category: {mem['category']}, Importance: {mem['importance']}")
                        print(f"  Value: {mem['value']}")
                        print(f"  Timestamp: {mem['timestamp']}")
                        print()
                    continue
                
                if command.lower().startswith("update "):
                    parts = command.split(" ", 4)
                    if len(parts) < 3:
                        print("Error: Missing ID or value")
                        print("Usage: update <id> <value> [category] [importance]")
                        continue
                    
                    memory_id = int(parts[1])
                    value = parts[2]
                    category = parts[3] if len(parts) > 3 and parts[3] != "_" else None
                    importance = int(parts[4]) if len(parts) > 4 else None
                    
                    result = memory.update(memory_id, value, category, importance)
                    if result:
                        print(f"Memory {memory_id} updated")
                    else:
                        print(f"Memory {memory_id} not found")
                    continue
                
                if command.lower().startswith("delete "):
                    parts = command.split(" ")
                    if len(parts) < 2:
                        print("Error: Missing ID")
                        print("Usage: delete <id>")
                        continue
                    
                    memory_id = int(parts[1])
                    result = memory.delete(memory_id)
                    if result:
                        print(f"Memory {memory_id} deleted")
                    else:
                        print(f"Memory {memory_id} not found")
                    continue
                
                if command.lower().startswith("clear "):
                    parts = command.split(" ")
                    category = parts[1]
                    count = memory.clear(category)
                    print(f"Cleared {count} memories with category: {category}")
                    continue
                
                if command.lower() == "clear":
                    count = memory.clear()
                    print(f"Cleared {count} memories")
                    continue
                
                print(f"Unknown command: {command}")
                
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {str(e)}")
        
        # Close the memory system
        memory.close()
        return
    
    # Run some example commands
    print("Running example commands with custom memory system:")
    
    print("\n1. Store memories:")
    memory.store("user_preference", "dark_mode", "preferences", 2)
    memory.store("last_login", "2025-05-13T10:30:00", "session", 1)
    memory.store("favorite_color", "blue", "preferences", 3)
    memory.store("conversation", {"user": "Hello", "agent": "Hi there!"}, "conversations", 2)
    
    print("\n2. Retrieve memories by category:")
    preferences = memory.retrieve(category="preferences")
    print(f"Preferences: {json.dumps(preferences, indent=2)}")
    
    print("\n3. Retrieve a specific memory:")
    conversation = memory.retrieve(key="conversation")
    print(f"Conversation: {json.dumps(conversation, indent=2)}")
    
    print("\n4. Update a memory:")
    if preferences and len(preferences) > 0:
        memory.update(preferences[0]["id"], importance=5)
        updated = memory.retrieve(key=preferences[0]["key"])
        print(f"Updated memory: {json.dumps(updated, indent=2)}")
    
    print("\n5. Delete a memory:")
    if preferences and len(preferences) > 1:
        memory.delete(preferences[1]["id"])
        remaining = memory.retrieve(category="preferences")
        print(f"Remaining preferences: {json.dumps(remaining, indent=2)}")
    
    print("\n6. Clear memories by category:")
    memory.clear(category="session")
    all_memories = memory.retrieve(limit=100)
    print(f"All remaining memories: {json.dumps(all_memories, indent=2)}")
    
    # Close the memory system
    memory.close()

if __name__ == "__main__":
    main()