"""
Memory System - Stores context, history, and learned information.
"""
import logging
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import sqlite3

logger = logging.getLogger(__name__)

class MemorySystem:
    """
    Manages the agent's memory, including short-term and long-term storage.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the MemorySystem with configuration.
        
        Args:
            config: Configuration dictionary for memory system
        """
        self.config = config
        self.memory_path = config.get("path", "memory")
        self.db_path = os.path.join(self.memory_path, "memory.db")
        
        # Create memory directory if it doesn't exist
        os.makedirs(self.memory_path, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Short-term memory (in-memory cache)
        self.short_term = {}
        
        logger.info("MemorySystem initialized")
    
    def _init_database(self):
        """Initialize the SQLite database for long-term memory."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables if they don't exist
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(category, key)
            )
            ''')
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_id TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                platform TEXT NOT NULL,
                interaction_type TEXT NOT NULL,
                content TEXT,
                metadata TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(entity_id, entity_type, platform, interaction_type, timestamp)
            )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("Memory database initialized")
        except Exception as e:
            logger.error(f"Failed to initialize memory database: {str(e)}")
    
    def store(self, category: str, key: str, value: Any, metadata: Dict[str, Any] = None) -> bool:
        """
        Store an item in memory.
        
        Args:
            category: Category of the memory item
            key: Key to store the value under
            value: Value to store
            metadata: Additional metadata about the value
            
        Returns:
            True if successful, False otherwise
        """
        # Store in short-term memory
        if category not in self.short_term:
            self.short_term[category] = {}
        self.short_term[category][key] = {
            "value": value,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Store in long-term memory
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Convert value and metadata to JSON strings
            value_json = json.dumps(value)
            metadata_json = json.dumps(metadata or {})
            
            # Insert or replace the memory item
            cursor.execute('''
            INSERT OR REPLACE INTO memory_items (category, key, value, metadata, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (category, key, value_json, metadata_json))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Stored memory item: {category}/{key}")
            return True
        except Exception as e:
            logger.error(f"Failed to store memory item {category}/{key}: {str(e)}")
            return False
    
    def retrieve(self, category: str, key: str) -> Optional[Any]:
        """
        Retrieve an item from memory.
        
        Args:
            category: Category of the memory item
            key: Key of the value to retrieve
            
        Returns:
            The stored value, or None if not found
        """
        # Check short-term memory first
        if category in self.short_term and key in self.short_term[category]:
            logger.debug(f"Retrieved memory item from short-term: {category}/{key}")
            return self.short_term[category][key]["value"]
        
        # Check long-term memory
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT value FROM memory_items
            WHERE category = ? AND key = ?
            ''', (category, key))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                value = json.loads(result[0])
                
                # Cache in short-term memory
                if category not in self.short_term:
                    self.short_term[category] = {}
                self.short_term[category][key] = {
                    "value": value,
                    "metadata": {},
                    "timestamp": datetime.now().isoformat()
                }
                
                logger.debug(f"Retrieved memory item from long-term: {category}/{key}")
                return value
            else:
                logger.debug(f"Memory item not found: {category}/{key}")
                return None
        except Exception as e:
            logger.error(f"Failed to retrieve memory item {category}/{key}: {str(e)}")
            return None
    
    def search(self, category: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search for memory items matching a query.
        
        Args:
            category: Category to search in
            query: Query parameters
            
        Returns:
            List of matching memory items
        """
        results = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Build the query
            sql = "SELECT * FROM memory_items WHERE category = ?"
            params = [category]
            
            for key, value in query.items():
                if key == "metadata":
                    # Search in metadata JSON
                    for meta_key, meta_value in value.items():
                        sql += f" AND json_extract(metadata, '$.{meta_key}') = ?"
                        params.append(meta_value)
                else:
                    # Regular field search
                    sql += f" AND {key} = ?"
                    params.append(value)
            
            cursor.execute(sql, params)
            
            for row in cursor.fetchall():
                results.append({
                    "category": row["category"],
                    "key": row["key"],
                    "value": json.loads(row["value"]),
                    "metadata": json.loads(row["metadata"]),
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                })
            
            conn.close()
            
            logger.debug(f"Found {len(results)} items matching query in {category}")
            return results
        except Exception as e:
            logger.error(f"Failed to search memory: {str(e)}")
            return []
    
    def record_interaction(self, entity_id: str, entity_type: str, platform: str,
                          interaction_type: str, content: Any = None,
                          metadata: Dict[str, Any] = None) -> bool:
        """
        Record an interaction with an entity.
        
        Args:
            entity_id: ID of the entity (user, post, etc.)
            entity_type: Type of entity (user, post, comment, etc.)
            platform: Platform where the interaction occurred
            interaction_type: Type of interaction (like, comment, follow, etc.)
            content: Content of the interaction
            metadata: Additional metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Convert content and metadata to JSON strings
            content_json = json.dumps(content) if content is not None else None
            metadata_json = json.dumps(metadata or {})
            
            # Insert the interaction
            cursor.execute('''
            INSERT INTO interactions 
            (entity_id, entity_type, platform, interaction_type, content, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (entity_id, entity_type, platform, interaction_type, content_json, metadata_json))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Recorded interaction: {interaction_type} with {entity_type} {entity_id} on {platform}")
            return True
        except Exception as e:
            logger.error(f"Failed to record interaction: {str(e)}")
            return False
    
    def get_interactions(self, entity_id: str = None, entity_type: str = None,
                        platform: str = None, interaction_type: str = None,
                        limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recorded interactions matching the criteria.
        
        Args:
            entity_id: Filter by entity ID
            entity_type: Filter by entity type
            platform: Filter by platform
            interaction_type: Filter by interaction type
            limit: Maximum number of results
            
        Returns:
            List of matching interactions
        """
        results = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Build the query
            sql = "SELECT * FROM interactions WHERE 1=1"
            params = []
            
            if entity_id:
                sql += " AND entity_id = ?"
                params.append(entity_id)
            
            if entity_type:
                sql += " AND entity_type = ?"
                params.append(entity_type)
            
            if platform:
                sql += " AND platform = ?"
                params.append(platform)
            
            if interaction_type:
                sql += " AND interaction_type = ?"
                params.append(interaction_type)
            
            sql += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(sql, params)
            
            for row in cursor.fetchall():
                content = json.loads(row["content"]) if row["content"] else None
                metadata = json.loads(row["metadata"]) if row["metadata"] else {}
                
                results.append({
                    "id": row["id"],
                    "entity_id": row["entity_id"],
                    "entity_type": row["entity_type"],
                    "platform": row["platform"],
                    "interaction_type": row["interaction_type"],
                    "content": content,
                    "metadata": metadata,
                    "timestamp": row["timestamp"]
                })
            
            conn.close()
            
            logger.debug(f"Found {len(results)} matching interactions")
            return results
        except Exception as e:
            logger.error(f"Failed to get interactions: {str(e)}")
            return []
    
    def clear_short_term(self):
        """Clear the short-term memory cache."""
        self.short_term = {}
        logger.info("Short-term memory cleared")
    
    def backup(self, backup_path: str = None) -> bool:
        """
        Create a backup of the memory database.
        
        Args:
            backup_path: Path to store the backup
            
        Returns:
            True if successful, False otherwise
        """
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(self.memory_path, f"memory_backup_{timestamp}.db")
        
        try:
            # Create a backup using SQLite's backup API
            conn = sqlite3.connect(self.db_path)
            backup_conn = sqlite3.connect(backup_path)
            
            conn.backup(backup_conn)
            
            conn.close()
            backup_conn.close()
            
            logger.info(f"Memory backup created at {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create memory backup: {str(e)}")
            return False