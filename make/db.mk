.PHONY: create-user
# create a user: make create-user username=<name> password=<pass>
create-user:
ifdef PYTHONANYWHERE_SITE
	venv/bin/python backend-src/manage.py create-user $(username) $(password)
else
	docker compose run --rm backend python manage.py create-user $(username) $(password)
endif

.PHONY: rename-user
# rename a user: make rename-user username=<name> new_username=<new-name>
rename-user:
ifdef PYTHONANYWHERE_SITE
	venv/bin/python backend-src/manage.py rename-user $(username) $(new_username)
else
	docker compose run --rm backend python manage.py rename-user $(username) $(new_username)
endif

.PHONY: delete-user
# delete a user: make delete-user username=<name>
delete-user:
ifdef PYTHONANYWHERE_SITE
	venv/bin/python backend-src/manage.py delete-user $(username)
else
	docker compose run --rm -it backend python manage.py delete-user $(username)
endif

.PHONY: list-users
# list all users
list-users:
ifdef PYTHONANYWHERE_SITE
	venv/bin/python backend-src/manage.py list-users
else
	docker compose run --rm backend python manage.py list-users
endif

.PHONY: reset-db
# delete all boxes, tubes, locations, and history — users are preserved
reset-db:
ifdef PYTHONANYWHERE_SITE
	venv/bin/python backend-src/manage.py reset-db
else
	docker compose run --rm -it backend python manage.py reset-db
endif

.PHONY: seed
# populate the database with sample data (~15 boxes, ~53 tubes)
seed:
ifdef PYTHONANYWHERE_SITE
	venv/bin/python backend-src/manage.py seed
else
	docker compose run --rm backend python manage.py seed
endif
