# HealthPing

HealthPing is a Django-based monitoring service for cron jobs, scheduled tasks,
and recurring background work. Jobs send HTTP pings to their checks, and the
service alerts when a ping is late or missing.

## Features

- Dashboard for checks, schedules, logs, and status badges
- HTTP ping and management APIs
- Project-based access control and team members
- Email, chat, paging, SMS, and webhook integrations
- WebAuthn two-factor authentication
- SQLite, PostgreSQL, MySQL, and MariaDB support
- Docker deployment configuration

## Requirements

- Python 3.12+
- SQLite for local development, or PostgreSQL/MySQL/MariaDB for deployment
- System libraries required by `pycurl` and the selected database driver

## Local setup

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt -r requirements-dev.txt
python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000/` after starting the development server.

## Configuration

Configuration is provided through environment variables. Common settings include:

| Variable | Purpose |
| --- | --- |
| `SECRET_KEY` | Django signing key |
| `DEBUG` | Enable development mode with `True` |
| `SITE_ROOT` | Public URL of the installation |
| `DB` | `sqlite`, `postgres`, `mysql`, or `mariadb` |
| `DB_HOST` | Database hostname |
| `DB_NAME` | Database name or SQLite path |
| `DB_USER` | Database username |
| `DB_PASSWORD` | Database password |
| `HC_VERSION` | Optional application version label |

See `hc/settings.py` and `docker/.env.example` for the available configuration
options.

## Tests and quality checks

```sh
python manage.py test
mypy hc
```

## Docker

Build the image from the repository root:

```sh
docker build -f docker/Dockerfile -t healthping .
docker run --env-file docker/.env -p 8000:8000 healthping
```

For production, use persistent storage and an external database. The
`docker/docker-compose.yml` file provides a PostgreSQL-based setup.

## Project layout

- `hc/` — Django application, APIs, models, integrations, and utilities
- `templates/` — HTML templates and rendered documentation fragments
- `static/` — CSS, JavaScript, fonts, and images
- `docker/` — container image and deployment configuration
- `.github/workflows/` — automated tests, type checks, and image publishing
