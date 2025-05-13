"""
Model Manager - Handles loading and interfacing with different AI models.
"""
import logging
import time
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class ModelManager:
    """
    Manages the loading, unloading, and interfacing with various AI models.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the ModelManager with configuration.
        
        Args:
            config: Configuration dictionary for models
        """
        self.config = config
        self.models = {}
        self.loaded_models = set()
        
        # Register available models from config
        self._register_models()
        
        # Load models marked as preload
        self._preload_models()
        
        logger.info(f"ModelManager initialized with {len(self.models)} registered models")
    
    def _register_models(self):
        """Register all models specified in the configuration."""
        for model_name, model_config in self.config.items():
            self.models[model_name] = {
                "type": model_config.get("type", "unknown"),
                "path": model_config.get("path", ""),
                "config": model_config.get("config", {}),
                "instance": None
            }
            logger.info(f"Registered model: {model_name} ({model_config.get('type', 'unknown')})")
    
    def _preload_models(self):
        """Preload models marked for preloading in the configuration."""
        for model_name, model_config in self.config.items():
            if model_config.get("preload", False):
                self.load_model(model_name)
    
    def load_model(self, model_name: str) -> bool:
        """
        Load a specific model into memory.
        
        Args:
            model_name: Name of the model to load
            
        Returns:
            True if successful, False otherwise
        """
        if model_name not in self.models:
            logger.error(f"Model {model_name} not registered")
            return False
            
        if model_name in self.loaded_models:
            logger.info(f"Model {model_name} already loaded")
            return True
            
        model_info = self.models[model_name]
        model_type = model_info["type"]
        
        try:
            # Load different model types
            if model_type == "llm":
                self._load_llm_model(model_name, model_info)
            elif model_type == "diffusion":
                self._load_diffusion_model(model_name, model_info)
            else:
                logger.error(f"Unknown model type: {model_type}")
                return False
                
            self.loaded_models.add(model_name)
            logger.info(f"Successfully loaded model: {model_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {str(e)}")
            return False
    
    def _load_llm_model(self, model_name: str, model_info: Dict[str, Any]):
        """Load a Large Language Model."""
        model_path = model_info["path"]
        model_config = model_info["config"]
        
        # Implementation for Llama 3.1
        if "llama" in model_name.lower():
            try:
                from llama_cpp import Llama
                
                # Check if model file exists
                import os
                model_file = os.path.join(model_path, "model.gguf")
                if not os.path.exists(model_file):
                    logger.warning(f"Model file not found at {model_file}. Using placeholder.")
                    model_info["instance"] = {
                        "name": model_name, 
                        "type": "llm_placeholder",
                        "generate": lambda prompt: f"[Simulated response from {model_name} for prompt: {prompt[:30]}...]"
                    }
                    return
                
                # Load the model
                logger.info(f"Loading LLM model {model_name} from {model_file}")
                model = Llama(
                    model_path=model_file,
                    n_ctx=model_config.get("max_tokens", 2048),
                    n_threads=model_config.get("n_threads", 4),
                    n_gpu_layers=model_config.get("n_gpu_layers", -1)
                )
                
                # Create a wrapper function for the model
                def generate(prompt, **kwargs):
                    temperature = kwargs.get("temperature", model_config.get("temperature", 0.7))
                    top_p = kwargs.get("top_p", model_config.get("top_p", 0.95))
                    max_tokens = kwargs.get("max_tokens", model_config.get("max_tokens", 2048))
                    repeat_penalty = kwargs.get("repeat_penalty", model_config.get("repetition_penalty", 1.1))
                    
                    response = model(
                        prompt,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        top_p=top_p,
                        repeat_penalty=repeat_penalty
                    )
                    
                    return response["choices"][0]["text"]
                
                # Store the model and the generate function
                model_info["instance"] = model
                model_info["instance"].generate = generate
                
            except ImportError:
                logger.error("llama_cpp library not installed. Install with: pip install llama-cpp-python")
                model_info["instance"] = {
                    "name": model_name, 
                    "type": "llm_placeholder",
                    "generate": lambda prompt: f"[Simulated response from {model_name} for prompt: {prompt[:30]}...]"
                }
        else:
            # Generic LLM loading logic using Hugging Face transformers
            try:
                from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
                
                # Check if model directory exists
                import os
                if not os.path.exists(model_path):
                    logger.warning(f"Model directory not found at {model_path}. Using placeholder.")
                    model_info["instance"] = {
                        "name": model_name, 
                        "type": "llm_placeholder",
                        "generate": lambda prompt: f"[Simulated response from {model_name} for prompt: {prompt[:30]}...]"
                    }
                    return
                
                # Load the model and tokenizer
                logger.info(f"Loading transformer model {model_name} from {model_path}")
                tokenizer = AutoTokenizer.from_pretrained(model_path)
                model = AutoModelForCausalLM.from_pretrained(
                    model_path,
                    device_map="auto",
                    torch_dtype="auto"
                )
                
                # Create a text generation pipeline
                generator = pipeline(
                    "text-generation",
                    model=model,
                    tokenizer=tokenizer,
                    max_length=model_config.get("max_tokens", 2048),
                    temperature=model_config.get("temperature", 0.7),
                    top_p=model_config.get("top_p", 0.95),
                    repetition_penalty=model_config.get("repetition_penalty", 1.1)
                )
                
                # Create a wrapper function for the model
                def generate(prompt, **kwargs):
                    max_length = kwargs.get("max_tokens", model_config.get("max_tokens", 2048))
                    temperature = kwargs.get("temperature", model_config.get("temperature", 0.7))
                    top_p = kwargs.get("top_p", model_config.get("top_p", 0.95))
                    repetition_penalty = kwargs.get("repeat_penalty", model_config.get("repetition_penalty", 1.1))
                    
                    response = generator(
                        prompt,
                        max_length=max_length,
                        temperature=temperature,
                        top_p=top_p,
                        repetition_penalty=repetition_penalty,
                        do_sample=True
                    )
                    
                    return response[0]["generated_text"][len(prompt):]
                
                # Store the model and the generate function
                model_info["instance"] = model
                model_info["instance"].generate = generate
                
            except ImportError:
                logger.error("transformers library not installed. Install with: pip install transformers")
                model_info["instance"] = {
                    "name": model_name, 
                    "type": "llm_placeholder",
                    "generate": lambda prompt: f"[Simulated response from {model_name} for prompt: {prompt[:30]}...]"
                }
    
    def _load_diffusion_model(self, model_name: str, model_info: Dict[str, Any]):
        """Load a Diffusion Model for image generation."""
        model_path = model_info["path"]
        model_config = model_info["config"]
        
        # Implementation for Stable Diffusion
        if "stable-diffusion" in model_name.lower():
            try:
                from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
                import torch
                
                # Check if model directory exists
                import os
                if not os.path.exists(model_path) and not model_path.startswith("runwayml/") and not model_path.startswith("stabilityai/"):
                    logger.warning(f"Model directory not found at {model_path}. Using placeholder.")
                    model_info["instance"] = {
                        "name": model_name, 
                        "type": "diffusion_placeholder",
                        "generate": lambda prompt: {"image_data": "placeholder_image_data", "prompt": prompt}
                    }
                    return
                
                # Determine if we should use a local path or download from HuggingFace
                # Always use HuggingFace models for now
                if "xl" in model_name.lower():
                    model_id = "stabilityai/stable-diffusion-xl-base-1.0"
                else:
                    model_id = "runwayml/stable-diffusion-v1-5"
                
                # Load the model
                logger.info(f"Loading diffusion model {model_name} from {model_id}")
                
                # Set up the pipeline with appropriate device
                device = "cuda" if torch.cuda.is_available() else "cpu"
                torch_dtype = torch.float16 if device == "cuda" else torch.float32
                
                # Load the pipeline
                pipe = StableDiffusionPipeline.from_pretrained(
                    model_id,
                    torch_dtype=torch_dtype,
                    safety_checker=None  # Disable safety checker for faster inference
                )
                
                # Use DPM-Solver++ for faster inference
                pipe.scheduler = DPMSolverMultistepScheduler.from_config(
                    pipe.scheduler.config,
                    algorithm_type="dpmsolver++",
                    solver_order=2
                )
                
                # Move to device
                pipe = pipe.to(device)
                
                # Enable memory optimization if on GPU
                if device == "cuda":
                    pipe.enable_attention_slicing()
                    # Enable xformers if available for memory efficiency
                    try:
                        pipe.enable_xformers_memory_efficient_attention()
                    except:
                        logger.info("xformers not available, using default attention mechanism")
                
                # Create a wrapper function for the model
                def generate(prompt, **kwargs):
                    width = kwargs.get("width", model_config.get("width", 512))
                    height = kwargs.get("height", model_config.get("height", 512))
                    guidance_scale = kwargs.get("guidance_scale", model_config.get("guidance_scale", 7.5))
                    num_inference_steps = kwargs.get("num_inference_steps", model_config.get("num_inference_steps", 50))
                    negative_prompt = kwargs.get("negative_prompt", "")
                    
                    # Generate the image
                    with torch.no_grad():
                        image = pipe(
                            prompt=prompt,
                            negative_prompt=negative_prompt,
                            width=width,
                            height=height,
                            guidance_scale=guidance_scale,
                            num_inference_steps=num_inference_steps
                        ).images[0]
                    
                    # Save the image to a temporary file
                    import tempfile
                    import os
                    
                    # Use provided output directory or default
                    output_dir = kwargs.get("output_dir", os.path.join("data", "generated", "images"))
                    os.makedirs(output_dir, exist_ok=True)
                    
                    # Save the image with a unique filename
                    timestamp = int(time.time())
                    filename = kwargs.get("filename", f"{model_name}_{timestamp}.png")
                    image_path = os.path.join(output_dir, filename)
                    image.save(image_path)
                    
                    return {
                        "image": image,
                        "image_path": image_path,
                        "prompt": prompt
                    }
                
                # Store the model and the generate function
                model_info["instance"] = pipe
                model_info["instance"].generate = generate
                
            except ImportError as e:
                logger.error(f"Error loading diffusion model: {str(e)}")
                logger.error("Make sure diffusers, torch, and transformers are installed")
                model_info["instance"] = {
                    "name": model_name, 
                    "type": "diffusion_placeholder",
                    "generate": lambda prompt: {"image_data": "placeholder_image_data", "prompt": prompt}
                }
        else:
            # Generic diffusion model loading logic
            logger.info(f"Loading generic diffusion model {model_name}")
            model_info["instance"] = {
                "name": model_name, 
                "type": "diffusion_placeholder",
                "generate": lambda prompt: {"image_data": "placeholder_image_data", "prompt": prompt}
            }
    
    def unload_model(self, model_name: str) -> bool:
        """
        Unload a model from memory.
        
        Args:
            model_name: Name of the model to unload
            
        Returns:
            True if successful, False otherwise
        """
        if model_name not in self.loaded_models:
            logger.warning(f"Model {model_name} not loaded")
            return False
            
        try:
            # Clear the model instance
            self.models[model_name]["instance"] = None
            self.loaded_models.remove(model_name)
            logger.info(f"Unloaded model: {model_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to unload model {model_name}: {str(e)}")
            return False
    
    def has_model(self, model_name: str) -> bool:
        """
        Check if a model is registered.
        
        Args:
            model_name: Name of the model to check
            
        Returns:
            True if the model is registered, False otherwise
        """
        return model_name in self.models
    
    def get_model(self, model_name: str) -> Optional[Any]:
        """
        Get a loaded model instance.
        
        Args:
            model_name: Name of the model to get
            
        Returns:
            Model instance if loaded, None otherwise
        """
        if model_name not in self.loaded_models:
            logger.warning(f"Model {model_name} not loaded, attempting to load")
            if not self.load_model(model_name):
                return None
                
        return self.models[model_name]["instance"]
    
    def run_model(self, model_name: str, inputs: Any, **kwargs) -> Any:
        """
        Run inference on a specific model.
        
        Args:
            model_name: Name of the model to use
            inputs: Input data for the model
            **kwargs: Additional parameters for the model
            
        Returns:
            Model output
        """
        model = self.get_model(model_name)
        if not model:
            logger.error(f"Failed to get model {model_name}")
            return None
            
        model_type = self.models[model_name]["type"]
        
        try:
            # Run different model types
            if model_type == "llm":
                return self._run_llm(model, inputs, **kwargs)
            elif model_type == "diffusion":
                return self._run_diffusion(model, inputs, **kwargs)
            else:
                logger.error(f"Unknown model type: {model_type}")
                return None
        except Exception as e:
            logger.error(f"Error running model {model_name}: {str(e)}")
            return None
    
    def _run_llm(self, model: Any, prompt: str, **kwargs) -> str:
        """Run inference on an LLM model."""
        logger.info(f"Running LLM with prompt: {prompt[:50]}...")
        
        # Check if the model has a generate method
        if hasattr(model, 'generate'):
            return model.generate(prompt, **kwargs)
        # Check if it's a dictionary with a generate function
        elif isinstance(model, dict) and callable(model.get('generate')):
            return model['generate'](prompt, **kwargs)
        # Otherwise, return a placeholder response
        else:
            logger.warning("Model doesn't have a generate method, using placeholder response")
            return f"LLM response to: {prompt[:20]}..."
    
    def _run_diffusion(self, model: Any, prompt: str, **kwargs) -> Any:
        """Run inference on a diffusion model."""
        logger.info(f"Running diffusion model with prompt: {prompt[:50]}...")
        
        # Check if the model has a generate method
        if hasattr(model, 'generate'):
            return model.generate(prompt, **kwargs)
        # Check if it's a dictionary with a generate function
        elif isinstance(model, dict) and callable(model.get('generate')):
            return model['generate'](prompt, **kwargs)
        # Otherwise, return a placeholder response
        else:
            logger.warning("Model doesn't have a generate method, using placeholder response")
            return {"image_data": "placeholder_image_data", "prompt": prompt}