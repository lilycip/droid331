# Droid - Modular AI Agent

A highly modular and customizable AI agent for social media interaction and content generation. Droid is designed to be flexible, extensible, and powerful, allowing you to create sophisticated AI agents for various tasks.

## Features

- **Modular Architecture**: Easily add, remove, or customize components
- **Multiple AI Models**: Support for Llama 3.1, Stable Diffusion 2.1, and Stable Diffusion XL
- **Social Media Integration**: Post content, interact with influencers, and reply to comments
- **Content Generation**: Create text, images, memes, and GIFs
- **Memory System**: Store and retrieve context, history, and learned information
- **Task Scheduling**: Prioritize and schedule tasks automatically
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
```

## Extending Droid

### Adding a New Module

1. Create a new module file in the `droid/modules` directory
2. Implement the module class with required methods
3. Add the module to your configuration file
4. The agent will automatically load and use your module

### Adding a New Model

1. Add the model configuration to your `config.yaml` file
2. Implement any necessary adapters in the `ModelManager` class
3. The agent will handle loading and using the model

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Llama 3.1](https://ai.meta.com/llama/) by Meta AI
- [Stable Diffusion](https://stability.ai/stable-diffusion) by Stability AI