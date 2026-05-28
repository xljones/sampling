CREATE TABLE locations (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

ALTER TABLE boxes ADD COLUMN location_id INTEGER REFERENCES locations(id);
ALTER TABLE boxes DROP COLUMN location;

ALTER TABLE box_history ADD COLUMN location_id INTEGER REFERENCES locations(id);
ALTER TABLE box_history DROP COLUMN location;
