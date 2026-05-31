# Sediment Sample Catalogue

[![CI](https://github.com/xljones/sampling/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/xljones/sampling/actions/workflows/ci.yml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A local web app for cataloguing sediment samples. Tubes are stored in boxes; cores are standalone sediment column samples. All entities are identified by barcodes.

## Features

- **Boxes & tubes** — create, view, inline-edit, and delete with full metadata
- **Version history** — every save is snapshotted; revert any box or tube to a previous version
- **Barcode input** — USB scanner (keyboard wedge), camera scan, or manual entry
- **Camera scanner** — auto-detects front/rear camera and corrects mirroring
- **GPS & map** — latitude/longitude on tubes with a pick-on-map tool and Leaflet map view
- **Export** — CSV and TSV export; boxes and cores export hierarchically with their tubes; single-item export from detail pages
- **Search** — filter by barcode, site, type, or location
- **Authentication** — session-based login; users stored in SQLite

## Running locally

Requires [Docker Desktop](https://www.docker.com/products/docker-desktop/).

```bash
# Start the app
make run

# Create a user account
make create-user username=you password=yourpassword

# Populate with sample data
make seed

# Reset all data except users
make reset-db

# View logs
make logs

# Stop
make stop
```

App runs at **http://localhost:5173**.

## Project structure

```
backend-src/           Python backend
  app.py               Entry point
  manage.py            CLI (create-user, list-users, seed, reset-db)
  wsgi.py              PythonAnywhere WSGI entry point
  sampling/
    __init__.py        App factory
    db.py              Connection + migration runner
    migrations/        Versioned SQL files
    domain/            Box, Tube, User dataclasses
    repositories/      All SQL per entity
    routes/            Flask Blueprints (boxes, cores, tubes, scan, export, auth, locations, users)

frontend-src/          React + Vite frontend
  App.jsx              Router and auth shell
  AuthContext.jsx      Session state
  api.js               Fetch wrapper
  components/          One file per page/component

data/                  SQLite database (gitignored)
dist/                  Built frontend (gitignored)
```

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for PythonAnywhere setup instructions.
