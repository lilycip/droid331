#!/usr/bin/env python3
"""
Web interface for the Droid agent.
"""
import os
import sys
import json
import logging
from flask import Flask, request, jsonify, render_template, send_from_directory

# Add the parent directory to the path so we can import the droid package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from droid.core.agent import Agent
from droid.utils.logger import setup_logging

# Set up logging
setup_logging({"level": "INFO"})
logger = logging.getLogger(__name__)

# Create the Flask app
app = Flask(__name__)

# Create the agent
agent = Agent("config/config.yaml")

@app.route('/')
def index():
    """Render the index page."""
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    """Generate content."""
    try:
        data = request.json
        content_type = data.get('content_type', 'text')
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({"success": False, "error": "No prompt provided"}), 400
        
        params = {
            "content_type": content_type,
            "prompt": prompt
        }
        
        # Add additional parameters based on content type
        if content_type == 'text':
            params['max_tokens'] = data.get('max_tokens', 512)
            params['temperature'] = data.get('temperature', 0.7)
        elif content_type == 'image':
            params['width'] = data.get('width', 512)
            params['height'] = data.get('height', 512)
            params['negative_prompt'] = data.get('negative_prompt', '')
        elif content_type == 'meme':
            params['topic'] = data.get('topic', prompt)
            params['style'] = data.get('style', 'funny')
            params['template'] = data.get('template', 'default')
        
        # Execute the task
        result = agent.execute_task("generate_content", params)
        
        if not result:
            return jsonify({"success": False, "error": "Failed to generate content"}), 500
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/post', methods=['POST'])
def post():
    """Post content to social media."""
    try:
        data = request.json
        platform = data.get('platform', 'twitter')
        content = data.get('content', '')
        
        if not content:
            return jsonify({"success": False, "error": "No content provided"}), 400
        
        params = {
            "platform": platform,
            "content_type": "text",
            "content": content
        }
        
        # Add media if provided
        if 'media_urls' in data:
            params['media_urls'] = data['media_urls']
        
        # Execute the task
        result = agent.execute_task("post_content", params)
        
        if not result:
            return jsonify({"success": False, "error": "Failed to post content"}), 500
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error posting content: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/interact', methods=['POST'])
def interact():
    """Interact with an influencer."""
    try:
        data = request.json
        platform = data.get('platform', 'twitter')
        influencer_id = data.get('influencer_id', '')
        
        if not influencer_id:
            return jsonify({"success": False, "error": "No influencer_id provided"}), 400
        
        params = {
            "platform": platform,
            "influencer_id": influencer_id,
            "interaction_type": data.get('interaction_type', 'follow')
        }
        
        # Add message if provided
        if 'message' in data:
            params['message'] = data['message']
        
        # Execute the task
        result = agent.execute_task("interact_with_influencer", params)
        
        if not result:
            return jsonify({"success": False, "error": "Failed to interact with influencer"}), 500
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error interacting with influencer: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/reply', methods=['POST'])
def reply():
    """Reply to a comment."""
    try:
        data = request.json
        platform = data.get('platform', 'twitter')
        comment_id = data.get('comment_id', '')
        content = data.get('content', '')
        
        if not comment_id:
            return jsonify({"success": False, "error": "No comment_id provided"}), 400
        
        if not content:
            return jsonify({"success": False, "error": "No content provided"}), 400
        
        params = {
            "platform": platform,
            "comment_id": comment_id,
            "content": content
        }
        
        # Execute the task
        result = agent.execute_task("reply_to_comment", params)
        
        if not result:
            return jsonify({"success": False, "error": "Failed to reply to comment"}), 500
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error replying to comment: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/generated/<path:filename>')
def generated_file(filename):
    """Serve generated files."""
    return send_from_directory('data/generated', filename)

def main():
    """Run the web interface."""
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 12000))
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=True)

if __name__ == '__main__':
    main()