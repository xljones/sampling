from werkzeug.security import check_password_hash, generate_password_hash


class UserRepository:
    def __init__(self, db):
        self.db = db

    def get_by_id(self, user_id):
        r = self.db.execute(
            "SELECT id, username, is_readonly, expires_at, created_at FROM users WHERE id=?",
            (user_id,),
        ).fetchone()
        return dict(r) if r else None

    def get_by_username(self, username):
        r = self.db.execute(
            "SELECT * FROM users WHERE username = ? COLLATE NOCASE", (username,)
        ).fetchone()
        return dict(r) if r else None

    def list_all(self):
        return [
            dict(r) for r in self.db.execute(
                "SELECT id, username, is_readonly, expires_at, created_at FROM users ORDER BY created_at"
            ).fetchall()
        ]

    def create(self, username, password, is_readonly=False, expires_at=None):
        cur = self.db.execute(
            "INSERT INTO users (username, password_hash, is_readonly, expires_at) VALUES (?,?,?,?)",
            (username, generate_password_hash(password), int(is_readonly), expires_at),
        )
        return self.get_by_id(cur.lastrowid)

    def delete(self, user_id):
        return self.db.execute("DELETE FROM users WHERE id=?", (user_id,)).rowcount > 0

    def verify_password(self, username, password):
        user = self.get_by_username(username)
        if user and check_password_hash(user["password_hash"], password):
            return user
        return None
