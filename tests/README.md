# MurphyAI Bot Tests

This directory contains comprehensive tests for the MurphyAI Twitch bot.

## Test Structure

- `conftest.py` - Test configuration and shared fixtures
- `test_commands.py` - Tests for command handling functionality
- `test_utils.py` - Tests for utility functions
- `test_validation_utils.py` - Tests for input validation
- `test_queue_manager.py` - Tests for queue management
- `test_ai_command.py` - Tests for AI command functionality

## Running Tests

### Quick Start
```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
python run_tests.py

# Or use pytest directly
pytest
```

### Test Options

```bash
# Run with coverage
python run_tests.py --coverage

# Run only fast tests (skip slow integration tests)
python run_tests.py --type fast

# Run with verbose output
python run_tests.py --verbose

# Run specific test file
pytest tests/test_commands.py

# Run specific test
pytest tests/test_commands.py::TestCommandHandling::test_handle_penta
```

### Coverage Reports

When running with `--coverage`, HTML coverage reports are generated in `htmlcov/` directory.

## Test Environment

Tests use:
- Mock objects to simulate Twitch messages and bot instances
- Temporary directories for state file testing
- Environment variable overrides for safe testing
- Async test support for async functions

## Writing New Tests

1. Add test files with `test_` prefix
2. Use `TestClassName` for test classes
3. Use `test_function_name` for test methods
4. Use fixtures from `conftest.py` for common test objects
5. Mark slow tests with `@pytest.mark.slow`
6. Mark integration tests with `@pytest.mark.integration`

## Continuous Integration

These tests are designed to run in CI environments and include:
- No external dependencies during testing
- Deterministic behavior
- Proper cleanup of temporary files
- Clear error messages
