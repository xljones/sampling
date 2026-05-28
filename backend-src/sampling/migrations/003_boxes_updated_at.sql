ALTER TABLE boxes ADD COLUMN updated_at DATETIME;
UPDATE boxes SET updated_at = created_at;
