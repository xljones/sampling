# Deployment

## Local development

Requires Docker Desktop.

```bash
docker compose up
```

App runs at **http://localhost:5173**.

Source files (`app.py`, `sampling/`, `src/`) are bind-mounted so changes hot-reload without rebuilding. The SQLite database is written to `data/samples.db`.

To stop: `docker compose down`

**Create a user for local dev:**

```bash
docker compose run --rm backend python manage.py create-user <username> <password>
```

---

## PythonAnywhere

### 1. Clone the repo

Open a **Bash console** on PythonAnywhere and run:

```bash
git clone https://github.com/xljones/sampling.git
cd sampling
```

### 2. Build the frontend

```bash
npm install
npm run build
```

This produces the `dist/` directory that Flask serves as static files.

### 3. Set up the Python environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Create your user account

```bash
python manage.py create-user <username> <password>
```

To list existing users at any time:

```bash
python manage.py list-users
```

### 5. Generate a secret key

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output — you'll need it in the next step.

### 6. Configure the web app

In the **PythonAnywhere Web tab**:

| Setting | Value |
|---|---|
| Source code | `/home/<you>/sampling` |
| Working directory | `/home/<you>/sampling` |
| Virtualenv | `/home/<you>/sampling/venv` |

**WSGI configuration file** — replace the entire contents with:

```python
import sys
sys.path.insert(0, '/home/<you>/sampling/backend-src')
from wsgi import application
```

**Environment variables** — add:

```
SECRET_KEY   <the key you generated above>
FLASK_DEBUG  0
```

### 7. Reload

Hit **Reload** in the Web tab. The app will be live at `https://<you>.pythonanywhere.com`.

The database is created automatically at `~/sampling/data/samples.db` on first request.

---

## Updating a deployment

```bash
# Pull latest code
git pull

# Rebuild frontend if src/ changed
npm run build

# Apply any new database migrations
# (migrations run automatically on next app reload)
```

Then hit **Reload** in the PythonAnywhere Web tab.
