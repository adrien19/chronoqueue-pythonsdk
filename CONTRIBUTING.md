# Contributing to Chronoqueue Python SDK

Thank you for your interest in contributing to the Chronoqueue Python SDK! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Poetry for dependency management
- Git

### Setting Up Your Development Environment

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/your-username/chronoqueue-pythonsdk.git
   cd chronoqueue-pythonsdk
   ```

2. Install dependencies:
   ```bash
   make install-dev
   ```

3. Generate proto files:
   ```bash
   make gen-proto
   ```

## Development Workflow

### Making Changes

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the coding standards below

3. Run tests:
   ```bash
   make test
   ```

4. Run linting and formatting:
   ```bash
   make format
   make lint
   ```

5. Commit your changes with a descriptive message:
   ```bash
   git commit -m "feat: Description of your changes"
   ```

6. Push to your fork and create a pull request

### Coding Standards

- **Code Style**: We use Black for code formatting (120 character line length)
- **Import Sorting**: We use isort with Black-compatible settings
- **Type Hints**: Use type hints where appropriate
- **Documentation**: Add docstrings for public functions and classes
- **Testing**: Write tests for new functionality

### Running Quality Checks

Before submitting a PR, ensure all checks pass:

```bash
# Format code
make format

# Run linting
make lint

# Run type checking
make typecheck

# Run tests with coverage
make test-coverage

# Run all CI checks
make ci
```

### Updating Proto Definitions

The project uses proto definitions from the [chronoqueue repository](https://github.com/adrien19/chronoqueue). To update them:

1. Set your GitHub token (required for private repo access):
```bash
export GITHUB_TOKEN=your_github_token
```

You can create a token at: https://github.com/settings/tokens (needs `repo` scope)

2. Download the latest proto definitions:
```bash
make update-proto
```

3. Regenerate Python classes:
```bash
make gen-proto
```

This will:
- Generate Python gRPC classes from all `.proto` files
- Fix imports to use relative imports
- Format the generated code with Black and isort
- Create proper Python package structure

**Important:** Generated proto files in `chronoqueue/api/proto/` are **checked into version control**. This allows users to install the SDK without needing build tools. After running `make gen-proto`, commit the changes.

**Advanced Configuration:**

You can override the default repository, branch, or proto path:

```bash
# Use a different branch
CHRONOQUEUE_BRANCH=main make update-proto

# Use a fork or different repo
CHRONOQUEUE_REPO=youruser/chronoqueue make update-proto

# Use a different proto directory
CHRONOQUEUE_PROTO_PATH=api/proto make update-proto
```

### Regenerating Proto Files

If you modify proto definitions locally or want to regenerate from scratch:

```bash
make clean-all  # Remove all generated proto code
make gen-proto  # Regenerate with formatting
```

**Note on clean targets:**
- `make clean` - Removes build artifacts and cache (preserves generated proto code)
- `make clean-all` - Removes everything including generated proto code (use before regenerating)

## Testing

### Writing Tests

- Place test files in the `tests/` directory
- Name test files with `test_` prefix (e.g., `test_client.py`)
- Use pytest fixtures and markers appropriately
- Aim for high test coverage

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Run specific test file
poetry run pytest tests/test_client.py -v
```

## Pull Request Process

1. Update the README.md or documentation if needed
2. Ensure all tests pass and coverage is maintained
3. Update the CHANGELOG.md with notable changes
4. Request review from maintainers
5. Address any feedback from code review

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] Tests added/updated and passing
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated
- [ ] All CI checks passing
- [ ] Commit messages are clear and descriptive

## Commit Message Guidelines

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters
- Reference issues and pull requests after the first line

Examples:
```
Add support for async operations

- Implement async client methods
- Add tests for async functionality
- Update documentation

Closes #123
```

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards other community members

## Questions?

If you have questions, feel free to:
- Open an issue for discussion
- Reach out to maintainers
- Check existing documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
