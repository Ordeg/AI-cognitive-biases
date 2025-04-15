# O1 LLM API Client

A simple Python application for making API calls to the O1 LLM model.

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Configure your API credentials by editing the `.env` file:
   ```
   O1_API_KEY=your_api_key_here
   O1_API_BASE=https://api.o1.aiinfra.io/v1
   ```

## Usage

You can use the client in two ways:

### Command Line

Run the script with command line arguments:

```bash
python o1_api_client.py --prompt "Your prompt here" --model "o1-mini" --max-tokens 1000 --temperature 0.7
```

Or simply run it and enter your prompt when prompted:

```bash
python o1_api_client.py
```

### As a Module

You can also import and use the client in your own Python code:

```python
from o1_api_client import O1Client

client = O1Client(api_key="your_api_key_here")
response = client.generate_text(
    prompt="Your prompt here",
    model="o1-mini",
    max_tokens=1000,
    temperature=0.7
)
print(response)
```

## Available Models

- `o1-mini`: Smaller, faster version
- `o1-preview`: Full version with more capabilities

## Parameters

- `prompt`: The text prompt to generate a completion for
- `model`: The model to use (default: "o1-mini")
- `max_tokens`: Maximum number of tokens to generate (default: 1000)
- `temperature`: Controls randomness. Higher values (e.g., 0.8) make output more random, lower values (e.g., 0.2) make it more deterministic (default: 0.7)
