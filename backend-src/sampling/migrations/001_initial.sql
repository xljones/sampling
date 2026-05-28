CREATE TABLE boxes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    barcode     TEXT    UNIQUE NOT NULL,
    name        TEXT,
    location    TEXT,
    notes       TEXT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
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
