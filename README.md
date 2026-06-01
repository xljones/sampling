# Sediment Sample Catalogue

[![CI](https://github.com/xljones/sampling/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/xljones/sampling/actions/workflows/ci.yml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A web app for cataloguing sediment samples. **Cores** are sediment column samples taken in the field; **tubes** are sub-samples taken from a core (or standalone field samples) and stored in **boxes**. All entities are identified by barcodes.

## Features

- **Cores, boxes & tubes** — create, view, inline-edit, and delete with full metadata
- **Version history** — every save of a core, box, or tube is snapshotted; revert to a previous version at any time
- **Barcode input** — USB scanner (keyboard wedge), camera scan, or manual entry
- **Camera scanner** — auto-detects front/rear camera and corrects mirroring
- **GPS & maps** — latitude/longitude on cores and tubes, with a pick-on-map tool and Leaflet map views (tubes inherit coords from their core unless overridden)
- **Storage locations** — named locations with optional coordinates; reusable across boxes and cores
- **Export** — CSV, TSV, JSON, and GeoJSON; boxes and cores export hierarchically with their tubes; single-item export from detail pages
- **Search** — filter by barcode, site, type, or location
- **Users & roles** — session login (Flask-Login); admins, normal users, read-only users, and optional account expiry
- **Admin panel** — manage users; view live PythonAnywhere CPU, web app, and scheduled task info

## Running locally

Requires [Docker Desktop](https://www.docker.com/products/docker-desktop/).

```bash
# Start the app
make run

# Create your first user (use create-admin for an admin account)
make create-user username=you password=yourpassword

# Populate with sample data (~15 boxes, 4 cores, ~55 tubes)
make seed

# Drop all tables — including users (interactive confirm)
make reset-db

# View logs (optionally: make logs service=backend)
make logs

# Stop
make stop
```

App runs at **http://localhost:5173**.

### Dev tooling

```bash
make test           # lint + typecheck + test (backend & frontend) — mirrors CI
make format         # ruff format the backend
make build-frontend # compile the React app into dist/
```

See `make/` for the full set of targets (database backup/restore, user management, individual lint/test steps, etc.).

## Project structure

```
backend-src/           Python backend
  app.py               Local dev entry point
  manage.py            CLI (create-user, migrate, seed, db-backup, db-restore, …)
  wsgi.py              WSGI entry point (used by pa_wsgi.py)
  sampling/
    __init__.py        App factory (Flask-Login, before_request auth/expiry/readonly guard)
    db.py              Connection + migration runner
    migrations/        Versioned SQL files
    domain/            Box, Core, Tube, User, Location dataclasses
    repositories/      All SQL per entity
    routes/            Flask Blueprints (admin, auth, boxes, cores, tubes,
                       scan, export, locations, users)

frontend-src/          React + Vite frontend
  App.jsx              Router and auth shell (sidebar + bottom nav)
  AuthContext.jsx      Session state
  api.js               Fetch wrapper
  constants.js         Shared frontend constants
  styles/              Per-concern CSS modules
  components/          One file per page/component (includes admin UserList + PythonAnywhereStats)

make/                  Modular Makefile (local, db, test, deploy)
scripts/               Deploy/build helper scripts
pa_wsgi.py             PythonAnywhere WSGI shim (loads .env, imports backend-src/wsgi.py)
pyproject.toml         Ruff, mypy, pytest config; project version

data/                  SQLite database (gitignored)
dist/                  Built frontend (gitignored)
```

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for PythonAnywhere setup instructions.
