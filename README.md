# Sediment Sample Catalogue

A local web app for cataloguing sediment samples. Samples are stored in tubes, tubes are stored in boxes, and both are identified by barcodes.

## Features

- **Boxes & tubes** — create, view, edit, and delete with full metadata
- **Barcode input** — USB scanner (keyboard wedge), camera scan, or manual entry
- **Camera scanner** — auto-detects front/rear camera and corrects mirroring
- **CSV export** — export all boxes or tubes to CSV
- **Search** — filter by barcode, site, type, or location
- **Authentication** — session-based login; users stored in SQLite

## Running locally

Requires [Docker Desktop](https://www.docker.com/products/docker-desktop/).

```bash
# Start the app
make run

# Create a user account
make create-user username=you password=yourpassword

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
  manage.py            CLI (create-user, list-users)
  wsgi.py              PythonAnywhere WSGI entry point
  sampling/
    __init__.py        App factory
    db.py              Connection + migration runner
    migrations/        Versioned SQL files
    domain/            Box, Tube, User dataclasses
    repositories/      All SQL per entity
    routes/            Flask Blueprints (boxes, tubes, scan, export, auth)

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
