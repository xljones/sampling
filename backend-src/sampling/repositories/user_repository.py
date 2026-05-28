from werkzeug.security import check_password_hash, generate_password_hash


class UserRepository:
    def __init__(self, db):
        self.db = db

    def get_by_id(self, user_id):
        r = self.db.execute(
            "SELECT id, username, created_at FROM users WHERE id=?", (user_id,)
        ).fetchone()
        return dict(r) if r else None

    def get_by_username(self, username):
        r = self.db.execute(
            "SELECT * FROM users WHERE username=?", (username,)
        ).fetchone()
        return dict(r) if r else None

    def create(self, username, password):
        cur = self.db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?,?)",
            (username, generate_password_hash(password)),
        )
        return self.get_by_id(cur.lastrowid)

    def verify_password(self, username, password):
        user = self.get_by_username(username)
        if user and check_password_hash(user["password_hash"], password):
            return {"id": user["id"], "username": user["username"]}
        return None
