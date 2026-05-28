#!/usr/bin/env python3
"""Management CLI. Usage: python manage.py <command> [args]"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def cmd_create_user(args):
    if len(args) != 2:
        print("Usage: python manage.py create-user <username> <password>")
        sys.exit(1)
    username, password = args
    from sampling.db import get_db
    from sampling.repositories.user_repository import UserRepository
    with get_db() as db:
        repo = UserRepository(db)
        if repo.get_by_username(username):
            print(f"Error: user '{username}' already exists")
            sys.exit(1)
        repo.create(username, password)
    print(f"User '{username}' created.")


def cmd_list_users(_):
    from sampling.db import get_db
    with get_db() as db:
        users = db.execute("SELECT id, username, created_at FROM users ORDER BY id").fetchall()
    if not users:
        print("No users.")
    for u in users:
        print(f"  [{u[0]}] {u[1]}  (created {u[2]})")


COMMANDS = {
    "create-user": cmd_create_user,
    "list-users":  cmd_list_users,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(f"Available commands: {', '.join(COMMANDS)}")
        sys.exit(1)
    COMMANDS[sys.argv[1]](sys.argv[2:])
