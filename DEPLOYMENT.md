# Deployment — PythonAnywhere

## First-time setup

### 1. Clone the repo

Open a **Bash console** on PythonAnywhere and run:

```bash
git clone https://github.com/xljones/sampling.git
cd sampling
```

### 2. Build the frontend

Use the pre-built frontend in /dist, or:

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
venv/bin/python backend-src/manage.py create-user <username> <password>
```

To list existing users at any time:

```bash
venv/bin/python backend-src/manage.py list-users
```

### 5. Set the secret key

Edit `pa_wsgi.py` and replace the placeholder value with a real secret:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Then open `pa_wsgi.py` and set `SECRET_KEY` to that value:

```python
os.environ.setdefault("SECRET_KEY", "paste-your-generated-key-here")
```

> **Note:** `pa_wsgi.py` is committed to the repo with a placeholder. Edit it directly on PythonAnywhere after cloning — `make deploy-pa` will overwrite it, so re-apply your key after each deploy, or keep a local copy outside the repo.

### 6. Configure the web app

In the **PythonAnywhere Web tab**:

| Setting | Value |
|---|---|
| Source code | `/home/<you>/sampling` |
| Working directory | `/home/<you>/sampling` |
| Virtualenv | `/home/<you>/sampling/venv` |

**WSGI configuration file** — replace the entire contents with:

```python
import os, sys
sys.path.insert(0, os.path.join(os.environ["HOME"], "sampling", "backend-src"))
from wsgi import application
```

Or run `make deploy-pa` (see below) which copies `pa_wsgi.py` from the repo automatically.

### 7. Reload

Hit **Reload** in the Web tab. The app will be live at `https://<you>.pythonanywhere.com`.

The database is created automatically at `~/sampling/data/samples.db` on first request.

---

## Updating a deployment

From a **PythonAnywhere Bash console** inside `~/sampling`:

```bash
make deploy-pa
```

This pulls the latest `main`, installs any new Python dependencies, and copies `pa_wsgi.py` to the PythonAnywhere WSGI location — which triggers a reload.

Database migrations run automatically on the next request after reload.
