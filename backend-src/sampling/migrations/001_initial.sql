CREATE TABLE locations (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    UNIQUE NOT NULL,
    password_hash TEXT    NOT NULL,
    is_readonly   INTEGER NOT NULL DEFAULT 0,
    expires_at    TEXT,
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE boxes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    barcode     TEXT    UNIQUE NOT NULL,
    name        TEXT,
    location_id INTEGER REFERENCES locations(id),
    notes       TEXT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tubes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    barcode         TEXT    UNIQUE NOT NULL,
    box_id          INTEGER REFERENCES boxes(id) ON DELETE SET NULL,
    collection_date DATE,
    site_name       TEXT,
    latitude        REAL,
    longitude       REAL,
    sample_type     TEXT,
    description     TEXT,
    volume_ml       REAL,
    weight_g        REAL,
    depth_cm        REAL,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE box_history (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    box_id      INTEGER NOT NULL REFERENCES boxes(id) ON DELETE CASCADE,
    changed_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    changed_by  INTEGER REFERENCES users(id),
    barcode     TEXT,
    name        TEXT,
    location_id INTEGER REFERENCES locations(id),
    notes       TEXT
);

CREATE TABLE tube_history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    tube_id         INTEGER NOT NULL REFERENCES tubes(id) ON DELETE CASCADE,
    changed_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    changed_by      INTEGER REFERENCES users(id),
    barcode         TEXT,
    box_id          INTEGER,
    collection_date TEXT,
    site_name       TEXT,
    latitude        REAL,
    longitude       REAL,
    sample_type     TEXT,
    description     TEXT,
    volume_ml       REAL,
    weight_g        REAL,
    depth_cm        REAL
);
