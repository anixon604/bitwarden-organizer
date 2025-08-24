# Using Local Models with Bitwarden Organizer

The Bitwarden Organizer now supports local AI models through custom base URLs. This allows you to use models like Ollama, LocalAI, or any other OpenAI-compatible API endpoint.

## Supported Local Model Platforms

### 1. Ollama
- **Base URL**: `http://localhost:11434/v1`
- **Models**: llama-3.1-8b, codellama, mistral, etc.
- **Installation**: [https://ollama.ai](https://ollama.ai)

### 2. LocalAI
- **Base URL**: `http://localhost:8080/v1`
- **Models**: Various open-source models
- **Installation**: [https://github.com/go-skynet/LocalAI](https://github.com/go-skynet/LocalAI)

### 3. LM Studio
- **Base URL**: `http://localhost:1234/v1`
- **Models**: Various local models
- **Installation**: [https://lmstudio.ai](https://lmstudio.ai)

### 4. Custom Endpoints
- Any OpenAI-compatible API endpoint
- Self-hosted models
- Cloud providers with OpenAI-compatible APIs

## Configuration Methods

### Method 1: Environment Variables (Recommended)

Create a `.env` file in your project directory:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=llama-3.1-8b
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.1
OPENAI_BASE_URL=http://localhost:11434/v1

# Optional: Customize AI behavior
AI_CATEGORIZATION_ENABLED=true
AI_NAME_SUGGESTION_ENABLED=true
AI_TAG_GENERATION_ENABLED=true
```

### Method 2: Command Line Arguments

Override environment variables with CLI arguments:

```bash
# Use Ollama with llama-3.1-8b
bitwarden-organize export.json --ai \
  --ai-model llama-3.1-8b \
  --ai-base-url http://localhost:11434/v1

# Use LocalAI with custom model
bitwarden-organize export.json --ai \
  --ai-model local-model \
  --ai-base-url http://localhost:8080/v1

# Use LM Studio
bitwarden-organize export.json --ai \
  --ai-model local-model \
  --ai-base-url http://localhost:1234/v1
```

### Method 3: Python API

```python
from bitwarden_organizer.ai_config import AIConfig, AICategorizer

# Configure for local model
config = AIConfig(
    api_key="your_api_key",
    model="llama-3.1-8b",
    base_url="http://localhost:11434/v1"
)

# Initialize AI categorizer
categorizer = AICategorizer(config)
```

## Setup Examples

### Ollama Setup

1. **Install Ollama**:
   ```bash
   # macOS/Linux
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Windows
   # Download from https://ollama.ai/download
   ```

2. **Pull a model**:
   ```bash
   ollama pull llama-3.1-8b
   ```

3. **Start Ollama**:
   ```bash
   ollama serve
   ```

4. **Configure Bitwarden Organizer**:
   ```bash
   export OPENAI_API_KEY="ollama"
   export OPENAI_BASE_URL="http://localhost:11434/v1"
   export OPENAI_MODEL="llama-3.1-8b"
   
   bitwarden-organize export.json --ai
   ```

### LocalAI Setup

1. **Install LocalAI**:
   ```bash
   # Using Docker
   docker run -d --name localai \
     -p 8080:8080 \
     -v localai:/models \
     quay.io/go-skynet/localai:latest
   ```

2. **Download models**:
   ```bash
   # Download a model to the models directory
   wget https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML/resolve/main/llama-2-7b-chat.ggmlv3.q4_0.bin
   ```

3. **Configure Bitwarden Organizer**:
   ```bash
   export OPENAI_API_KEY="localai"
   export OPENAI_BASE_URL="http://localhost:8080/v1"
   export OPENAI_MODEL="llama-2-7b-chat"
   
   bitwarden-organize export.json --ai
   ```

## Model Compatibility

### Required Model Capabilities

Your local model should support:
- **Chat completion API** (`/v1/chat/completions`)
- **System prompts** (for categorization instructions)
- **JSON-like responses** (for structured output)

### Recommended Models

- **Llama 3.1 8B** - Good balance of performance and resource usage
- **CodeLlama** - Excellent for developer-related categorization
- **Mistral 7B** - Fast and efficient
- **Phi-3** - Lightweight and capable

## Troubleshooting

### Common Issues

1. **Connection Refused**:
   ```bash
   # Check if your local model server is running
   curl http://localhost:11434/v1/models  # Ollama
   curl http://localhost:8080/v1/models   # LocalAI
   ```

2. **Model Not Found**:
   ```bash
   # List available models
   ollama list                    # Ollama
   curl http://localhost:8080/v1/models  # LocalAI
   ```

3. **API Key Issues**:
   - Most local models don't require real API keys
   - Use any placeholder value like "local" or "ollama"

4. **Response Format Issues**:
   - Ensure your model supports chat completions
   - Check if system prompts are supported

### Debug Mode

Enable verbose output to see detailed API interactions:

```bash
bitwarden-organize export.json --ai --verbose
```

## Performance Considerations

### Resource Usage
- **8B models**: ~8GB RAM, good for most use cases
- **13B models**: ~13GB RAM, better quality, slower
- **70B models**: ~70GB RAM, best quality, much slower

### Batch Processing
- Adjust batch size based on your model's performance:
  ```bash
  bitwarden-organize export.json --ai --ai-batch-size 5
  ```

### Caching
- Local models don't have API rate limits
- Process items in smaller batches for better memory management

## Security Notes

- Local models keep your data on your machine
- No data is sent to external services
- API keys for local models are typically not validated
- Ensure your local model server is properly secured

## Advanced Configuration

### Custom Model Parameters

Some local models support additional parameters:

```python
# Example with custom parameters
config = AIConfig(
    api_key="local",
    model="llama-3.1-8b",
    base_url="http://localhost:11434/v1",
    temperature=0.7,  # More creative responses
    max_tokens=2000   # Longer responses
)
```

### Multiple Model Endpoints

You can easily switch between different local models:

```bash
# Development model
export OPENAI_BASE_URL="http://localhost:11434/v1"
export OPENAI_MODEL="llama-3.1-8b"

# Production model
export OPENAI_BASE_URL="http://localhost:8080/v1"
export OPENAI_MODEL="llama-3.1-70b"
```

## Testing Your Setup

Run the test script to verify your configuration:

```bash
python test_local_model.py
```

This will test:
- Configuration loading
- Base URL handling
- Model parameter setting
- AI categorizer initialization

## Support

If you encounter issues with local models:

1. Check the model server logs
2. Verify API endpoint compatibility
3. Test with a simple curl request
4. Check model documentation for specific requirements

Remember: Local models may have different response formats and capabilities compared to OpenAI's models. Adjust your expectations accordingly.
