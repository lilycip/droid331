"""
Image Generator Module - Generates images using diffusion models.
"""
import logging
import os
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ImageGenerator:
    """
    Module for generating images using diffusion models.
    """
    
    def __init__(self, config: Dict[str, Any], model_manager: Any, memory: Any):
        """
        Initialize the ImageGenerator module.
        
        Args:
            config: Module configuration
            model_manager: Model manager instance
            memory: Memory system instance
        """
        self.config = config
        self.model_manager = model_manager
        self.memory = memory
        
        # Default model for image generation
        self.default_model = config.get("default_model", "stable-diffusion-xl")
        
        # Output directory for generated images
        self.output_dir = config.get("output_dir", "data/generated/images")
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info("ImageGenerator module initialized")
    
    def generate(self, params: Dict[str, Any]) -> Dict[str, Any]:
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
        model_name = params.get("model", self.default_model)
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
    
    def enhance_prompt(self, prompt: str) -> str:
        """
        Enhance a prompt for better image generation results.
        
        Args:
            prompt: Original prompt
            
        Returns:
            Enhanced prompt
        """
        try:
            # Use an LLM to enhance the prompt
            enhancement_prompt = f"Enhance the following prompt for image generation, adding details about lighting, style, and composition: '{prompt}'"
            
            result = self.model_manager.run_model(
                "llama-3.1",  # Use LLM for prompt enhancement
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