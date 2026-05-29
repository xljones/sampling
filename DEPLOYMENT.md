# Deployment — PythonAnywhere

## First-time setup

### 1. Clone the repo

Open a **Bash console** on PythonAnywhere and clone the **`deploy` branch**, which always contains the latest built frontend:

```bash
git clone --branch deploy https://github.com/xljones/sampling.git
cd sampling
```

The `deploy` branch mirrors `main` and includes the pre-built `dist/` directory. It is rebuilt and force-pushed automatically by CI on every push to `main`.

### 2. Set up the Python environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Create your user account

```bash
make create-user username=<username> password=<password>
```

To list existing users at any time:

```bash
make list-users
```

### 4. Create the `.env` file

```bash
echo "SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')" > .env
echo "FLASK_DEBUG=0" >> .env
```

This file is gitignored and will not be overwritten by `make deploy-pa`.

### 5. Configure the web app

In the **PythonAnywhere Web tab**:

| Setting | Value |
|---|---|
| Source code | `/home/<you>/sampling` |
| Working directory | `/home/<you>/sampling` |
| Virtualenv | `/home/<you>/sampling/venv` |

**WSGI configuration file** — replace the entire contents with the contents of `pa_wsgi.py` from the repo.

### 6. Reload

Hit **Reload** in the Web tab. The app will be live at `https://<you>.pythonanywhere.com`.

The database is created automatically at `~/sampling/data/samples.db` on first request.

---

## Updating a deployment

From a **PythonAnywhere Bash console** inside `~/sampling`:

```bash
make deploy-pa
```

This switches to the `deploy` branch, pulls the latest changes (including the freshly built `dist/`), and installs any new Python dependencies. Reload the web app from the PythonAnywhere Web tab to apply the changes.

Database migrations run automatically on the next request after reload.

---

## Database management

All commands below work on both PythonAnywhere and locally — they auto-detect the environment.

```bash
make seed         # populate with sample data (~15 boxes, ~53 tubes)
make reset-db     # delete all boxes, cores, tubes, locations, and history (users kept)
make create-user username=x password=y
make list-users
```
