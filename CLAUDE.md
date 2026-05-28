# Sediment Sample Catalogue — Claude Context

## Tech stack

| Layer | Tech |
|---|---|
| Backend | Python 3.14, Flask, SQLite (built-in `sqlite3`) |
| Frontend | React 18, Vite, React Router |
| Auth | Flask sessions + `werkzeug.security` password hashing |
| Dev environment | Docker Compose (two services: `backend`, `frontend`) |

## Architecture

### Backend (`backend-src/`)

DDD-inspired layering — routes never write SQL directly.

```
sampling/
  __init__.py        create_app() factory; registers blueprints, before_request auth guard
  db.py              get_db(), run_migrations() — migration runner reads migrations/*.sql
  migrations/        Numbered SQL files (001_initial.sql, 002_add_users.sql, …)
  domain/            Plain dataclasses: Box, Tube, User, Location
  repositories/      BoxRepository, TubeRepository, UserRepository, LocationRepository — own all SQL
  routes/            Flask Blueprints: boxes, tubes, scan, export, auth, locations
```

- **Adding a schema change:** drop a new `NNN_description.sql` in `migrations/`. It runs automatically on next startup and is recorded in `schema_migrations`.
- **Adding an endpoint:** add a method to the relevant repository, call it from the relevant blueprint.
- **Auth:** all `/api/*` routes except `/api/auth/*` require a valid session (`user_id` in Flask session). Enforced in `before_request` in `__init__.py`.

### Frontend (`frontend-src/`)

```
App.jsx              Shell: checks auth state, renders LoginPage or the main layout
AuthContext.jsx      Provides user, login(), logout() via React context
api.js               Thin fetch wrapper; all calls use credentials: 'include'
components/          One file per page: Dashboard, BoxList, BoxDetail, TubeList,
                     TubeDetail, TubeForm, ScanPage, LoginPage, LocationList
                     Shared: BarcodeInput, CameraScanner, Toast
```

- **BarcodeInput** — composes manual text input + camera toggle; USB scanners work natively as keyboard wedge.
- **CameraScanner** — lazy-loaded; starts camera immediately on mount (triggers browser permission), enumerates devices after permission granted, auto-detects front/rear for mirror correction.

## Running locally

```bash
make run          # start both services
make stop         # stop
make logs         # tail logs (make logs service=backend for one service)
make build        # rebuild images (needed after requirements.txt or Dockerfile changes)
make create-user username=x password=y
make list-users
make seed         # populate with sample data (~15 boxes, ~53 tubes)
make reset-db     # delete all boxes, tubes, locations, and history (users kept)
```

The database is at `data/samples.db` (bind-mounted into the backend container).

## PythonAnywhere deployment

```bash
make deploy-pa    # pull latest, create venv if needed, install deps
make create-user username=x password=y
make list-users
make seed
make reset-db
```

`make create-user`, `make list-users`, `make seed`, and `make reset-db` auto-detect the environment: on PythonAnywhere they run via `venv/bin/python backend-src/manage.py` directly; locally they use Docker. Detection relies on `PYTHONANYWHERE_SITE`, an env var PythonAnywhere injects automatically into every console and web process (set to your site's domain, e.g. `username.pythonanywhere.com`).

## Key conventions

- Commit format: `feat/fix/chore(component): one-line description`
- Small, focused commits — never bulk everything together
- Never commit or push without explicit instruction
- Backend changes that don't touch `requirements.txt` or `Dockerfile.backend` hot-reload via the bind mount — no rebuild needed
- Frontend changes hot-reload via Vite — no rebuild needed
