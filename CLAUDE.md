# Sediment Sample Catalogue — Claude Context

## Tech stack

| Layer | Tech |
|---|---|
| Backend | Python 3.14, Flask, SQLite (`better-sqlite3` via built-in `sqlite3`) |
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
  domain/            Plain dataclasses: Box, Tube, User
  repositories/      BoxRepository, TubeRepository, UserRepository — own all SQL
  routes/            Flask Blueprints: boxes, tubes, scan, export, auth
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
                     TubeDetail, TubeForm, ScanPage, LoginPage
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
```

The database is at `data/samples.db` (bind-mounted into the backend container).

## Key conventions

- Commit format: `feat/fix/chore(component): one-line description`
- Small, focused commits — never bulk everything together
- Never commit or push without explicit instruction
- Backend changes that don't touch `requirements.txt` or `Dockerfile.backend` hot-reload via the bind mount — no rebuild needed
- Frontend changes hot-reload via Vite — no rebuild needed
