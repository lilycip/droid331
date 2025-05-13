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