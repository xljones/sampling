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

CREATE TABLE cores (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    barcode          TEXT    UNIQUE NOT NULL,
    name             TEXT,
    location_id      INTEGER REFERENCES locations(id),
    latitude         REAL,
    longitude        REAL,
    site_name        TEXT,
    collection_date  DATE,
    depth_cm         REAL,
    collector        TEXT,
    sample_type      TEXT,
    owner            TEXT,
    notes            TEXT,
    created_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at       DATETIME DEFAULT CURRENT_TIMESTAMP
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
    core_id         INTEGER REFERENCES cores(id) ON DELETE SET NULL,
    sample_date     DATE,
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

CREATE TABLE core_history (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    core_id          INTEGER NOT NULL REFERENCES cores(id) ON DELETE CASCADE,
    changed_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
    changed_by       INTEGER REFERENCES users(id),
    barcode          TEXT,
    name             TEXT,
    location_id      INTEGER,
    latitude         REAL,
    longitude        REAL,
    site_name        TEXT,
    collection_date  TEXT,
    depth_cm         REAL,
    collector        TEXT,
    sample_type      TEXT,
    owner            TEXT,
    notes            TEXT
);

CREATE TABLE tube_history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    tube_id         INTEGER NOT NULL REFERENCES tubes(id) ON DELETE CASCADE,
    changed_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    changed_by      INTEGER REFERENCES users(id),
    barcode         TEXT,
    box_id          INTEGER,
    core_id         INTEGER,
    sample_date     TEXT,
    site_name       TEXT,
    latitude        REAL,
    longitude       REAL,
    sample_type     TEXT,
    description     TEXT,
    volume_ml       REAL,
    weight_g        REAL,
    depth_cm        REAL
);
