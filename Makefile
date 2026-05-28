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
	docker compose run --rm backend python manage.py create-user $(username) $(password)

.PHONY: list-users
# list all users
list-users:
	docker compose run --rm backend python manage.py list-users

.PHONY: seed
# populate the database with sample data (~15 boxes, ~53 tubes)
seed:
	docker compose run --rm backend python manage.py seed

.PHONY: build-frontend
# compile the React app into dist/ (for production / PythonAnywhere)
build-frontend:
	docker compose run --rm frontend npm run build

# ── Dev tooling ──────────────────────────────────────────────────────────────
# Requires: make build (rebuilds backend-dev and frontend images with dev deps)

.PHONY: lint-backend
# lint the Python backend with ruff
lint-backend:
	docker compose --profile dev run --rm backend-dev ruff check sampling/

.PHONY: typecheck
# type-check the Python backend with mypy
typecheck:
	docker compose --profile dev run --rm backend-dev mypy sampling/

.PHONY: test-backend
# run Python backend tests with pytest
test-backend:
	docker compose --profile dev run --rm backend-dev pytest tests/ -v

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
# Usage: make pa-deploy PA_USER=<your-pythonanywhere-username>
PA_USER  ?= unset
PA_HOST   = ssh.pythonanywhere.com
PA_DIR    = /home/$(PA_USER)/sampling
PA_VENV   = $(PA_DIR)/venv/bin

.PHONY: _pa-check-user
_pa-check-user:
ifeq ($(PA_USER),unset)
	$(error PA_USER is not set — run: make <target> PA_USER=<your-pythonanywhere-username>)
endif

.PHONY: pa-pull
# pull latest code on PythonAnywhere
pa-pull: _pa-check-user
	ssh $(PA_USER)@$(PA_HOST) "cd $(PA_DIR) && git pull"

.PHONY: pa-build
# rebuild the React frontend on PythonAnywhere
pa-build: _pa-check-user
	ssh $(PA_USER)@$(PA_HOST) "cd $(PA_DIR) && npm run build"

.PHONY: pa-install
# install/update Python dependencies in the PythonAnywhere venv
pa-install: _pa-check-user
	ssh $(PA_USER)@$(PA_HOST) "$(PA_VENV)/pip install -r $(PA_DIR)/requirements.txt"

.PHONY: pa-reload
# reload the PythonAnywhere web app (triggers migration runner on next request)
pa-reload: _pa-check-user
	ssh $(PA_USER)@$(PA_HOST) "touch /var/www/$(PA_USER)_pythonanywhere_com_wsgi.py"

.PHONY: pa-deploy
# full deploy: pull → build → install → reload
pa-deploy: pa-pull pa-build pa-install pa-reload

.PHONY: pa-create-user
# create a user on PythonAnywhere: make pa-create-user PA_USER=<pa-user> username=<name> password=<pass>
pa-create-user: _pa-check-user
	ssh $(PA_USER)@$(PA_HOST) "cd $(PA_DIR) && $(PA_VENV)/python backend-src/manage.py create-user $(username) $(password)"

.PHONY: pa-list-users
# list users on PythonAnywhere
pa-list-users: _pa-check-user
	ssh $(PA_USER)@$(PA_HOST) "cd $(PA_DIR) && $(PA_VENV)/python backend-src/manage.py list-users"
