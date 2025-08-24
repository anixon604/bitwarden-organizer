# Bitwarden Organizer

A Python tool to organize and structure Bitwarden JSON exports with automatic categorization and tagging.

## Features

- **Automatic Categorization**: Intelligently categorizes entries based on domain patterns
- **Smart Tagging**: Adds relevant tags and labels to entries
- **Folder Organization**: Creates and assigns folders for personal vaults
- **Collection Management**: Handles organization vaults with collections
- **Safe Processing**: Never modifies usernames, passwords, or TOTP secrets
- **Metadata Enhancement**: Adds structured notes with metadata headers

## Installation

### Prerequisites

- Python 3.8 or higher
- Poetry (recommended) or pip

### Using Poetry (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/bitwarden-organizer.git
cd bitwarden-organizer

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

### Using pip

```bash
pip install bitwarden-organizer
```

## Usage

### Command Line Interface

```bash
# Basic usage
bitwarden-organize input.json

# Specify output file
bitwarden-organize input.json -o organized_output.json

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

1. **Analyzes URLs** to determine appropriate categories
2. **Creates folders** for personal vaults (if missing)
3. **Assigns collections** for organization vaults
4. **Adds tags** based on domain patterns and content
5. **Structures notes** with metadata headers
6. **Suggests cleaner names** for entries
7. **Maintains data integrity** - never touches sensitive fields

## Categories

The tool automatically categorizes entries into:

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

- **Read-only processing** of sensitive data
- **Backup recommendation** before processing
- **Dry-run mode** to preview changes
- **Validation** of input/output data
- **Error handling** for malformed data

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
│   └── utils.py         # Utility functions
├── tests/
│   ├── __init__.py
│   ├── test_core.py
│   └── test_cli.py
├── pyproject.toml       # Poetry configuration
├── README.md
└── .gitignore
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool processes sensitive password data. Always:
- Test on a copy of your export first
- Verify the output before importing back to Bitwarden
- Keep your original export as a backup
- Use in a secure environment

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/bitwarden-organizer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/bitwarden-organizer/discussions)
- **Security**: Report security issues to [security@example.com](mailto:security@example.com)
