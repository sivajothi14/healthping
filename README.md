# Healthchecks

Healthchecks is a Django service for monitoring cron jobs, scheduled tasks, and
other recurring work. A check receives a ping before its deadline; if the ping
is late or missing, Healthchecks can notify your team through its integrations.

## What is included

- Web dashboard and HTTP API
- Check schedules, grace periods, pauses, logs, and status badges
- Team projects and role-based access
- WebAuthn two-factor authentication
- Notifications through email, chat, paging, SMS, and webhooks
- Self-hosted SQLite, PostgreSQL, MySQL, and MariaDB support

## Requirements

- Python 3.12 or newer
- A supported database (SQLite is convenient for local development)
- System libraries required by `pycurl` and your selected database driver

## Local development

Create and activate a virtual environment, then install the dependencies:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt -r requirements-dev.txt
```

Initialize the local database and start Django:

```sh
python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000/`. The default development settings use SQLite,
enable debug mode, and allow registration. Set `SECRET_KEY` before running in
any shared or production environment.

## Configuration

Settings are read from environment variables. Common deployment variables are:

| Variable | Purpose |
| --- | --- |
| `SECRET_KEY` | Django signing key; required for a real deployment |
| `DB` | Select `sqlite`, `postgres`, `mysql`, or `mariadb` |
| `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | Database connection settings |
| `SITE_ROOT` | Public base URL of the installation |
| `DEBUG` | Use `True` only for local development |
| `DEFAULT_FROM_EMAIL` | Sender address for system email |
| `HC_VERSION` | Optional version label displayed by the application |

See `hc/settings.py` for the complete set of supported options.

## Tests and checks

Run the test suite with:

```sh
python manage.py test
```

Run type checking with:

```sh
mypy hc
```

The documentation pages are shipped as pre-rendered HTML fragments under
`templates/docs`. The search index can be rebuilt with:

```sh
python manage.py populate_searchdb
```

## Docker

The `docker/` directory contains the production image definition and uWSGI
configuration. Build and run it with your preferred database and environment
configuration:

```sh
docker build -f docker/Dockerfile -t healthchecks .
docker run --env-file .env -p 8000:8000 healthchecks
```

Use a persistent volume for application data when running SQLite, or use an
external PostgreSQL, MySQL, or MariaDB database for production workloads.
