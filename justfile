# Justfile per Radon Project
# Installa just: https://github.com/casey/just
# Uso: just <comando>

# Mostra tutti i comandi disponibili
default:
    @just --list

# 🧪 Testing

# Esegui tutti i test con coverage
test:
    uv run pytest --cov=apps --cov-report=html

# Esegui test specifici
test-file file:
    uv run pytest {{file}}

# Esegui test con output verboso
test-verbose:
    uv run pytest -v

# Esegui test per un'app specifica (es: territorio, users)
test-app app:
    uv run pytest apps/{{app}}/tests/

# 🎨 Code Quality

# Esegui linting con ruff
lint:
    uv run ruff check .

# Esegui linting e correggi automaticamente
lint-fix:
    uv run ruff check --fix .

# Formatta il codice Python con ruff
format:
    uv run ruff format .

# Formatta tutti i file markdown
format-docs:
    @echo "🔍 Formattazione file markdown..."
    @uv run mdformat .github/copilot-instructions.md README.md docs/*.md
    @echo "✅ Formattazione completata!"

# Verifica formattazione markdown senza modificare
check-docs:
    @echo "🔍 Verifica formattazione markdown..."
    @uv run mdformat --check .github/copilot-instructions.md README.md docs/*.md

# Esegui tutti i controlli di qualità
quality: lint format format-docs
    @echo "✅ Tutti i controlli di qualità completati!"

# 🔒 Security

# Audit delle dipendenze per vulnerabilità
audit:
    uv run pip-audit

# 🗄️ Database

# Crea nuove migrazioni
makemigrations:
    uv run python manage.py makemigrations

# Applica le migrazioni
migrate:
    uv run python manage.py migrate

# Crea un superuser
createsuperuser:
    uv run python manage.py createsuperuser

# 🚀 Server

# Avvia il server di sviluppo
run:
    uv run python manage.py runserver

# Avvia il server su una porta specifica
run-port port:
    uv run python manage.py runserver {{port}}

# Raccogli i file statici
collectstatic:
    uv run python manage.py collectstatic --noinput

# 🧹 Cleanup

# Pulisci file cache Python
clean-pyc:
    find . -type f -name "*.pyc" -delete
    find . -type d -name "__pycache__" -delete

# Pulisci coverage reports
clean-cov:
    rm -rf htmlcov .coverage

# Pulisci tutto (cache, coverage, etc)
clean: clean-pyc clean-cov
    @echo "🧹 Pulizia completata!"

# 📦 Dependencies

# Sincronizza dipendenze
sync:
    uv sync --all-extras --dev

# Aggiorna dipendenze
update:
    uv sync --upgrade --all-extras --dev

# 🔧 Pre-commit

# Installa pre-commit hooks
install-hooks:
    uv run pre-commit install

# Esegui pre-commit su tutti i file
pre-commit-all:
    uv run pre-commit run --all-files

# 🚢 CI/CD Simulation

# Simula la CI pipeline localmente
ci: lint test audit check-docs
    @echo "✅ CI simulation completata con successo!"

# 📊 Coverage

# Apri il report di coverage nel browser
coverage-report:
    @echo "📊 Apertura report coverage..."
    @start htmlcov/index.html

# 🎯 Workflow comuni

# Prepara per commit: quality checks + tests
pre-push: quality test
    @echo "✅ Pronto per il push!"

# Setup completo del progetto
setup: sync install-hooks migrate
    @echo "✅ Setup completato!"
    @echo "💡 Crea un superuser con: just createsuperuser"
    @echo "🚀 Avvia il server con: just run"
