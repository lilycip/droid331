"""
Comment Reply Module - Handles replying to comments on social media.
"""
import logging
import random
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class CommentReply:
    """
    Module for replying to comments on social media.
    """
    
    def __init__(self, config: Dict[str, Any], model_manager: Any, memory: Any):
        """
        Initialize the CommentReply module.
        
        Args:
            config: Module configuration
            model_manager: Model manager instance
            memory: Memory system instance
        """
        self.config = config
        self.model_manager = model_manager
        self.memory = memory
        
        # Platform-specific clients
        self.clients = {}
        
        # Default model for generating responses
        self.default_model = config.get("default_model", "llama-3.1")
        
        # Initialize platform clients
        self._init_clients()
        
        logger.info("CommentReply module initialized")
    
    def _init_clients(self):
        """Initialize clients for configured platforms."""
        platforms = self.config.get("platforms", ["twitter", "instagram", "facebook"])
        
        for platform in platforms:
            try:
                platform_config = self.config.get(platform, {})
                
                if platform == "twitter":
                    self.clients[platform] = self._init_twitter_client(platform_config)
                elif platform == "instagram":
                    self.clients[platform] = self._init_instagram_client(platform_config)
                elif platform == "facebook":
                    self.clients[platform] = self._init_facebook_client(platform_config)
                else:
                    logger.warning(f"Unknown platform: {platform}")
                    
                if platform in self.clients:
                    logger.info(f"Initialized client for {platform}")
            except Exception as e:
                logger.error(f"Failed to initialize client for {platform}: {str(e)}")
    
    def _init_twitter_client(self, config: Dict[str, Any]) -> Any:
        """Initialize Twitter client."""
        # This is a placeholder - in a real implementation, you would use the Twitter API
        return {"name": "twitter_client", "config": config}
    
    def _init_instagram_client(self, config: Dict[str, Any]) -> Any:
        """Initialize Instagram client."""
        # This is a placeholder - in a real implementation, you would use the Instagram API
        return {"name": "instagram_client", "config": config}
    
    def _init_facebook_client(self, config: Dict[str, Any]) -> Any:
        """Initialize Facebook client."""
        # This is a placeholder - in a real implementation, you would use the Facebook API
        return {"name": "facebook_client", "config": config}
    
    def reply_to_comment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reply to a comment on a social media platform.
        
        Args:
            params: Parameters for the reply
                - platform: Platform where the comment is
                - comment_id: ID of the comment to reply to
                - post_id: ID of the post containing the comment
                - content: Content of the reply (optional, will be generated if not provided)
                - tone: Tone for the reply (optional)
                
        Returns:
            Result of the reply operation
        """
        platform = params.get("platform", "twitter")
        comment_id = params.get("comment_id")
        post_id = params.get("post_id")
        content = params.get("content")
        tone = params.get("tone", "friendly")
        
        if not comment_id:
            logger.error("No comment_id provided")
            return {"success": False, "error": "No comment_id provided"}
        
        if platform not in self.clients:
            logger.error(f"No client available for platform: {platform}")
            return {"success": False, "error": f"Platform {platform} not configured"}
        
        client = self.clients[platform]
        
        try:
            # Get the comment content
            comment_content = self._get_comment_content(platform, comment_id, post_id)
            
            if not comment_content:
                logger.error(f"Failed to get content for comment {comment_id}")
                return {"success": False, "error": "Failed to get comment content"}
            
            # Generate reply content if not provided
            if not content:
                content = self._generate_reply(platform, comment_id, comment_content, tone)
            
            # Platform-specific reply logic
            if platform == "twitter":
                result = self._reply_on_twitter(client, comment_id, post_id, content)
            elif platform == "instagram":
                result = self._reply_on_instagram(client, comment_id, post_id, content)
            elif platform == "facebook":
                result = self._reply_on_facebook(client, comment_id, post_id, content)
            else:
                logger.error(f"Replying on {platform} not implemented")
                return {"success": False, "error": f"Replying on {platform} not implemented"}
            
            # Record the interaction in memory
            if result.get("success"):
                self.memory.record_interaction(
                    entity_id=comment_id,
                    entity_type="comment",
                    platform=platform,
                    interaction_type="reply",
                    content=content,
                    metadata={
                        "post_id": post_id,
                        "original_comment": comment_content,
                        "result": result
                    }
                )
            
            return result
        except Exception as e:
            logger.error(f"Error replying to comment {comment_id} on {platform}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _reply_on_twitter(self, client: Any, comment_id: str, post_id: str, content: str) -> Dict[str, Any]:
        """Reply to a comment on Twitter."""
        # This is a placeholder - in a real implementation, you would use the Twitter API
        logger.info(f"Would reply to comment {comment_id} on Twitter: {content[:50]}...")
        return {"success": True, "reply_id": f"twitter_reply_{random.randint(1000, 9999)}", "platform": "twitter"}
    
    def _reply_on_instagram(self, client: Any, comment_id: str, post_id: str, content: str) -> Dict[str, Any]:
        """Reply to a comment on Instagram."""
        # This is a placeholder - in a real implementation, you would use the Instagram API
        logger.info(f"Would reply to comment {comment_id} on Instagram: {content[:50]}...")
        return {"success": True, "reply_id": f"instagram_reply_{random.randint(1000, 9999)}", "platform": "instagram"}
    
    def _reply_on_facebook(self, client: Any, comment_id: str, post_id: str, content: str) -> Dict[str, Any]:
        """Reply to a comment on Facebook."""
        # This is a placeholder - in a real implementation, you would use the Facebook API
        logger.info(f"Would reply to comment {comment_id} on Facebook: {content[:50]}...")
        return {"success": True, "reply_id": f"facebook_reply_{random.randint(1000, 9999)}", "platform": "facebook"}
    
    def _get_comment_content(self, platform: str, comment_id: str, post_id: Optional[str]) -> Optional[str]:
        """
        Get the content of a comment.
        
        Args:
            platform: Platform of the comment
            comment_id: ID of the comment
            post_id: ID of the post containing the comment
            
        Returns:
            Comment content if available, None otherwise
        """
        # This is a placeholder - in a real implementation, you would fetch the comment content
        # from the appropriate platform API
        return f"Example comment content for comment {comment_id} on post {post_id} on {platform}"
    
    def _generate_reply(self, platform: str, comment_id: str, comment_content: str, tone: str) -> str:
        """
        Generate a reply to a comment using an LLM.
        
        Args:
            platform: Platform of the comment
            comment_id: ID of the comment
            comment_content: Content of the comment
            tone: Tone for the reply
            
        Returns:
            Generated reply
        """
        # Get previous interactions with this comment
        previous_interactions = self.memory.get_interactions(
            entity_id=comment_id,
            entity_type="comment",
            platform=platform,
            limit=5
        )
        
        # Create a prompt for the LLM
        prompt = f"Generate a {tone} reply to the following comment on {platform}:\n\n"
        prompt += f"Comment: {comment_content}\n\n"
        
        if previous_interactions:
            prompt += "Previous interactions with this comment:\n"
            for interaction in previous_interactions:
                prompt += f"- {interaction['interaction_type']}: {interaction.get('content', '')}\n"
            prompt += "\n"
        
        prompt += f"The reply should be {tone}, relevant to the comment, and not overly promotional. "
        prompt += "It should sound natural and conversational, as if written by a real person. "
        prompt += "Keep it concise (1-2 sentences) and include an appropriate emoji if relevant."
        
        try:
            # Run the model
            result = self.model_manager.run_model(
                self.default_model,
                prompt,
                max_tokens=256,
                temperature=0.7
            )
            
            if not result or not isinstance(result, str):
                logger.error("Failed to generate reply")
                return "Thanks for your comment! 👍"
            
            # Clean up the result
            reply = result.strip()
            
            # Remove any quotation marks that might be around the reply
            if reply.startswith('"') and reply.endswith('"'):
                reply = reply[1:-1]
            
            logger.info(f"Generated reply: {reply}")
            return reply
        except Exception as e:
            logger.error(f"Error generating reply: {str(e)}")
            return "Thanks for your comment! 👍"
    
    def get_comments(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get comments from a post.
        
        Args:
            params: Parameters for the query
                - platform: Platform to query
                - post_id: ID of the post
                - count: Number of comments to retrieve
                - include_replies: Whether to include replies to comments
                
        Returns:
            List of comments
        """
        platform = params.get("platform", "twitter")
        post_id = params.get("post_id")
        count = params.get("count", 10)
        include_replies = params.get("include_replies", False)
        
        if not post_id:
            logger.error("No post_id provided")
            return []
        
        if platform not in self.clients:
            logger.error(f"No client available for platform: {platform}")
            return []
        
        client = self.clients[platform]
        
        try:
            # Platform-specific logic to get comments
            if platform == "twitter":
                return self._get_twitter_comments(client, post_id, count, include_replies)
            elif platform == "instagram":
                return self._get_instagram_comments(client, post_id, count, include_replies)
            elif platform == "facebook":
                return self._get_facebook_comments(client, post_id, count, include_replies)
            else:
                logger.error(f"Getting comments from {platform} not implemented")
                return []
        except Exception as e:
            logger.error(f"Error getting comments from post {post_id} on {platform}: {str(e)}")
            return []
    
    def _get_twitter_comments(self, client: Any, post_id: str, count: int, include_replies: bool) -> List[Dict[str, Any]]:
        """Get comments from a Twitter post."""
        # This is a placeholder - in a real implementation, you would use the Twitter API
        logger.info(f"Would get {count} comments from Twitter post {post_id}")
        return [
            {
                "id": f"twitter_comment_{i}",
                "content": f"Example Twitter comment {i} on post {post_id}",
                "user_id": f"twitter_user_{i}",
                "username": f"user{i}",
                "platform": "twitter",
                "post_id": post_id,
                "created_at": "2023-01-01T00:00:00Z",
                "replies": [] if not include_replies else [
                    {
                        "id": f"twitter_reply_{i}_{j}",
                        "content": f"Example Twitter reply {j} to comment {i}",
                        "user_id": f"twitter_user_{j}",
                        "username": f"user{j}",
                        "platform": "twitter",
                        "created_at": "2023-01-01T00:00:00Z"
                    }
                    for j in range(2)
                ]
            }
            for i in range(count)
        ]
    
    def _get_instagram_comments(self, client: Any, post_id: str, count: int, include_replies: bool) -> List[Dict[str, Any]]:
        """Get comments from an Instagram post."""
        # This is a placeholder - in a real implementation, you would use the Instagram API
        logger.info(f"Would get {count} comments from Instagram post {post_id}")
        return [
            {
                "id": f"instagram_comment_{i}",
                "content": f"Example Instagram comment {i} on post {post_id}",
                "user_id": f"instagram_user_{i}",
                "username": f"user{i}",
                "platform": "instagram",
                "post_id": post_id,
                "created_at": "2023-01-01T00:00:00Z",
                "replies": [] if not include_replies else [
                    {
                        "id": f"instagram_reply_{i}_{j}",
                        "content": f"Example Instagram reply {j} to comment {i}",
                        "user_id": f"instagram_user_{j}",
                        "username": f"user{j}",
                        "platform": "instagram",
                        "created_at": "2023-01-01T00:00:00Z"
                    }
                    for j in range(2)
                ]
            }
            for i in range(count)
        ]
    
    def _get_facebook_comments(self, client: Any, post_id: str, count: int, include_replies: bool) -> List[Dict[str, Any]]:
        """Get comments from a Facebook post."""
        # This is a placeholder - in a real implementation, you would use the Facebook API
        logger.info(f"Would get {count} comments from Facebook post {post_id}")
        return [
            {
                "id": f"facebook_comment_{i}",
                "content": f"Example Facebook comment {i} on post {post_id}",
                "user_id": f"facebook_user_{i}",
                "username": f"user{i}",
                "platform": "facebook",
                "post_id": post_id,
                "created_at": "2023-01-01T00:00:00Z",
                "replies": [] if not include_replies else [
                    {
                        "id": f"facebook_reply_{i}_{j}",
                        "content": f"Example Facebook reply {j} to comment {i}",
                        "user_id": f"facebook_user_{j}",
                        "username": f"user{j}",
                        "platform": "facebook",
                        "created_at": "2023-01-01T00:00:00Z"
                    }
                    for j in range(2)
                ]
            }
            for i in range(count)
        ]