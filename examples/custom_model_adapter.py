#!/usr/bin/env python3
"""
Example of creating and using a custom model adapter with the Droid agent.
"""
import os
import sys
import json
import argparse
import logging
import random
from droid.core.agent import Agent
from droid.core.model_manager import ModelManager
from droid.utils.logger import setup_logging

class CustomModelAdapter:
    """A custom model adapter for the Droid agent."""
    
    def __init__(self, config=None):
        """Initialize the custom model adapter."""
        self.config = config or {}
        self.name = self.config.get("name", "Custom Model")
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initializing {self.name}")
        
        # Model parameters
        self.temperature = self.config.get("temperature", 0.7)
        self.max_tokens = self.config.get("max_tokens", 100)
        self.creativity = self.config.get("creativity", 0.5)
        self.knowledge = self.config.get("knowledge", ["general", "tech", "science"])
        
        # Load the model (in a real adapter, this would load the actual model)
        self.logger.info(f"Loading model with temperature={self.temperature}, creativity={self.creativity}")
        self.logger.info(f"Model knowledge areas: {', '.join(self.knowledge)}")
    
    def generate_text(self, prompt, max_tokens=None, temperature=None):
        """Generate text with the model."""
        max_tokens = max_tokens or self.max_tokens
        temperature = temperature or self.temperature
        
        self.logger.info(f"Generating text with prompt: {prompt[:50]}...")
        
        # In a real adapter, this would call the actual model
        # For this example, we'll generate some placeholder text
        words = ["AI", "agent", "model", "custom", "adapter", "Droid", "generate", "text", "image", 
                "content", "social", "media", "module", "system", "task", "schedule", "memory",
                "configuration", "parameter", "function", "method", "class", "object", "instance"]
        
        # Generate a response based on the prompt and parameters
        response_length = min(max_tokens, 200)
        response_words = []
        
        # Add some words from the prompt to make it seem more relevant
        prompt_words = prompt.split()
        for _ in range(min(5, len(prompt_words))):
            response_words.append(random.choice(prompt_words))
        
        # Add random words to complete the response
        for _ in range(response_length - len(response_words)):
            response_words.append(random.choice(words))
        
        # Shuffle the words a bit to make it less repetitive
        random.shuffle(response_words)
        
        # Create sentences
        sentences = []
        sentence_words = []
        
        for word in response_words:
            sentence_words.append(word)
            
            # End the sentence with a probability based on temperature
            if len(sentence_words) > 5 and random.random() < (0.1 * temperature):
                sentences.append(" ".join(sentence_words) + ".")
                sentence_words = []
        
        # Add any remaining words as the last sentence
        if sentence_words:
            sentences.append(" ".join(sentence_words) + ".")
        
        # Join sentences into a paragraph
        response = " ".join(sentences)
        
        self.logger.info(f"Generated {len(response)} characters")
        return response
    
    def generate_image(self, prompt, width=512, height=512, num_inference_steps=30):
        """Generate an image with the model."""
        self.logger.info(f"Generating image with prompt: {prompt}")
        
        # In a real adapter, this would call the actual model
        # For this example, we'll return a placeholder
        
        # Create a simple JSON representation of what the image would be
        image_data = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "steps": num_inference_steps,
            "filepath": "/tmp/generated_image.png",
            "generation_time": "0.5 seconds"
        }
        
        self.logger.info(f"Generated image with dimensions {width}x{height}")
        return image_data
    
    def embed_text(self, text):
        """Generate embeddings for text."""
        self.logger.info(f"Generating embeddings for text: {text[:50]}...")
        
        # In a real adapter, this would call the actual model
        # For this example, we'll generate random embeddings
        embedding_size = 128
        embeddings = [random.random() for _ in range(embedding_size)]
        
        self.logger.info(f"Generated embeddings with dimension {embedding_size}")
        return embeddings
    
    def classify_text(self, text, categories):
        """Classify text into categories."""
        self.logger.info(f"Classifying text: {text[:50]}...")
        
        # In a real adapter, this would call the actual model
        # For this example, we'll generate random classifications
        classifications = {}
        total = 0.0
        
        for category in categories:
            score = random.random()
            classifications[category] = score
            total += score
        
        # Normalize to sum to 1.0
        for category in classifications:
            classifications[category] /= total
        
        self.logger.info(f"Classified text into {len(categories)} categories")
        return classifications

class CustomModelManager(ModelManager):
    """A custom model manager for the Droid agent."""
    
    def __init__(self, config=None):
        """Initialize the custom model manager."""
        super().__init__(config)
        self.logger.info("Initializing CustomModelManager")
        
        # Register the custom model adapter
        self.register_adapter("custom", CustomModelAdapter)
    
    def register_adapter(self, model_type, adapter_class):
        """Register a model adapter."""
        self.adapters[model_type] = adapter_class
        self.logger.info(f"Registered adapter for model type: {model_type}")

def main():
    """Run the agent with a custom model adapter."""
    parser = argparse.ArgumentParser(description="Run the Droid agent with a custom model adapter")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = "DEBUG" if args.debug else "INFO"
    setup_logging({"level": log_level})
    logger = logging.getLogger(__name__)
    
    # Create the custom model manager
    model_manager = CustomModelManager()
    
    # Create a custom model configuration
    model_config = {
        "name": "My Custom Model",
        "temperature": 0.8,
        "max_tokens": 150,
        "creativity": 0.7,
        "knowledge": ["general", "tech", "science", "art"]
    }
    
    # Load the custom model
    model = model_manager.load_model("custom", model_config)
    
    # Create the agent with the custom model manager
    agent = Agent()
    agent.model_manager = model_manager
    
    logger.info("Agent initialized with custom model adapter")
    
    # Run in interactive mode
    if args.interactive:
        print("Droid AI Agent with Custom Model - Interactive Mode")
        print("Type 'exit' to quit")
        print("Type 'help' for a list of commands")
        
        while True:
            try:
                command = input("\nModel> ")
                
                if command.lower() == "exit":
                    break
                
                if command.lower() == "help":
                    print("\nAvailable commands:")
                    print("  text <prompt>                      - Generate text")
                    print("  image <prompt> [width] [height]    - Generate an image")
                    print("  embed <text>                       - Generate embeddings for text")
                    print("  classify <text> <categories>       - Classify text into categories")
                    print("  exit                               - Exit the program")
                    print("  help                               - Show this help message")
                    continue
                
                if command.lower().startswith("text "):
                    prompt = command[5:]
                    response = model.generate_text(prompt)
                    print(f"\nGenerated text:\n{response}")
                    continue
                
                if command.lower().startswith("image "):
                    parts = command.split(" ", 3)
                    prompt = parts[1]
                    width = int(parts[2]) if len(parts) > 2 else 512
                    height = int(parts[3]) if len(parts) > 3 else 512
                    
                    result = model.generate_image(prompt, width, height)
                    print(f"\nImage generation result:")
                    print(json.dumps(result, indent=2))
                    continue
                
                if command.lower().startswith("embed "):
                    text = command[6:]
                    embeddings = model.embed_text(text)
                    print(f"\nGenerated embeddings (first 10):")
                    print(embeddings[:10])
                    print(f"Total dimensions: {len(embeddings)}")
                    continue
                
                if command.lower().startswith("classify "):
                    parts = command.split(" ", 2)
                    if len(parts) < 3:
                        print("Error: Missing text or categories")
                        print("Usage: classify <text> <categories>")
                        continue
                    
                    text = parts[1]
                    
                    try:
                        categories = json.loads(parts[2])
                    except json.JSONDecodeError:
                        print(f"Error: Invalid JSON categories: {parts[2]}")
                        continue
                    
                    if not isinstance(categories, list):
                        print("Error: Categories must be a JSON array")
                        continue
                    
                    result = model.classify_text(text, categories)
                    print(f"\nClassification results:")
                    for category, score in sorted(result.items(), key=lambda x: x[1], reverse=True):
                        print(f"  {category}: {score:.4f}")
                    continue
                
                print(f"Unknown command: {command}")
                
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {str(e)}")
        
        return
    
    # Run some example commands
    print("Running example commands with custom model:")
    
    print("\n1. Generate text:")
    prompt = "Explain how AI agents can help with social media management"
    response = model.generate_text(prompt)
    print(f"Prompt: {prompt}")
    print(f"Response: {response}")
    
    print("\n2. Generate an image:")
    prompt = "A futuristic AI assistant helping with social media"
    result = model.generate_image(prompt)
    print(f"Prompt: {prompt}")
    print(f"Result: {json.dumps(result, indent=2)}")
    
    print("\n3. Generate embeddings:")
    text = "AI agents are revolutionizing how we interact with technology"
    embeddings = model.embed_text(text)
    print(f"Text: {text}")
    print(f"Embeddings (first 10): {embeddings[:10]}")
    print(f"Total dimensions: {len(embeddings)}")
    
    print("\n4. Classify text:")
    text = "The new AI model can generate images and text with remarkable quality"
    categories = ["technology", "art", "science", "business", "entertainment"]
    result = model.classify_text(text, categories)
    print(f"Text: {text}")
    print(f"Categories: {categories}")
    print(f"Classification results:")
    for category, score in sorted(result.items(), key=lambda x: x[1], reverse=True):
        print(f"  {category}: {score:.4f}")

if __name__ == "__main__":
    main()