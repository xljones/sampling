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

CREATE TABLE box_history (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    box_id     INTEGER NOT NULL REFERENCES boxes(id) ON DELETE CASCADE,
    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    changed_by INTEGER REFERENCES users(id),
    barcode    TEXT,
    name       TEXT,
    location   TEXT,
    notes      TEXT
);
