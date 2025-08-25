# Bitwarden Organizer

A Python tool to organize and structure Bitwarden JSON exports with **AI-powered** automatic categorization and tagging.

## Features

- **🤖 AI-Powered Categorization**: Uses OpenAI GPT models for intelligent, context-aware categorization
- **🧠 Smart Name Suggestions**: AI-generated descriptive names for better organization
- **🏷️ Intelligent Tagging**: Context-aware tag generation based on content and purpose
- **📁 Folder Organization**: Creates and assigns folders for personal vaults
- **🏢 Collection Management**: Handles organization vaults with collections
- **🔄 Rule-Based Fallback**: Automatic fallback to pattern-based rules if AI fails
- **🛡️ Safe Processing**: Never modifies usernames, passwords, or TOTP secrets
- **📝 Metadata Enhancement**: Adds structured notes with AI insights and metadata

## Installation

### Prerequisites

- Python 3.8 or higher
- Poetry (recommended) or pip
- OpenAI API key (for AI features)

### Using Poetry (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/bitwarden-organizer.git
cd bitwarden-organizer

# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Set up OpenAI API key
cp env.example .env
# Edit .env file with your OpenAI API key
```

### Using pip

```bash
pip install bitwarden-organizer
```

## Usage

### Command Line Interface

```bash
# Basic usage (rule-based)
bitwarden-organize input.json

# AI-powered organization
bitwarden-organize input.json --ai

# Specify output file
bitwarden-organize input.json -o organized_output.json

# AI with custom model and batch size
bitwarden-organize input.json --ai --ai-model gpt-4 --ai-batch-size 20

# AI with local model (Ollama)
bitwarden-organize input.json --ai --ai-model llama-3.1-8b --ai-base-url http://localhost:11434/v1

# AI with local model (LocalAI)
bitwarden-organize input.json --ai --ai-model llama-2-7b-chat --ai-base-url http://localhost:8080/v1

# Dry run (preview changes without writing)
bitwarden-organize input.json --dry-run

# Help
bitwarden-organize --help
```

### Python API

```python
from bitwarden_organizer import organize_bitwarden_export

# Organize export data
organized_data = organize_bitwarden_export(input_data)

# Save to file
with open('output.json', 'w') as f:
    json.dump(organized_data, f, indent=2)
```

## What It Does

The tool processes Bitwarden exports and:

### AI-Powered Processing (with `--ai` flag)
1. **🤖 AI Categorization**: Uses GPT models to intelligently categorize entries
2. **🧠 Smart Naming**: AI-generated descriptive names for better identification
3. **🏷️ Intelligent Tagging**: Context-aware tag generation based on content analysis
4. **📊 Batch Processing**: Efficiently processes items in configurable batches
5. **🔄 Smart Fallback**: Automatically falls back to rules if AI fails

### Local Model Support
The tool now supports local AI models through custom base URLs:

- **🔧 Ollama**: Use local models like llama-3.1-8b, codellama, mistral
- **🏠 LocalAI**: Self-hosted models with Docker support
- **💻 LM Studio**: Local model management and serving
- **🌐 Custom Endpoints**: Any OpenAI-compatible API endpoint

**Example with Ollama:**
```bash
# Set environment variables
export OPENAI_API_KEY="ollama"
export OPENAI_BASE_URL="http://localhost:11434/v1"
export OPENAI_MODEL="llama-3.1-8b"

# Run with local model
bitwarden-organize export.json --ai
```

**Example with CLI arguments:**
```bash
bitwarden-organize export.json --ai \
  --ai-model llama-3.1-8b \
  --ai-base-url http://localhost:11434/v1
```

See [LOCAL_MODELS.md](LOCAL_MODELS.md) for detailed setup instructions.

### Traditional Rule-Based Processing (default)
1. **🔍 Pattern Analysis**: Analyzes URLs and domains for categorization
2. **📁 Folder Creation**: Creates folders for personal vaults (if missing)
3. **🏢 Collection Assignment**: Assigns collections for organization vaults
4. **🏷️ Rule-Based Tagging**: Adds tags based on domain patterns
5. **📝 Metadata Structuring**: Adds structured notes with metadata headers
6. **✏️ Name Suggestions**: Suggests cleaner names based on domain analysis
7. **🛡️ Data Integrity**: Never touches sensitive fields (passwords, TOTP, etc.)

## Categories

The tool automatically categorizes entries into:

### AI-Powered Categories (with `--ai` flag)
The AI model can intelligently categorize entries into any relevant category based on context, including:
- **Finance**: Banking, payment processors, crypto exchanges, investments
- **Social**: Social media platforms, community sites, communication tools
- **Developer**: Code repositories, development tools, CI/CD, APIs
- **Cloud**: Cloud providers, infrastructure services, hosting platforms
- **Email**: Email providers, identity services, communication
- **Shopping**: E-commerce platforms, retail sites, marketplaces
- **Government/Utilities**: Government services, utility providers, official portals
- **Travel**: Travel booking, transportation services, accommodation
- **Security**: Security tools, authentication, password managers
- **Entertainment**: Streaming services, gaming platforms, media
- **Education**: Learning platforms, courses, academic resources
- **Health**: Healthcare services, fitness platforms, medical resources
- **Business**: Business tools, productivity software, professional services
- **General**: Everything else

### Rule-Based Categories (default)
- **Finance**: Banking, payment processors, crypto exchanges
- **Social**: Social media platforms, community sites
- **Developer**: Code repositories, development tools, CI/CD
- **Cloud**: Cloud providers, infrastructure services
- **Email**: Email providers, identity services
- **Shopping**: E-commerce platforms, retail sites
- **Government/Utilities**: Government services, utility providers
- **Travel**: Travel booking, transportation services
- **Security**: Security tools, password managers

## Safety Features

- **🛡️ Read-only processing** of sensitive data
- **💾 Backup recommendation** before processing
- **👀 Dry-run mode** to preview changes
- **✅ Validation** of input/output data
- **🚨 Error handling** for malformed data
- **🔄 AI fallback** to rule-based processing if needed
- **🔒 Secure API handling** for OpenAI integration

## Development

### Setup Development Environment

```bash
# Install development dependencies
poetry install --with dev,test

# Install pre-commit hooks
pre-commit install

# Run tests
poetry run pytest

# Run linting
poetry run black .
poetry run isort .
poetry run flake8 .
poetry run mypy .
```

### Project Structure

```
bitwarden-organizer/
├── bitwarden_organizer/
│   ├── __init__.py
│   ├── core.py          # Main organization logic
│   ├── cli.py           # Command-line interface
│   ├── ai_config.py     # AI configuration and OpenAI integration
│   └── utils.py         # Utility functions
├── tests/
│   ├── __init__.py
│   ├── test_core.py
│   └── test_cli.py
├── validation/
│   ├── validate_bitwarden_export.py  # Main validation script
│   ├── test_validation.py            # Test script for validation
│   ├── test_validation_errors.py     # Error scenario tests
│   └── validate.sh                   # Shell script wrapper
├── pyproject.toml       # Poetry configuration
├── env.example          # Environment variables template
├── README.md
├── VALIDATION_README.md # Validation documentation
└── .gitignore
```

## Validation

After organizing your Bitwarden export, you can validate the integrity and quality of the output using our validation script.

### Quick Validation

```bash
# Using the shell script (recommended)
./validate.sh bw.json bw_organized.json

# Using Python directly
python validate_bitwarden_export.py bw.json bw_organized.json

# Using Make
make validate INPUT=bw.json OUTPUT=bw_organized.json
```

### What Gets Validated

- **Data Integrity**: Item count, credentials preservation, core data integrity
- **Organization Quality**: Folders created, collections created, tags assigned
- **Metadata Preservation**: Notes, URIs, creation dates, revision dates
- **Structure Validation**: JSON format, required fields, vault type detection

### Test the Validation

```bash
# Test with sample data
make validate-test

# Test error scenarios
make validate-test-errors
```

### Validation Report

The script generates a comprehensive report showing:
- ✅ Pass/fail status for each validation check
- 📊 Statistics about organization improvements
- ⚠️ Warnings for non-critical issues
- ❌ Errors that prevent safe import
- 🎯 Overall recommendation for import

For detailed documentation, see [VALIDATION_README.md](VALIDATION_README.md).

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Configuration

### Environment Variables

Create a `.env` file in the project root with your OpenAI configuration:

```bash
# Required for AI features
OPENAI_API_KEY=your_openai_api_key_here

# Optional AI configuration
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.1
OPENAI_BASE_URL=https://api.openai.com/v1

# Feature flags
AI_CATEGORIZATION_ENABLED=true
AI_NAME_SUGGESTION_ENABLED=true
AI_TAG_GENERATION_ENABLED=true
```

**Local Model Configuration:**
```bash
# For Ollama
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_MODEL=llama-3.1-8b

# For LocalAI
OPENAI_BASE_URL=http://localhost:8080/v1
OPENAI_MODEL=llama-2-7b-chat

# For custom endpoints
OPENAI_BASE_URL=https://your-endpoint.com/v1
OPENAI_MODEL=your-model-name
```

### API Key Security

- Never commit your `.env` file to version control
- Use environment variables in production
- Consider using a secrets manager for sensitive keys

## Disclaimer

This tool processes sensitive password data. Always:
- Test on a copy of your export first
- Verify the output before importing back to Bitwarden
- Keep your original export as a backup
- Use in a secure environment
- Be aware that AI processing sends data to OpenAI (review their privacy policy)

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/bitwarden-organizer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/bitwarden-organizer/discussions)
- **Security**: Report security issues to [security@example.com](mailto:security@example.com)
