"""
Content Generator Module - Generates various types of content using AI models.
"""
import logging
import os
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class ContentGenerator:
    """
    Module for generating content using AI models.
    """
    
    def __init__(self, config: Dict[str, Any], model_manager: Any, memory: Any):
        """
        Initialize the ContentGenerator module.
        
        Args:
            config: Module configuration
            model_manager: Model manager instance
            memory: Memory system instance
        """
        self.config = config
        self.model_manager = model_manager
        self.memory = memory
        
        # Default models for different content types
        self.default_text_model = config.get("default_model", "llama-3.1")
        self.default_image_model = config.get("default_image_model", "stable-diffusion-xl")
        
        # Output directory for generated content
        self.output_dir = config.get("output_dir", "data/generated")
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info("ContentGenerator module initialized")
    
    def generate_text(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate text content using an LLM.
        
        Args:
            params: Parameters for text generation
                - prompt: Text prompt
                - model: Model to use (optional)
                - max_tokens: Maximum tokens to generate (optional)
                - temperature: Temperature for generation (optional)
                
        Returns:
            Generated text content
        """
        prompt = params.get("prompt", "")
        model_name = params.get("model", self.default_text_model)
        max_tokens = params.get("max_tokens", 1024)
        temperature = params.get("temperature", 0.7)
        
        if not prompt:
            logger.error("No prompt provided for text generation")
            return {"success": False, "error": "No prompt provided"}
        
        try:
            # Run the model
            model_params = {
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            result = self.model_manager.run_model(model_name, prompt, **model_params)
            
            if not result:
                logger.error(f"Failed to generate text with model {model_name}")
                return {"success": False, "error": f"Failed to generate text with model {model_name}"}
            
            # Store the generated content in memory
            content_id = f"text_{hash(prompt)}"
            self.memory.store(
                category="generated_content",
                key=content_id,
                value=result,
                metadata={
                    "type": "text",
                    "prompt": prompt,
                    "model": model_name,
                    "params": model_params
                }
            )
            
            return {
                "success": True,
                "content_id": content_id,
                "text": result,
                "model": model_name
            }
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def generate_image(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate an image using a diffusion model.
        
        Args:
            params: Parameters for image generation
                - prompt: Text prompt
                - model: Model to use (optional)
                - negative_prompt: Negative prompt (optional)
                - width: Image width (optional)
                - height: Image height (optional)
                - guidance_scale: Guidance scale (optional)
                - num_inference_steps: Number of inference steps (optional)
                
        Returns:
            Generated image information
        """
        prompt = params.get("prompt", "")
        model_name = params.get("model", self.default_image_model)
        negative_prompt = params.get("negative_prompt", "")
        width = params.get("width", 512)
        height = params.get("height", 512)
        guidance_scale = params.get("guidance_scale", 7.5)
        num_inference_steps = params.get("num_inference_steps", 50)
        
        if not prompt:
            logger.error("No prompt provided for image generation")
            return {"success": False, "error": "No prompt provided"}
        
        try:
            # Run the model
            model_params = {
                "negative_prompt": negative_prompt,
                "width": width,
                "height": height,
                "guidance_scale": guidance_scale,
                "num_inference_steps": num_inference_steps
            }
            
            result = self.model_manager.run_model(model_name, prompt, **model_params)
            
            if not result:
                logger.error(f"Failed to generate image with model {model_name}")
                return {"success": False, "error": f"Failed to generate image with model {model_name}"}
            
            # Save the image to disk
            content_id = f"image_{hash(prompt)}"
            filename = f"{content_id}.png"
            filepath = os.path.join(self.output_dir, filename)
            
            # In a real implementation, you would save the image here
            # For example: result["image_data"].save(filepath)
            
            # Store the generated content in memory
            self.memory.store(
                category="generated_content",
                key=content_id,
                value={
                    "filepath": filepath,
                    "prompt": prompt
                },
                metadata={
                    "type": "image",
                    "prompt": prompt,
                    "model": model_name,
                    "params": model_params
                }
            )
            
            return {
                "success": True,
                "content_id": content_id,
                "filepath": filepath,
                "model": model_name
            }
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def generate_content(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate content based on the specified type.
        
        Args:
            params: Parameters for content generation
                - content_type: Type of content to generate (text, image)
                - prompt: Text prompt
                - model: Model to use (optional)
                - additional parameters based on content type
                
        Returns:
            Generated content information
        """
        content_type = params.get("content_type", "text")
        
        if content_type == "text":
            return self.generate_text(params)
        elif content_type == "image":
            return self.generate_image(params)
        else:
            logger.error(f"Unsupported content type: {content_type}")
            return {"success": False, "error": f"Unsupported content type: {content_type}"}
    
    def enhance_prompt(self, prompt: str, content_type: str = "text") -> str:
        """
        Enhance a user prompt to get better generation results.
        
        Args:
            prompt: Original prompt
            content_type: Type of content (text, image)
            
        Returns:
            Enhanced prompt
        """
        try:
            # Use an LLM to enhance the prompt
            if content_type == "text":
                enhancement_prompt = f"Enhance the following prompt for text generation: '{prompt}'"
            elif content_type == "image":
                enhancement_prompt = f"Enhance the following prompt for image generation, adding details about lighting, style, and composition: '{prompt}'"
            else:
                return prompt
            
            result = self.model_manager.run_model(
                self.default_text_model, 
                enhancement_prompt,
                max_tokens=512,
                temperature=0.7
            )
            
            if result and isinstance(result, str):
                enhanced_prompt = result.strip()
                logger.info(f"Enhanced prompt: {enhanced_prompt[:50]}...")
                return enhanced_prompt
            else:
                return prompt
        except Exception as e:
            logger.error(f"Error enhancing prompt: {str(e)}")
            return prompt