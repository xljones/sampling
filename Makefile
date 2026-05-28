.PHONY: build
# build docker images
build:
	docker compose build

.PHONY: run
# start all services (detached)
run:
	docker compose up --force-recreate --detach --remove-orphans

.PHONY: stop
# stop all services
stop:
	docker compose down

.PHONY: logs
# follow logs (optionally: make logs service=backend)
logs:
	docker compose logs -f $(service)

.PHONY: create-user
# create a user: make create-user username=<name> password=<pass>
create-user:
ifdef PYTHONANYWHERE_SITE
	venv/bin/python backend-src/manage.py create-user $(username) $(password)
else
	docker compose run --rm backend python manage.py create-user $(username) $(password)
endif

.PHONY: list-users
# list all users
list-users:
ifdef PYTHONANYWHERE_SITE
	venv/bin/python backend-src/manage.py list-users
else
	docker compose run --rm backend python manage.py list-users
endif

.PHONY: seed
# populate the database with sample data (~15 boxes, ~53 tubes)
seed:
ifdef PYTHONANYWHERE_SITE
	venv/bin/python backend-src/manage.py seed
else
	docker compose run --rm backend python manage.py seed
endif

.PHONY: build-frontend
# compile the React app into dist/ (for production / PythonAnywhere)
build-frontend:
	docker compose run --rm frontend npm run build

# ── Dev tooling ──────────────────────────────────────────────────────────────
# Requires: make build (rebuilds backend image with dev deps)

.PHONY: lint-backend
# lint the Python backend with ruff
lint-backend:
	docker compose run --rm backend ruff check sampling/

.PHONY: typecheck
# type-check the Python backend with mypy
typecheck:
	docker compose run --rm backend mypy sampling/

.PHONY: test-backend
# run Python backend tests with pytest
test-backend:
	docker compose run --rm backend pytest tests/ -v

.PHONY: lint-frontend
# lint the frontend with eslint
lint-frontend:
	docker compose run --rm frontend npm run lint

.PHONY: test-frontend
# run frontend tests with vitest
test-frontend:
	docker compose run --rm frontend npm run test

.PHONY: lint
# lint backend and frontend
lint: lint-backend lint-frontend

.PHONY: test
# test backend and frontend
test: test-backend test-frontend

# ── PythonAnywhere deployment ────────────────────────────────────────────────
# Run from a PythonAnywhere Bash console inside ~/sampling

.PHONY: deploy-pa
# pull latest main, create venv if needed, install deps
deploy-pa:
	git fetch origin && git checkout main && git pull origin main
	[ -d venv ] || python3 -m venv venv
	venv/bin/pip install -r requirements.txt
