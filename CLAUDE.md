# FlacJacket Development Guide

## Build Commands
- **Backend**: `docker compose exec backend flask run`
- **Frontend**: `docker compose exec frontend npm run dev`
- **Full stack**: `docker compose up --build`

## Test Commands
- **Run all tests**: `docker compose exec backend pytest`
- **Run specific test**: `docker compose exec backend pytest tests/test_audio_analysis.py::test_soundcloud_track_analysis -v`
- **API tests**: `docker compose exec backend pytest tests/test_api.py`
- **Frontend tests**: `docker compose exec frontend npm test`

## Lint Commands
- **Backend**: No specific linter configured (follow PEP 8)
- **Frontend**: `docker compose exec frontend npm run lint`

## Code Style Guidelines
- **Python**: Follow PEP 8 guidelines
  - Group imports: stdlib, third-party, local
  - Use docstrings for classes and functions
  - Use type hints where appropriate
  
- **JavaScript/TypeScript**: 
  - Follow Airbnb style guide
  - Use ESLint and Prettier for formatting
  - Prefer TypeScript interfaces for complex types
  
- **Naming Conventions**:
  - Python: snake_case for variables/functions, PascalCase for classes
  - JS/TS: camelCase for variables/functions, PascalCase for components/classes
  
- **Error Handling**:
  - Use try/except blocks with specific exceptions in Python
  - Use structured logging with context information
  - Handle API errors with appropriate status codes