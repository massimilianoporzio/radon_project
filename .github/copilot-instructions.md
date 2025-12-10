# Copilot Code Review Instructions

## Review Standards

Review all pull requests automatically on every push.

### Code Quality Guidelines

1. **Django Best Practices**

   - Check for proper use of Django ORM
   - Validate model structure and migrations
   - Ensure settings are properly configured

1. **Testing Requirements**

   - Verify test coverage is >= 75%
   - Check pytest assertions are comprehensive
   - Validate GeoDjango spatial data handling

1. **Security**

   - Check for SQL injection vulnerabilities
   - Validate input handling
   - Review authentication/authorization code
   - Ensure no hardcoded secrets

1. **Python Code Quality**

   - Follow PEP 8 standards
   - Check for unused imports
   - Validate type hints where applicable
   - Review error handling

1. **Git & Refactoring**

   - Ensure migration consistency
   - Validate import path updates during refactoring
   - Check for breaking changes

## Focus Areas for This Project

- GeoDjango spatial operations (PostGIS)
- API endpoint validation (tolerance parameter constraints)
- Admin interface customization
- User model and authentication
- Test database setup (PostGIS extensions)

## Severity Levels

- **Critical**: Security issues, breaking changes, test failures
- **Major**: Code quality, performance issues, missing tests
- **Minor**: Style, documentation, naming conventions
