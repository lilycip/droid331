"""
Meme Generator Module - Creates memes by combining templates with generated text.
"""
import logging
import os
import json
import random
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class MemeGenerator:
    """
    Module for generating memes using templates and AI-generated text.
    """
    
    def __init__(self, config: Dict[str, Any], model_manager: Any, memory: Any):
        """
        Initialize the MemeGenerator module.
        
        Args:
            config: Module configuration
            model_manager: Model manager instance
            memory: Memory system instance
        """
        self.config = config
        self.model_manager = model_manager
        self.memory = memory
        
        # Templates directory
        self.templates_path = config.get("templates_path", "data/meme_templates")
        os.makedirs(self.templates_path, exist_ok=True)
        
        # Output directory for generated memes
        self.output_dir = config.get("output_dir", "data/generated/memes")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Default model for text generation
        self.default_text_model = config.get("default_model", "llama-3.1")
        
        # Load available templates
        self.templates = self._load_templates()
        
        logger.info(f"MemeGenerator module initialized with {len(self.templates)} templates")
    
    def _load_templates(self) -> Dict[str, Any]:
        """Load meme templates from the templates directory."""
        templates = {}
        
        # Check for templates.json file
        templates_json = os.path.join(self.templates_path, "templates.json")
        if os.path.exists(templates_json):
            try:
                with open(templates_json, 'r') as f:
                    templates = json.load(f)
                logger.info(f"Loaded {len(templates)} templates from {templates_json}")
                return templates
            except Exception as e:
                logger.error(f"Error loading templates from {templates_json}: {str(e)}")
        
        # If no templates.json, scan the directory for image files
        try:
            for filename in os.listdir(self.templates_path):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    template_name = os.path.splitext(filename)[0]
                    templates[template_name] = {
                        "name": template_name,
                        "file": filename,
                        "path": os.path.join(self.templates_path, filename),
                        "text_regions": [
                            {"x": 0, "y": 0, "width": 1.0, "height": 0.3, "align": "center"},
                            {"x": 0, "y": 0.7, "width": 1.0, "height": 0.3, "align": "center"}
                        ]
                    }
            
            # Save the templates to templates.json for future use
            if templates:
                with open(templates_json, 'w') as f:
                    json.dump(templates, f, indent=2)
                
            logger.info(f"Scanned and found {len(templates)} templates in {self.templates_path}")
            return templates
        except Exception as e:
            logger.error(f"Error scanning templates directory: {str(e)}")
            return {}
    
    def generate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a meme.
        
        Args:
            params: Parameters for meme generation
                - template: Template name (optional, random if not specified)
                - topic: Topic for the meme (optional)
                - text: List of text strings for the template (optional)
                - style: Style of humor (optional)
                
        Returns:
            Generated meme information
        """
        template_name = params.get("template")
        topic = params.get("topic", "")
        text_list = params.get("text", [])
        style = params.get("style", "funny")
        
        # Select a template
        template = self._select_template(template_name)
        if not template:
            logger.error("No template available for meme generation")
            return {"success": False, "error": "No template available"}
        
        try:
            # Generate text if not provided
            if not text_list:
                text_list = self._generate_meme_text(template, topic, style)
            
            # Create the meme
            meme_id = f"meme_{hash(str(template_name) + str(text_list))}"
            filename = f"{meme_id}.png"
            filepath = os.path.join(self.output_dir, filename)
            
            # In a real implementation, you would create the image here
            # For example:
            # self._create_meme_image(template, text_list, filepath)
            
            # Store the generated meme in memory
            self.memory.store(
                category="generated_content",
                key=meme_id,
                value={
                    "filepath": filepath,
                    "template": template["name"],
                    "text": text_list
                },
                metadata={
                    "type": "meme",
                    "topic": topic,
                    "style": style
                }
            )
            
            logger.info(f"Generated meme with template {template['name']}")
            
            return {
                "success": True,
                "content_id": meme_id,
                "filepath": filepath,
                "template": template["name"],
                "text": text_list
            }
        except Exception as e:
            logger.error(f"Error generating meme: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _select_template(self, template_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Select a template for the meme.
        
        Args:
            template_name: Name of the template to use
            
        Returns:
            Selected template information
        """
        if not self.templates:
            logger.error("No templates available")
            return None
        
        if template_name and template_name in self.templates:
            return self.templates[template_name]
        
        # Select a random template
        return random.choice(list(self.templates.values()))
    
    def _generate_meme_text(self, template: Dict[str, Any], topic: str, style: str) -> List[str]:
        """
        Generate text for the meme using an LLM.
        
        Args:
            template: Template information
            topic: Topic for the meme
            style: Style of humor
            
        Returns:
            List of text strings for the template
        """
        # Count the number of text regions in the template
        num_regions = len(template.get("text_regions", []))
        if num_regions == 0:
            num_regions = 2  # Default to 2 text regions
        
        # Create a prompt for the LLM
        prompt = f"Generate a {style} meme about {topic} for the template '{template['name']}'. "
        prompt += f"The meme should have {num_regions} text parts. "
        prompt += "Return only the text parts, one per line, without any additional explanation."
        
        try:
            # Run the model
            result = self.model_manager.run_model(
                self.default_text_model,
                prompt,
                max_tokens=256,
                temperature=0.8
            )
            
            if not result or not isinstance(result, str):
                logger.error("Failed to generate meme text")
                return ["Top text", "Bottom text"]
            
            # Parse the result into separate text parts
            text_parts = [part.strip() for part in result.strip().split('\n') if part.strip()]
            
            # Ensure we have the right number of parts
            while len(text_parts) < num_regions:
                text_parts.append("")
            
            if len(text_parts) > num_regions:
                text_parts = text_parts[:num_regions]
            
            return text_parts
        except Exception as e:
            logger.error(f"Error generating meme text: {str(e)}")
            return ["Top text", "Bottom text"]
    
    def _create_meme_image(self, template: Dict[str, Any], text_list: List[str], output_path: str):
        """
        Create the meme image by adding text to the template.
        
        Args:
            template: Template information
            text_list: List of text strings
            output_path: Path to save the output image
        """
        # This is a placeholder - in a real implementation, you would use an image processing library
        # For example:
        # from PIL import Image, ImageDraw, ImageFont
        # 
        # # Load the template image
        # template_path = template["path"]
        # img = Image.open(template_path)
        # 
        # # Create a drawing context
        # draw = ImageDraw.Draw(img)
        # 
        # # Add text to each region
        # for i, region in enumerate(template.get("text_regions", [])):
        #     if i < len(text_list) and text_list[i]:
        #         # Calculate position and size
        #         x = int(region["x"] * img.width)
        #         y = int(region["y"] * img.height)
        #         width = int(region["width"] * img.width)
        #         height = int(region["height"] * img.height)
        #         
        #         # Add text
        #         font = ImageFont.truetype("arial.ttf", 36)
        #         draw.text((x + width/2, y + height/2), text_list[i], font=font, fill="white", stroke_width=2, stroke_fill="black", anchor="mm")
        # 
        # # Save the image
        # img.save(output_path)
        
        logger.info(f"Would create meme image at {output_path} with text: {text_list}")
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """
        List available meme templates.
        
        Returns:
            List of template information
        """
        return [
            {
                "name": template["name"],
                "file": template.get("file", ""),
                "num_text_regions": len(template.get("text_regions", []))
            }
            for template in self.templates.values()
        ]
    
    def add_template(self, name: str, image_path: str, text_regions: List[Dict[str, Any]] = None) -> bool:
        """
        Add a new meme template.
        
        Args:
            name: Template name
            image_path: Path to the template image
            text_regions: List of text region definitions
            
        Returns:
            True if successful, False otherwise
        """
        if name in self.templates:
            logger.warning(f"Template {name} already exists")
            return False
        
        if not os.path.exists(image_path):
            logger.error(f"Template image not found: {image_path}")
            return False
        
        try:
            # Copy the image to the templates directory
            filename = os.path.basename(image_path)
            dest_path = os.path.join(self.templates_path, filename)
            
            # In a real implementation, you would copy the file here
            # For example: shutil.copy(image_path, dest_path)
            
            # Add the template to the collection
            self.templates[name] = {
                "name": name,
                "file": filename,
                "path": dest_path,
                "text_regions": text_regions or [
                    {"x": 0, "y": 0, "width": 1.0, "height": 0.3, "align": "center"},
                    {"x": 0, "y": 0.7, "width": 1.0, "height": 0.3, "align": "center"}
                ]
            }
            
            # Save the updated templates
            templates_json = os.path.join(self.templates_path, "templates.json")
            with open(templates_json, 'w') as f:
                json.dump(self.templates, f, indent=2)
            
            logger.info(f"Added new template: {name}")
            return True
        except Exception as e:
            logger.error(f"Error adding template {name}: {str(e)}")
            return False