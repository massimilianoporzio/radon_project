# Radon Project 🌍

A Django-based monitoring application for radon concentration data with GeoDjango spatial capabilities.

## Status Badges

[![Django CI (PostGIS Ready)](https://github.com/massimilianoporzio/radon_project/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/massimilianoporzio/radon_project/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/massimilianoporzio/radon_project/branch/main/graph/badge.svg)](https://codecov.io/gh/massimilianoporzio/radon_project)
[![Markdown Formatting](https://img.shields.io/badge/markdown-mdformat-blue.svg)](https://mdformat.readthedocs.io/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Django 6.0 LTS](https://img.shields.io/badge/django-6.0%20LTS-darkgreen.svg)](https://docs.djangoproject.com/)
[![PostgreSQL 14](https://img.shields.io/badge/postgresql-14-336791.svg)](https://www.postgresql.org/)
[![PostGIS 3.3](https://img.shields.io/badge/postgis-3.3-003d5c.svg)](https://postgis.net/)

## Overview

Radon Project is a comprehensive Django application designed to monitor and manage radon concentration data across geographical regions. It leverages GeoDjango and PostGIS for advanced spatial analysis and visualization.

### Key Features

- 🗺️ **Spatial Data Management** - Built on GeoDjango with PostGIS for geographic data handling
- 📊 **Data Visualization** - Leaflet.js integration for interactive maps
- 🔐 **Secure Admin Interface** - Django admin with Unfold theme and read-only field protection
- 🧪 **Comprehensive Testing** - 90+ tests with 75%+ code coverage
- 🛡️ **Security First** - Automated security audits and vulnerability scanning
- 📱 **RESTful API** - DRF-based API with Swagger/Redoc documentation
- 🚀 **Continuous Integration** - GitHub Actions CI/CD with automated testing and security checks

## Project Structure

```
radon_project/
├── apps/
│   ├── territorio/          # Geographic territory data management
│   │   ├── models.py        # Territory models (GeoDjango)
│   │   ├── admin.py         # Admin interface
│   │   ├── views.py         # API endpoints
│   │   ├── tests/           # Test suite
│   │   └── migrations/      # Database migrations
│   └── users/               # User management
│       ├── models.py        # CustomUser model
│       ├── admin.py         # User admin interface
│       ├── tests/           # Test suite
│       └── migrations/      # Database migrations
├── config/                  # Django configuration
│   ├── settings/           # Settings modules (base, local, production)
│   ├── urls.py             # URL routing
│   └── wsgi.py             # WSGI application
├── static/                  # Static files (CSS, JS)
├── templates/               # HTML templates
├── pytest.ini              # Pytest configuration
├── pyproject.toml          # Project dependencies (uv)
└── manage.py               # Django management command
```

## Tech Stack

### Backend

- **Django 6.0 LTS** - Web framework
- **GeoDjango** - Spatial data support
- **PostGIS 3.3** - Spatial database extension
- **PostgreSQL 14** - Relational database
- **Django REST Framework** - API development
- **psycopg 3** - PostgreSQL driver

### Frontend

- **Leaflet.js** - Interactive mapping
- **Django Admin Unfold** - Enhanced admin interface

### Development & Testing

- **uv** - Python package manager
- **pytest** - Testing framework
- **pytest-django** - Django testing utilities
- **pytest-cov** - Coverage reporting
- **Ruff** - Linting and formatting
- **Pre-commit** - Git hooks for code quality

### Security & CI/CD

- **pip-audit** - Dependency vulnerability scanning
- **GitGuardian** - Secret scanning
- **Codecov** - Coverage tracking
- **GitHub Actions** - Continuous integration

## Installation

### Prerequisites

- Python 3.12+
- PostgreSQL 14+ with PostGIS 3.3+
- Git

### Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/massimilianoporzio/radon_project.git
   cd radon_project
   ```

2. **Install dependencies with uv**

   ```bash
   uv sync --all-extras --dev
   ```

3. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Set up database**

   ```bash
   uv run python manage.py migrate
   ```

5. **Create superuser**

   ```bash
   uv run python manage.py createsuperuser
   ```

6. **Run development server**

   ```bash
   uv run python manage.py runserver
   ```

Visit `http://localhost:8000/` to access the application.

## Testing

### Run all tests with coverage

```bash
uv run pytest --cov=apps --cov-report=html
```

### Run specific test module

```bash
uv run pytest apps/territorio/tests/
```

### Run with verbose output

```bash
uv run pytest -v
```

## Code Quality

### Linting

```bash
uv run ruff check .
```

### Format code

```bash
uv run ruff format .
```

### Security audit

```bash
uv run pip-audit
```

## Documentation

Additional documentation can be found in the `docs/` directory:

- `RADON_MAP_INTEGRATION.md` - Map integration details
- `LEAFLET_INTEGRATION.md` - Leaflet.js setup guide
- `GESTIONE_DATI_MANCANTI.md` - Missing data management

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes and ensure tests pass
3. Commit with clear messages: `git commit -am 'feat: add new feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

### Pre-commit hooks

The project uses pre-commit hooks to ensure code quality:

- Trailing whitespace check
- YAML validation
- TOML validation
- Ruff linting and formatting
- pip-audit security scanning

Install hooks:

```bash
uv run pre-commit install
```

## License

This project is proprietary and confidential.

## Support

For issues and questions, please open a GitHub issue or contact the development team.

______________________________________________________________________

**Made with ❤️ by the Radon Project Team (Massimiliano)**
