# Changelog

## [1.0.0] — 2026-05-xx

### Added
- `make migrate` command to apply pending database migrations without a full restart
- PythonAnywhere scheduled tasks listed in the admin deployment panel
- Webapp expiry date and Python version shown with relative time in admin panel
- CI workflow to auto-renew PythonAnywhere extension on a schedule

### Changed
- Backend package renamed from `sampling` to `dirtnap`
- App renamed to **Dirt Nap** across README, CLAUDE.md, and DEPLOYMENT.md

---

## [0.4.2] — 2026-04

### Added
- PythonAnywhere CPU/web app stats panel under `/admin`
- Role badges (Admin, Read-only) displayed in the sidebar
- ComboInput combo search replaces the scan/list toggle on scan page

### Fixed
- CPU reset time now shown in minutes/hours/days instead of raw seconds
- Read-only users can now log out
- Consistent button sizes and wider content area across detail pages
- Admin scheduled-task status dot aligned vertically with first line of text

### Changed
- Camera emoji replaced with Font Awesome solid camera SVG
- Scan/form mode strings replaced with `InputMode`/`FormMode` enums

---

## [0.4.1] — 2026-03

### Added
- Admin role: created via `make create-admin`; full user management UI at `/admin`
- `make db-backup` and `make db-restore` commands

### Fixed
- `reset-db` now always drops all tables including the users table

---

## [0.4.0] — 2026-03

### Added
- Skeleton loaders on all list pages, detail pages, and dashboard stat cards
- `CoreForm` page for creating new core records from the UI
- Scan page: option to register an unrecognised barcode as a new core
- Box detail map falls back to parent core coordinates when a tube has no own coords

### Fixed
- Missing `useEffect` dependencies in BoxDetail and CoreDetail
- Removed unused delete handlers from list pages

---

## [0.3.x] — 2026-02

### Added
- **Cores model**: full CRUD, edit history with revert, and linkage to tubes
- Core list and detail views; cores shown on box detail page
- Tube detail shows inherited core depth and cross-highlighting in the depth diagram
- Export: hierarchical CSV/TSV with nested cores/tubes; single-item export on box and core detail pages
- Export dropdown: JSON and GeoJSON formats with nested structure; GeoJSON note on flat-only limitation
- Dashboard map: coloured markers distinguish cores from coreless tubes
- Tubes with their own coordinates shown in green on the dashboard map
- Relative timestamps with UTC tooltip on hover (`RelativeTime` component)
- DNA helix logo replaces sediment logo; sidebar grass decoration; DNA favicon
- `CoordCard` component extracted from map views
- Map picker always visible in edit mode; pin syncs to manual coordinate input changes
- `ExportDropdown` supports dividers and checkboxes (e.g. nested export toggle)

### Fixed
- Deterministic history ordering; `is_readonly` correctly typed as bool
- Map legend CSS scoped to iframe to avoid bleeding into page styles
- `sample_date` field consistently named across backend and frontend (was `collection_date`)

---

## [0.2.1] — 2026-01

### Added
- Version number and git SHA baked into the frontend build; live indicator shown in dev mode
- Version shown on login page
- Deploy summary prints version, dist SHA, and build info
- CI tests against Python 3.10 and 3.14 in parallel

### Fixed
- Python 3.10 compatibility: `datetime.UTC` → `timezone.utc`; `tomllib` guard for older Pythons
- `pyproject.toml` mounted into Docker container to fix missing-file error on macOS
- Deploy uses `reset --hard` instead of `pull` to prevent stale merge commits on PythonAnywhere

---

## [0.1.0] — 2025-12

### Added
- **Read-only user accounts** with optional TTL; account expiry enforced on every request
- Users can change their own password from the Account page
- Admin can rename and delete users
- **Locations** model: boxes and tubes can reference a named location; location detail shows linked cores and boxes
- Responsive mobile layout with collapsible bottom navigation
- Inline edit form on tube and box detail pages (no separate edit page)
- **Version history** for tubes and boxes with diff highlighting and one-click revert
- Multi-select bulk assign: select multiple tubes and assign to a box at once
- Case-insensitive username login (`COLLATE NOCASE`)
- `make seed` with 15 boxes, 4 cores, and ~53 tubes of sample data
- `make reset-db` with interactive confirmation

### Fixed
- iOS Safari auto-zoom suppressed on barcode inputs
- Dashboard rows clickable throughout; datetime columns labelled UTC
- Barcode autofill from scan result; instant tube assign in box panel

---

## [0.0.1] — 2025-11

### Added
- Flask backend with DDD-inspired layering (routes → repositories → domain dataclasses)
- SQLite database with numbered migration files; `schema_migrations` tracking table
- Flask-Login authentication with `werkzeug` password hashing and `before_request` auth guard
- React 18 + Vite frontend with React Router
- Tube and box CRUD with barcode scanning (USB wedge + camera)
- Scan page: scan barcode to look up or create a tube; inline prompt to create unknown barcodes
- Box detail: assign existing tubes by barcode, edit/remove per-tube buttons
- Tube form: scan box barcode to assign; location search map picker (Leaflet + OSM)
- Leaflet maps on tube and box detail views; dashboard map showing all tube locations
- CSV/TSV export with timestamped filenames
- Box list with filter/search
- Dashboard stat cards linking to filtered box and tube lists
- Docker Compose dev environment with hot-reload for both services
- GitHub Actions CI: lint, typecheck, and test for backend and frontend
- PythonAnywhere deployment via `make deploy-pa`
