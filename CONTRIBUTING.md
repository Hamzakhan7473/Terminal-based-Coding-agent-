# Contributing to Terminal-based AI Coding Agent

Thank you for your interest in contributing to the Terminal-based AI Coding Agent! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/Hamzakhan7473/Terminal-based-Coding-agent-/issues)
2. If not, create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)

### Suggesting Features

1. Check [Discussions](https://github.com/Hamzakhan7473/Terminal-based-Coding-agent-/discussions) for existing feature requests
2. Create a new discussion with:
   - Clear feature description
   - Use case and motivation
   - Potential implementation approach

### Code Contributions

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes following our coding standards
4. Add tests for new functionality
5. Ensure all tests pass
6. Commit your changes: `git commit -m 'Add amazing feature'`
7. Push to your branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

## 📋 Development Setup

### Prerequisites

- Python 3.8+
- Git
- OpenAI API key (for testing)
- E2B API key (for sandbox testing)

### Installation

```bash
# Clone your fork
git clone https://github.com/your-username/Terminal-based-Coding-agent-.git
cd Terminal-based-Coding-agent-

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# Set up pre-commit hooks
pre-commit install
```

### Development Dependencies

Create a `requirements-dev.txt` file with:

```txt
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0
black>=22.0.0
flake8>=5.0.0
mypy>=1.0.0
pre-commit>=2.20.0
```

## 🏗️ Architecture Guidelines

### Code Organization

- Follow the existing module structure
- Keep related functionality together
- Use clear, descriptive names
- Add docstrings for all public functions/classes

### Design Patterns

- Use dependency injection for LLM clients
- Implement proper error handling with logging
- Follow async/await patterns for I/O operations
- Use Pydantic models for data validation

### Code Style

We use:
- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking
- **Pytest** for testing

```bash
# Format code
black coding_agent/

# Lint code
flake8 coding_agent/

# Type check
mypy coding_agent/

# Run tests
pytest tests/
```

## 🧪 Testing

### Writing Tests

- Place tests in the `tests/` directory
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies (APIs, file system)

### Test Structure

```python
import pytest
from coding_agent.core.intent_parser import IntentParser

class TestIntentParser:
    def test_parse_create_file_intent(self):
        # Arrange
        parser = IntentParser(mock_llm_client)
        user_input = "Create a Python file"
        
        # Act
        intent = parser.parse_intent(user_input)
        
        # Assert
        assert intent.intent_type == IntentType.CREATE_FILE
        assert intent.confidence > 0.5
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=coding_agent

# Run specific test file
pytest tests/test_intent_parser.py

# Run with verbose output
pytest -v
```

## 📝 Documentation

### Code Documentation

- Use Google-style docstrings
- Document all public APIs
- Include examples for complex functions
- Update README for new features

### Example Docstring

```python
def parse_intent(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> UserIntent:
    """
    Parse natural language input into structured intent.
    
    Args:
        user_input: Natural language input from user
        context: Optional context from previous interactions
        
    Returns:
        Parsed UserIntent object with structured information
        
    Raises:
        ValueError: If user input cannot be parsed
        
    Example:
        >>> parser = IntentParser(llm_client)
        >>> intent = parser.parse_intent("Create a Python function")
        >>> print(intent.intent_type)
        IntentType.CREATE_FILE
    """
```

## 🔒 Security Guidelines

### Code Safety

- Never commit API keys or secrets
- Use environment variables for configuration
- Validate all user inputs
- Implement proper error handling

### Sandbox Security

- Always execute user code in sandboxed environments
- Implement resource limits (CPU, memory, time)
- Block dangerous operations (file system access, network)
- Log all execution attempts

## 🚀 Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

- [ ] Update version in `pyproject.toml`
- [ ] Update CHANGELOG.md
- [ ] Run full test suite
- [ ] Update documentation
- [ ] Create release tag
- [ ] Publish to PyPI

## 💬 Communication

### Getting Help

- **GitHub Discussions**: For questions and general discussion
- **GitHub Issues**: For bugs and feature requests
- **Email**: [hamzakhan@taxora.ai](mailto:hamzakhan@taxora.ai)

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different viewpoints and experiences

## 📋 Pull Request Template

When creating a PR, please include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

## 🏆 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing to make AI-assisted coding more accessible! 🚀
