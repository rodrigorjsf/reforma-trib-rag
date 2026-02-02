# AGENTS.md - Backend Development Guidelines

This document contains coding standards, conventions, and commands for agentic coding agents working in the backend Python application.

## Project Overview

**ReformaTax Backend** is a Python FastAPI application for Brazilian tax reform documentation and analysis. This codebase strictly follows [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/) for maintainable, readable Python code.

## Development Commands

```bash
# Run development server
uvicorn src.main:app --reload

# Run tests
pytest

# Run tests with coverage
pytest --cov=src

# Linting (uses ruff configured in pyproject.toml)
ruff check src/

# Format code
ruff format src/

# Type checking (if using mypy)
mypy src/

# Install dependencies
pip install -e .
```

**Important**: Always run `ruff check src/` and `pytest` after making changes to ensure code quality.

## Python PEP 8 Standards

This codebase strictly follows the official PEP 8 style guide. Key sections are highlighted below.

### Code Layout

#### Indentation
- **Use 4 spaces per indentation level**
- **Never use tabs** (spaces are the preferred method)
- **Hanging indents** should add 4 spaces extra level to distinguish continuation lines

```python
# Correct
def long_function_name(
        var_one, var_two, var_three,
        var_four):
    print(var_one)

# Wrong
def long_function_name(
    var_one, var_two,
    var_three, var_four):
    print(var_one)
```

#### Maximum Line Length
- **Limit all lines to 100 characters** (configured in pyproject.toml)
- **Docstrings/comments limited to 72 characters** when possible

#### Blank Lines
- **Two blank lines** surrounding top-level function and class definitions
- **One blank line** surrounding method definitions inside classes
- **Spare blank lines** to separate groups of related functions

#### Imports
- **Imports on separate lines** (never `import os, sys`)
- **Group imports in this order**:
  1. Standard library imports
  2. Related third-party imports
  3. Local application/library specific imports
- **Put a blank line between each group**
- **Use absolute imports** unless explicit relative imports are necessary

```python
# Correct
import os
import sys
from typing import Any, Dict, List

import fastapi
from pydantic import BaseModel

from src.models import User
from src.services.auth import AuthService
```

### Naming Conventions

#### Function and Variable Names
- **lowercase with underscores**: `function_name`, `variable_name`
- **Avoid single-character variable names** except for counters or iterators

#### Class Names
- **CapWords (CamelCase)**: `ClassName`, `ModelClass`
- **Exception classes** should end with "Error": `ValueError`, `CustomError`

#### Constants
- **ALL_CAPS_WITH_UNDERSCORES**: `MAX_OVERFLOW`, `TOTAL_COUNT`
- Defined at module level

#### Private Names
- **Single leading underscore**: `_internal_function` (weak internal use indicator)
- **Double leading underscore**: `__private_method` (name mangling in classes)

### String Quotes
- **Be consistent** within a project
- **Prefer single quotes** for strings
- **Use double quotes** when string contains single quotes to avoid escaping
- **Always use double quotes for docstrings** (PEP 257 convention)

```python
# Correct
single_quoted = 'This is a string'
double_quoted = "This contains a 'single quote'"

"""This is a docstring using triple double quotes."""
```

### Whitespace in Expressions

#### Avoid Extraneous Whitespace
- **No whitespace inside parentheses, brackets, or braces**: `spam(ham[1], {eggs: 2})`
- **No whitespace before comma, semicolon, or colon**: `if x == 4: print(x, y)`
- **No whitespace around = for keyword arguments**: `def complex(real, imag=0.0):`

#### Use Whitespace Around Binary Operators
- **Surround these operators with single spaces**: `=`, `+=`, `==`, `<`, `>`, `in`, `is`, `and`, `or`
- **For operators with different priorities**, consider adding whitespace around lowest priority operators

```python
# Correct
i = i + 1
submitted += 1
x = x*2 - 1
hypot2 = x*x + y*y
c = (a+b) * (a-b)

# Wrong
i=i+1
submitted +=1
x = x * 2 - 1
```

### Comments and Documentation

#### Comments
- **Comments should be complete sentences** starting with capital letter
- **Block comments** apply to code that follows, indented to same level
- **Inline comments** should be separated by at least two spaces
- **Write comments in English** for global audience projects

#### Docstrings
- **Write docstrings for all public modules, functions, classes, and methods**
- **Use triple double quotes**: `"""Docstring goes here"""`
- **One-line docstrings** keep closing quotes on same line: `"""Return an ex-parrot."""`
- **Multi-line docstrings** start summary on first line, blank line, then details

```python
def complex(real=0.0, imag=0.0):
    """Form a complex number.
    
    Keyword arguments:
    real -- the real part (default 0.0)
    imag -- the imaginary part (default 0.0)
    """
    return complex(real, imag)
```

## Programming Recommendations

### Comparison Operations
- **Always use `is` or `is not` for singletons**: `if foo is not None:`
- **Never compare boolean values to True/False**: `if greeting:` not `if greeting == True:`
- **Use isinstance() for type comparisons**: `if isinstance(obj, int):`
- **Use object identity testing with `is`**: `if seq is not None:`

### Exception Handling
- **Specific exceptions**: `except ImportError:` instead of bare `except:`
- **Limit try clause to minimum code necessary**
- **Use `raise X from Y` for exception chaining**
- **Derive exceptions from `Exception`**, not `BaseException`

```python
# Correct
try:
    value = collection[key]
except KeyError:
    return key_not_found(key)
else:
    return handle_value(value)

# Wrong - too broad
try:
    return handle_value(collection[key])
except KeyError:
    return key_not_found(key)  # Will also catch KeyError from handle_value()
```

### Resource Management
- **Use `with` statements for resources**: `with open('file.txt') as f:`
- **Context managers for cleanup operations**

### Return Statements
- **Be consistent**: all return statements should return an expression, or none should
- **If any return returns a value, all should explicitly return `None`** when no value is returned

```python
# Correct
def foo(x):
    if x >= 0:
        return math.sqrt(x)
    else:
        return None

# Correct
def bar(x):
    if x < 0:
        return None
    return math.sqrt(x)
```

## FastAPI Specific Patterns

### Route Definitions
- **Use type hints** for all parameters and return values
- **Use Pydantic models** for request/response validation
- **Follow RESTful conventions** for HTTP methods and endpoints

```python
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter()

class UserCreate(BaseModel):
    name: str
    email: str

@router.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Database = Depends(get_db)):
    """Create a new user."""
    return user_service.create(db, user)
```

### Dependency Injection
- **Use dependency injection** for database connections, authentication, etc.
- **Keep dependencies reusable** and testable

### Error Responses
- **Use HTTPException** for HTTP-specific errors
- **Custom exception handlers** for application-specific errors

## Testing Approach

This project uses pytest for testing following PEP 8 conventions.

### Test Structure
- **Test files**: `test_*.py` in `tests/` directory
- **Test functions**: `test_*` descriptive names
- **Use fixtures** for common setup/teardown
- **Follow AAA pattern**: Arrange, Act, Assert

```python
import pytest
from src.services.user_service import UserService

class TestUserService:
    def test_create_user_success(self, db_session):
        """Test successful user creation."""
        # Arrange
        user_data = {"name": "Test User", "email": "test@example.com"}
        service = UserService(db_session)
        
        # Act
        result = service.create_user(user_data)
        
        # Assert
        assert result.name == "Test User"
        assert result.email == "test@example.com"
```

## Configuration Files

### pyproject.toml
The project uses ruff for linting and formatting with PEP 8 compliance:
- **Line length**: 100 characters
- **Target Python**: 3.11+
- **Lint rules**: E, F, I, W (error, flake8, import sorting, warnings)

### Environment Variables
- **Use `.env` files** for local development
- **Never commit secrets** or API keys
- **Use pydantic-settings** for configuration management

## Security Considerations

- **Input validation**: Use Pydantic models for all inputs
- **SQL injection prevention**: Use ORM or parameterized queries
- **HTTPS in production**: Never serve sensitive data over HTTP
- **Rate limiting**: Implement for API endpoints
- **Authentication/authorization**: Proper user access controls

## Git Workflow

1. Create feature branches from main
2. Make atomic, focused commits following conventional commit format
3. Run `ruff check src/` and `pytest` before committing
4. Ensure all tests pass and code is properly formatted

## Common Anti-Patterns to Avoid

- ❌ **Mixed tabs and spaces**: Use 4 spaces consistently
- ❌ **Lines over 100 characters**: Break long lines appropriately
- ❌ **Bare except clauses**: Catch specific exceptions
- ❌ **Mutable default arguments**: Use None and check inside function
- ❌ **Wildcard imports**: Avoid `from module import *`
- ❌ **Comparisons to True/False**: Use boolean directly
- ❌ **Inconsistent naming**: Follow PEP 8 conventions
- ❌ **Missing docstrings**: Document public functions and classes

## Development Tips

- **Use editor integration** for real-time PEP 8 checking
- **Configure auto-formatting** with ruff format in your editor
- **Regular code reviews** to maintain style consistency
- **Use virtual environments** for dependency isolation

## When Working on This Codebase

1. Follow PEP 8 standards strictly
2. Use ruff for linting and formatting
3. Write comprehensive tests with pytest
4. Document all public APIs with proper docstrings
5. Ensure type hints are used throughout
6. Run full test suite before creating PRs
7. Keep functions focused and small
8. Use descriptive names following conventions

This codebase prioritizes readability, maintainability, and strict adherence to Python community standards through PEP 8 compliance.