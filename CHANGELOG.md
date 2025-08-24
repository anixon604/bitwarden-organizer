# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased] - Local Model Support

### Added
- **Local Model Support**: Added support for local AI models through custom base URLs
- **New Environment Variable**: `OPENAI_BASE_URL` for configuring custom API endpoints
- **New CLI Argument**: `--ai-base-url` for specifying local model endpoints
- **Ollama Integration**: Support for Ollama local models (http://localhost:11434/v1)
- **LocalAI Integration**: Support for LocalAI self-hosted models (http://localhost:8080/v1)
- **LM Studio Support**: Support for LM Studio local models (http://localhost:1234/v1)
- **Custom Endpoint Support**: Any OpenAI-compatible API endpoint
- **Comprehensive Documentation**: Added LOCAL_MODELS.md with setup guides and examples

### Changed
- **OpenAI API Update**: Migrated from OpenAI v0.x to v1.x API
- **Configuration Loading**: Enhanced environment variable support for local models
- **Error Handling**: Improved error messages for local model connections
- **CLI Help**: Updated help text to include local model options and examples

### Technical Details
- Updated `AIConfig` class to include `base_url` parameter
- Modified `AICategorizer` to use OpenAI v1.x client with custom base URLs
- Enhanced CLI argument parsing for local model configuration
- Added validation and error handling for custom endpoints
- Created example scripts demonstrating local model usage

### Files Modified
- `bitwarden_organizer/ai_config.py` - Added base URL support and v1.x API migration
- `bitwarden_organizer/cli.py` - Added `--ai-base-url` argument and help text
- `env.example` - Added `OPENAI_BASE_URL` environment variable
- `README.md` - Added local model documentation and examples
- `LOCAL_MODELS.md` - Comprehensive local model setup guide
- `examples/local_model_example.py` - Example usage scripts

### Breaking Changes
- **OpenAI API**: The tool now requires OpenAI Python package v1.0.0 or higher
- **API Key Handling**: Local models may not require real API keys (use placeholder values)

### Migration Guide
1. Update OpenAI package: `pip install "openai>=1.0.0"`
2. For local models, set `OPENAI_BASE_URL` in your `.env` file
3. Use appropriate model names for your local setup
4. Test with `--dry-run` before processing real data

### Local Model Quick Start
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama-3.1-8b

# Start Ollama
ollama serve

# Configure environment
export OPENAI_API_KEY="ollama"
export OPENAI_BASE_URL="http://localhost:11434/v1"
export OPENAI_MODEL="llama-3.1-8b"

# Run Bitwarden Organizer
bitwarden-organize export.json --ai
```

### Supported Local Model Platforms
- **Ollama**: http://localhost:11434/v1
- **LocalAI**: http://localhost:8080/v1
- **LM Studio**: http://localhost:1234/v1
- **Custom**: Any OpenAI-compatible endpoint

### Performance Notes
- Local models may have different response formats and capabilities
- Adjust batch sizes based on your model's performance
- Monitor memory usage with larger models (8B, 13B, 70B variants)
- Local models don't have API rate limits but may have memory constraints
