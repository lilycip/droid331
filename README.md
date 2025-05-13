# Droid - Modular AI Agent

A highly modular and customizable AI agent for social media interaction and content generation. Droid is designed to be flexible, extensible, and powerful, allowing you to create sophisticated AI agents for various tasks.

## Features

- **Modular Architecture**: Easily add, remove, or customize components
- **Multiple AI Models**: Support for Llama 3.1, Stable Diffusion 2.1, and Stable Diffusion XL
- **Social Media Integration**: Post content, interact with influencers, and reply to comments
- **Content Generation**: Create text, images, memes, and GIFs
- **Memory System**: Store and retrieve context, history, and learned information
- **Task Scheduling**: Prioritize and schedule tasks automatically
- **Team Management**: Coordinate multiple AI agents with specialized roles
- **Extensible Plugin System**: Add new features with minimal code

## Architecture

Droid is built with a modular architecture consisting of:

### Core Components

- **Agent**: Central orchestration system
- **Model Manager**: Handles loading and interfacing with different AI models
- **Task Scheduler**: Manages and prioritizes different tasks
- **Memory System**: Stores context, history, and learned information

### Feature Modules

- **Social Media**: Post to various platforms
- **Content Generator**: Generate text and images
- **Meme Generator**: Create memes with templates
- **Influencer Interaction**: Interact with social media influencers
- **Comment Reply**: Reply to comments on social media
- **Management**: Coordinate teams of specialized AI agents for complex tasks using CrewAI Lite

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/droid.git
   cd droid
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure the agent:
   ```
   cp config/config.example.yaml config/config.yaml
   # Edit config.yaml with your settings
   ```

4. Run the agent:
   ```
   python main.py
   ```

## Configuration

Droid is highly configurable through the `config.yaml` file. You can customize:

- AI models and their parameters
- Enabled modules and their settings
- Task scheduling and priorities
- Memory system configuration
- Logging settings

See the `config/config.yaml` file for a complete example.

## Models

Droid supports multiple AI models for different tasks:

### Llama 3.1

Llama 3.1 is a powerful large language model (LLM) from Meta AI. It's used for text generation, conversation, and reasoning tasks.

To download and set up Llama 3.1:

```bash
# Download the 8B parameter model
python scripts/download_llama.py --model-size 8b

# Download the 70B parameter model (requires more memory)
python scripts/download_llama.py --model-size 70b
```

### Stable Diffusion

Stable Diffusion is a state-of-the-art text-to-image diffusion model. It's used for generating images from text prompts.

To download and set up Stable Diffusion:

```bash
# Download Stable Diffusion v1.5
python scripts/download_stable_diffusion.py --model-type sd

# Download Stable Diffusion XL (higher quality, requires more memory)
python scripts/download_stable_diffusion.py --model-type sdxl
```

### Testing Models

You can test the models with the provided test script:

```bash
# Test all models
python examples/test_models.py

# Test only LLM models
python examples/test_models.py --model-type llm

# Test only diffusion models
python examples/test_models.py --model-type diffusion

# Test a specific model
python examples/test_models.py --model-name llama-3.1
python examples/test_models.py --model-name stable-diffusion-xl
```

## Usage

### CLI Mode

Run the agent in CLI mode with interactive shell:

```
python run_cli.py --interactive
```

### Execute a Specific Task

```
python run_cli.py --task post_content --params '{"platform": "twitter", "content": "Hello, world!"}'
```

### Custom Configuration

```
python run_cli.py --config my_config.yaml
```

### Web Interface

Droid includes a web interface for easy interaction:

```
python run_web.py
```

This will start a web server on port 12000 by default. You can access the interface at http://localhost:12000.

Options:
- `--port PORT`: Specify a custom port (default: 12000)
- `--host HOST`: Specify the host (default: 0.0.0.0)
- `--debug`: Run in debug mode

Example:
```
python run_web.py --port 8080 --debug
```

## Examples

The `examples` directory contains sample scripts to help you get started with Droid. These examples demonstrate various features and capabilities of the agent.

### Basic Usage

- `generate_content.py`: Generate text, images, or memes
- `social_media_post.py`: Post content to social media platforms
- `run_task.py`: Run a specific task with parameters
- `test_web_api.py`: Test the web API endpoints

### Model Integration

- `run_with_llama.py`: Run the agent with Llama 3.1 model
- `run_with_stable_diffusion.py`: Run the agent with Stable Diffusion model
- `run_with_all_models.py`: Run the agent with all supported models

### Customization

- `run_with_module.py`: Run the agent with a specific module
- `custom_module.py`: Create and use a custom module
- `custom_config.py`: Create and use a custom configuration
- `custom_memory.py`: Create and use a custom memory system
- `custom_scheduler.py`: Create and use a custom task scheduler
- `custom_model_adapter.py`: Create and use a custom model adapter
- `custom_logger.py`: Create and use a custom logger
- `custom_api.py`: Create and use a custom API
- `custom_plugin.py`: Create and use a custom plugin system
- `custom_workflow.py`: Create and use a custom workflow system

### Running Examples

To run an example script:

```bash
# Basic example
python examples/generate_content.py --prompt "Write a blog post about AI agents" --type text

# Run with a specific model
python examples/run_with_llama.py --llama_path /path/to/llama/model --interactive

# Run with a custom module
python examples/custom_module.py --interactive

# Run with a custom memory system
python examples/custom_memory.py --db-path /tmp/droid/memory.db --interactive

# Run with a custom task scheduler
python examples/custom_scheduler.py --interactive

# Run with a custom model adapter
python examples/custom_model_adapter.py --interactive

# Run with a custom logger
python examples/custom_logger.py --log-format colored --log-file /tmp/droid/agent.log

# Run with a custom API
python examples/custom_api.py --port 5000 --api-key "your-secret-key"

# Test the custom API
python examples/test_custom_api.py --url "http://localhost:5000" --api-key "your-secret-key"

# Run with a custom plugin system
python examples/custom_plugin.py --plugin-dir plugins --log-file /tmp/droid/events.log

# Run with a custom workflow system
python examples/custom_workflow.py --workflow workflows/social_media_post.json

# Run with the management module
python examples/management_example.py --team-type custom --topic "artificial intelligence" --platform twitter

# Test management module with AI models
python examples/test_management_with_models.py --topic "climate change" --debug

# Test image generation with Stable Diffusion
python examples/test_image_generation.py --model stable-diffusion-2.1 --output-dir ./output
```

## Extending Droid

### Adding a New Module

1. Create a new module file in the `droid/modules` directory
2. Implement the module class with required methods
3. Add the module to your configuration file
4. The agent will automatically load and use your module

## Image Generation

The `ImageGenerator` module provides a simple interface for generating images using diffusion models:

```python
from droid.core.model_manager import ModelManager
from droid.core.memory import MemorySystem
from droid.modules.image_generator import ImageGenerator
from droid.utils.config_manager import ConfigManager

# Load configuration
config_manager = ConfigManager()
config = config_manager.get_config()

# Initialize components
model_manager = ModelManager(config.get("models", {}))
memory = MemorySystem(config.get("memory", {}))

# Initialize image generator
image_generator = ImageGenerator(
    config.get("modules", {}).get("image_generator", {}),
    model_manager,
    memory
)

# Generate an image
result = image_generator.generate({
    "prompt": "A beautiful landscape with mountains and a lake",
    "model": "stable-diffusion-xl",
    "width": 768,
    "height": 512,
    "num_inference_steps": 25  # Lower for faster generation
})

if result["success"]:
    print(f"Image generated at: {result['filepath']}")
else:
    print(f"Error: {result['error']}")
```

You can customize the output directory and filename when generating images:

```python
# In ModelManager.run_model():
result = model_manager.run_model(
    "stable-diffusion-xl",
    "A beautiful landscape with mountains and a lake",
    output_dir="./my_images",
    filename="landscape.png",
    num_inference_steps=25
)
```

### Adding a New Model

1. Add the model configuration to your `config.yaml` file
2. Implement any necessary adapters in the `ModelManager` class
3. The agent will handle loading and using the model

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## CrewAI Lite

Droid includes a lightweight implementation of CrewAI called CrewAI Lite, which provides the core functionality of CrewAI without the complex dependencies. This allows you to coordinate multiple AI agents with different roles and goals, enabling complex task execution in a sequential or hierarchical manner.

### Features

- **Agent**: Define specialized AI agents with roles, goals, and backstories
- **Task**: Create tasks for agents to execute
- **Crew**: Coordinate multiple agents working together
- **Tool**: Define custom tools for agents to use
- **Process**: Choose between sequential or hierarchical execution

### Example

```python
from droid.modules.management import Management, CustomTool
from droid.utils.crewai_lite import Agent, Task, Crew, Process

# Create a management module
management = Management(config, model_manager, memory)

# Register tools
management.register_tool(
    name="search_web",
    description="Search the web for information",
    func=search_web
)

# Create agents
management.create_agent(
    name="researcher",
    role="Research Specialist",
    goal="Find accurate information",
    tools=["search_web"]
)

# Create tasks
management.create_task(
    name="research_topic",
    description="Research the topic: AI",
    agent_name="researcher",
    expected_output="Research notes"
)

# Create and run a team
team_name = "research_team"
management.create_team(
    name=team_name,
    task_names=["research_topic"],
    process="sequential"
)

result = management.run_team(team_name, {"topic": "AI"})
```

## Acknowledgments

- [Llama 3.1](https://ai.meta.com/llama/) by Meta AI
- [Stable Diffusion](https://stability.ai/stable-diffusion) by Stability AI
- [CrewAI](https://github.com/joaomdmoura/crewAI) by João Moura (inspiration for CrewAI Lite)