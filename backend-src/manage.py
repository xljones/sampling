#!/usr/bin/env python3
"""Management CLI. Usage: python manage.py <command> [args]"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def cmd_create_user(args):
    if len(args) != 2:
        print("Usage: python manage.py create-user <username> <password>")
        sys.exit(1)
    username, password = args
    from sampling.db import get_db
    from sampling.repositories.user_repository import UserRepository
    with get_db() as db:
        repo = UserRepository(db)
        if repo.get_by_username(username):
            print(f"Error: user '{username}' already exists")
            sys.exit(1)
        repo.create(username, password)
    print(f"User '{username}' created.")


def cmd_list_users(_):
    from sampling.db import get_db
    with get_db() as db:
        users = db.execute(
            "SELECT id, username, is_readonly, expires_at, created_at FROM users ORDER BY id"
        ).fetchall()
    if not users:
        print("No users.")
    for u in users:
        kind = "read-only" if u[2] else "normal"
        expiry = f"  expires {u[3]}" if u[3] else ""
        print(f"  [{u[0]}] {u[1]}  ({kind}{expiry})  created {u[4]}")


def cmd_seed(_):
    from sampling.db import get_db, run_migrations
    from sampling.repositories.box_repository import BoxRepository
    from sampling.repositories.core_repository import CoreRepository
    from sampling.repositories.tube_repository import TubeRepository

    run_migrations()

    DEFAULT_LOCATIONS = [
        "Tromsø – Lab",
        "Southampton - Lab A",
        "Southampton - Lab B",
        "In transit",
    ]

    BOXES = [
        # (barcode, name, location_name, notes)
        ("BX-001", "North Sea Set A",    "Southampton - Lab A", None),
        ("BX-002", "North Sea Set B",    "Southampton - Lab A", None),
        ("BX-003", "North Sea Set C",    "Southampton - Lab A", None),
        ("BX-004", "Thames Est. Set 1",  "Southampton - Lab B", None),
        ("BX-005", "Thames Est. Set 2",  "Southampton - Lab B", None),
        ("BX-006", "Norfolk Broads TH-1","Southampton - Lab A", None),
        ("BX-007", "Norfolk Broads TH-2","Southampton - Lab A", None),
        ("BX-008", "Norfolk Broads TH-3","Southampton - Lab A", None),
        ("BX-009", "Severn Est. SE-01",  "In transit",          None),
        ("BX-010", "Severn Est. SE-02",  "In transit",          None),
        ("BX-011", "Loch Etive LE-1",    "Tromsø – Lab",       None),
        ("BX-012", "Loch Etive LE-2",    "Tromsø – Lab",       None),
        ("BX-013", "Loch Lomond LL-1",   "Tromsø – Lab",       None),
        ("BX-014", "Humber Est. HE-1",   "Southampton - Lab B", None),
        ("BX-015", "Solent Core SL-1",   "Southampton - Lab A", None),
    ]

    CORES = [
        # (barcode, name, loc_name, site_name, lat, lon, date,
        #  sample_type, depth_cm, collector, owner, notes)
        (
            "CR-001", "North Sea Core A", "Southampton - Lab A",
            "North Sea Block 49/5", 56.82, 2.41, "2023-07-14",
            "Piston core", 105, "J. Harrison", "NOC Southampton",
            "Long piston core, 2023 cruise",
        ),
        (
            "CR-002", "North Sea Core B", "Southampton - Lab A",
            "North Sea Block 49/5", 56.83, 2.43, "2023-07-15",
            "Gravity core", 70, "J. Harrison", "NOC Southampton",
            "Gravity core, 2023 cruise",
        ),
        (
            "CR-003", "North Sea Core C", "Southampton - Lab A",
            "North Sea Block 49/5", 56.80, 2.38, "2023-07-16",
            "Box core", 110, "J. Harrison", "NOC Southampton", None,
        ),
        (
            "CR-004", "Thames Est. Core 1", "Southampton - Lab B",
            "Thames Estuary, Canvey Island", 51.52, 0.60, "2022-09-03",
            "Gouge core", 75, "A. Phillips", "BGS",
            "Intertidal flat, spring tide",
        ),
        (
            "CR-005", "Thames Est. Core 2", "Southampton - Lab B",
            "Thames Estuary, Canvey Island", 51.50, 0.58, "2022-09-04",
            "Gouge core", 65, "A. Phillips", "BGS",
            "Subtidal channel margin",
        ),
        (
            "CR-006", "Norfolk Broads TH-1", "Southampton - Lab A",
            "Hickling Broad, Norfolk", 52.76, 1.56, "2021-04-20",
            "Russian corer", 80, "S. Weston", "UEA",
            "Hickling Broad, 4m water depth",
        ),
        (
            "CR-007", "Norfolk Broads TH-2", "Southampton - Lab A",
            "Barton Broad, Norfolk", 52.74, 1.53, "2021-04-22",
            "Russian corer", 65, "S. Weston", "UEA", "Barton Broad",
        ),
        (
            "CR-008", "Norfolk Broads TH-3", "Southampton - Lab A",
            "Barton Broad, Norfolk", 52.75, 1.54, "2021-04-23",
            "Russian corer", 60, "S. Weston", "UEA", None,
        ),
        (
            "CR-009", "Severn Est. SE-01", "In transit",
            "Goldcliff, Severn Estuary", 51.56, -2.90, "2023-03-10",
            "Percussion core", 70, "D. Massey", "Cardiff University",
            "Goldcliff mudflat transect",
        ),
        (
            "CR-010", "Severn Est. SE-02", "In transit",
            "Goldcliff, Severn Estuary", 51.55, -2.91, "2023-03-11",
            "Percussion core", 60, "D. Massey", "Cardiff University", None,
        ),
        (
            "CR-011", "Loch Etive LE-1", "Tromsø – Lab",
            "Loch Etive, Argyll", 56.47, -5.23, "2020-08-05",
            "Gravity core", 105, "T. Andersen", "SAMS",
            "Fjordic basin, 145m depth",
        ),
        (
            "CR-012", "Loch Etive LE-2", "Tromsø – Lab",
            "Loch Etive, Argyll", 56.45, -5.20, "2020-08-06",
            "Gravity core", 75, "T. Andersen", "SAMS", "Mid-basin",
        ),
        (
            "CR-013", "Loch Lomond LL-1", "Tromsø – Lab",
            "Loch Lomond, Stirling", 56.08, -4.65, "2019-06-18",
            "Freeze core", 120, "T. Andersen", "SAMS", "Deep basin core",
        ),
        (
            "CR-014", "Humber Est. HE-1", "Southampton - Lab B",
            "Spurn Point, Humber Estuary", 53.58, 0.12, "2022-05-12",
            "Gouge core", 75, "R. Lamb", "University of Hull",
            "Spurn Point vicinity",
        ),
        (
            "CR-015", "Solent Core SL-1", "Southampton - Lab A",
            "Western Solent, Hampshire", 50.76, -1.52, "2023-11-08",
            "Box core", 70, "K. Murray", "NOC Southampton",
            "Western Solent, 12m depth",
        ),
    ]

    # (barcode, box_bc, core_bc, sample_date, sample_type, description, vol_ml, wt_g, depth_cm)
    # site/lat/lon inherited from core. sample_date is the lab sub-sampling date.
    # A few tubes carry explicit coords to demonstrate the override feature.
    TUBES = [
        # CR-001 collected 2023-07-14 — sub-sampled late July
        ("T-0001", "BX-001", "CR-001", "2023-07-21", "Sediment", "Olive-grey silty clay",             45.0,  98.2,   5.0),
        ("T-0002", "BX-001", "CR-001", "2023-07-21", "Sediment", "Olive-grey silty clay",             45.0,  97.1,  25.0),
        ("T-0003", "BX-001", "CR-001", "2023-07-22", "Sediment", "Sandy layer, possible turbidite",   40.0, 102.5,  50.0),
        ("T-0004", "BX-001", "CR-001", "2023-07-22", "Sediment", "Dark organic-rich layer",           38.0,  89.3,  80.0),
        # CR-002 collected 2023-07-15 — sub-sampled early August
        ("T-0005", "BX-002", "CR-002", "2023-08-01", "Sediment", "Foram-rich foraminiferal ooze",     50.0, 110.0,  10.0),
        ("T-0006", "BX-002", "CR-002", "2023-08-01", "Sediment", "Foram-rich foraminiferal ooze",     50.0, 108.4,  30.0),
        ("T-0007", "BX-002", "CR-002", "2023-08-02", "Sand",     "Coarse sand, IRD present",          42.0,  95.0,  60.0),
        # CR-003 collected 2023-07-16 — sub-sampled early August
        ("T-0008", "BX-003", "CR-003", "2023-08-07", "Sediment", "Homogeneous grey clay",             44.0,  96.1,  15.0),
        ("T-0009", "BX-003", "CR-003", "2023-08-07", "Sediment", "Laminated clay-silt",               44.0,  94.7,  45.0),
        ("T-0010", "BX-003", "CR-003", "2023-08-08", "Sediment", "Bioturbated silty clay",            43.0,  93.8,  90.0),
        # CR-004 collected 2022-09-03 — sub-sampled mid-September
        ("T-0011", "BX-004", "CR-004", "2022-09-16", "Organic",  "Peat layer, dark brown fibrous",    30.0,  52.4,   8.0),
        ("T-0012", "BX-004", "CR-004", "2022-09-16", "Sediment", "Blue-grey estuarine clay",          48.0, 103.2,  22.0),
        ("T-0013", "BX-004", "CR-004", "2022-09-17", "Sediment", "Blue-grey estuarine clay",          47.0, 101.5,  40.0),
        ("T-0014", "BX-004", "CR-004", "2022-09-17", "Sand",     "Tidal flat sand, shell fragments",  35.0,  88.9,  60.0),
        # CR-005 collected 2022-09-04 — sub-sampled late September
        ("T-0015", "BX-005", "CR-005", "2022-09-23", "Sediment", "Silty clay with organic flecks",    46.0,  99.0,  12.0),
        ("T-0016", "BX-005", "CR-005", "2022-09-23", "Sediment", "Silty clay with organic flecks",    45.0,  97.3,  35.0),
        ("T-0017", "BX-005", "CR-005", "2022-09-24", "Organic",  "Buried saltmarsh peat",             28.0,  48.1,  55.0),
        # CR-006 collected 2021-04-20 — sub-sampled early May
        ("T-0018", "BX-006", "CR-006", "2021-05-05", "Sediment", "Lake marl, white calcareous",       40.0,  72.3,   5.0),
        ("T-0019", "BX-006", "CR-006", "2021-05-05", "Organic",  "Gyttja, dark organic lake mud",     38.0,  68.5,  20.0),
        ("T-0020", "BX-006", "CR-006", "2021-05-06", "Organic",  "Gyttja, dark organic lake mud",     37.0,  67.1,  40.0),
        ("T-0021", "BX-006", "CR-006", "2021-05-06", "Peat",     "Reed peat, brown fibrous",          32.0,  55.8,  65.0),
        # CR-007 collected 2021-04-22 — sub-sampled mid-May
        ("T-0022", "BX-007", "CR-007", "2021-05-13", "Sediment", "Grey silty clay with diatoms",      41.0,  80.2,  10.0),
        ("T-0023", "BX-007", "CR-007", "2021-05-13", "Organic",  "Dark gyttja",                       39.0,  71.4,  30.0),
        ("T-0024", "BX-007", "CR-007", "2021-05-14", "Peat",     "Fen peat",                          31.0,  53.2,  55.0),
        # CR-008 collected 2021-04-23 — sub-sampled mid-May
        ("T-0025", "BX-008", "CR-008", "2021-05-19", "Sediment", "Calcareous mud",                    40.0,  78.9,   8.0),
        ("T-0026", "BX-008", "CR-008", "2021-05-19", "Organic",  "Organic-rich clay",                 39.0,  73.6,  25.0),
        ("T-0027", "BX-008", "CR-008", "2021-05-20", "Peat",     "Basal peat, woody fragments",       30.0,  51.0,  50.0),
        # CR-009 collected 2023-03-10 — sub-sampled late March
        ("T-0028", "BX-009", "CR-009", "2023-03-24", "Sediment", "Laminated estuarine clay",          49.0, 106.3,   6.0),
        ("T-0029", "BX-009", "CR-009", "2023-03-24", "Organic",  "Submerged forest peat",             27.0,  46.2,  18.0),
        ("T-0030", "BX-009", "CR-009", "2023-03-25", "Sediment", "Red-brown alluvial clay",           48.0, 104.1,  35.0),
        ("T-0031", "BX-009", "CR-009", "2023-03-25", "Sediment", "Red-brown alluvial clay",           47.0, 102.8,  55.0),
        # CR-010 collected 2023-03-11 — sub-sampled early April
        ("T-0032", "BX-010", "CR-010", "2023-04-01", "Sediment", "Grey estuarine clay",               48.0, 105.0,  10.0),
        ("T-0033", "BX-010", "CR-010", "2023-04-01", "Sand",     "Intertidal sand layer",             36.0,  84.5,  28.0),
        ("T-0034", "BX-010", "CR-010", "2023-04-02", "Sediment", "Grey estuarine clay",               47.0, 103.3,  48.0),
        # CR-011 collected 2020-08-05 — sub-sampled late August
        ("T-0035", "BX-011", "CR-011", "2020-08-21", "Sediment", "Dark laminated fjord sediment",     46.0, 100.7,   3.0),
        ("T-0036", "BX-011", "CR-011", "2020-08-21", "Sediment", "Varved clay, annual laminae",       45.0,  98.9,  20.0),
        ("T-0037", "BX-011", "CR-011", "2020-08-22", "Sediment", "Varved clay, annual laminae",       44.0,  97.4,  50.0),
        ("T-0038", "BX-011", "CR-011", "2020-08-22", "Sand",     "Event layer, coarse sand",          38.0,  92.0,  85.0),
        # CR-012 collected 2020-08-06 — sub-sampled early September
        ("T-0039", "BX-012", "CR-012", "2020-09-04", "Sediment", "Olive-grey silty clay",             45.0,  99.2,   7.0),
        ("T-0040", "BX-012", "CR-012", "2020-09-04", "Sediment", "Olive-grey silty clay",             44.0,  97.8,  30.0),
        ("T-0041", "BX-012", "CR-012", "2020-09-05", "Organic",  "Organic-rich layer",                36.0,  68.3,  60.0),
        # CR-013 collected 2019-06-18 — sub-sampled early July
        ("T-0042", "BX-013", "CR-013", "2019-07-04", "Sediment", "Grey glaciolacustrine clay",        47.0, 101.5,  10.0),
        ("T-0043", "BX-013", "CR-013", "2019-07-04", "Sediment", "Grey glaciolacustrine clay",        46.0, 100.2,  35.0),
        ("T-0044", "BX-013", "CR-013", "2019-07-05", "Sediment", "Diamict, possible till",            50.0, 118.4,  70.0),
        ("T-0045", "BX-013", "CR-013", "2019-07-05", "Sediment", "Diamict, possible till",            50.0, 117.1, 100.0),
        # CR-014 collected 2022-05-12 — sub-sampled late May
        ("T-0046", "BX-014", "CR-014", "2022-05-27", "Sediment", "Estuarine silty clay",              47.0, 102.0,   5.0),
        ("T-0047", "BX-014", "CR-014", "2022-05-27", "Sand",     "Fluvial sand, cross-bedded",        34.0,  82.3,  22.0),
        ("T-0048", "BX-014", "CR-014", "2022-05-28", "Sediment", "Grey estuarine clay",               46.0, 100.8,  42.0),
        ("T-0049", "BX-014", "CR-014", "2022-05-28", "Organic",  "Rootlet bed, reworked peat",        26.0,  43.5,  62.0),
        # CR-015 collected 2023-11-08 — sub-sampled late November
        ("T-0050", "BX-015", "CR-015", "2023-11-23", "Sediment", "Pale grey calcareous mud",          44.0,  96.5,   4.0),
        ("T-0051", "BX-015", "CR-015", "2023-11-23", "Sediment", "Pale grey calcareous mud",          44.0,  95.8,  18.0),
        ("T-0052", "BX-015", "CR-015", "2023-11-24", "Sand",     "Shelly coarse sand",                37.0,  87.2,  38.0),
        ("T-0053", "BX-015", "CR-015", "2023-11-24", "Sediment", "Grey silty clay",                   45.0,  98.1,  58.0),
    ]

    # Tubes that carry their own coordinates (overriding core inheritance)
    TUBE_COORD_OVERRIDES = {
        "T-0007": (56.835, 2.447),   # IRD sand — slightly offset sample position
        "T-0029": (51.558, -2.903),  # Submerged forest — precise peat outcrop location
        "T-0044": (56.079, -4.648),  # Till diamict — deeper basin sample point
    }

    with get_db() as db:
        box_repo = BoxRepository(db)
        core_repo = CoreRepository(db)
        tube_repo = TubeRepository(db)
        box_ids = {}
        core_ids = {}

        for loc_name in DEFAULT_LOCATIONS:
            exists = db.execute(
                "SELECT 1 FROM locations WHERE name=?", (loc_name,)
            ).fetchone()
            if not exists:
                db.execute("INSERT INTO locations (name) VALUES (?)", (loc_name,))
                print(f"  location: {loc_name}")

        locs = {
            r["name"]: r["id"]
            for r in db.execute("SELECT id, name FROM locations").fetchall()
        }

        for barcode, name, loc_name, notes in BOXES:
            if box_repo.get_by_barcode(barcode):
                print(f"  skip box {barcode} (already exists)")
                continue
            box = box_repo.create(barcode, name, locs.get(loc_name), notes)
            box_ids[barcode] = box["id"]
            print(f"  box {barcode} — {name}")

        for (bc, name, loc_name, site, lat, lon, date,
             stype, depth, collector, owner, notes) in CORES:
            if core_repo.get_by_barcode(bc):
                print(f"  skip core {bc} (already exists)")
                continue
            core = core_repo.create(
                bc, name=name, location_id=locs.get(loc_name),
                site_name=site, latitude=lat, longitude=lon,
                collection_date=date, sample_type=stype,
                depth_cm=depth, collector=collector, owner=owner, notes=notes,
            )
            core_ids[bc] = core["id"]
            print(f"  core {bc} — {name}")

        for (barcode, box_bc, core_bc, sample_date, stype, desc, vol, wt, depth) in TUBES:
            if tube_repo.get_by_barcode(barcode):
                print(f"  skip tube {barcode} (already exists)")
                continue
            box_id = box_ids.get(box_bc) or (
                (box_repo.get_by_barcode(box_bc) or {}).get("id")
            )
            core_id = core_ids.get(core_bc) or (
                (core_repo.get_by_barcode(core_bc) or {}).get("id")
            )
            lat, lon = TUBE_COORD_OVERRIDES.get(barcode, (None, None))
            tube_repo.create(
                barcode, box_id=box_id, core_id=core_id,
                sample_date=sample_date, sample_type=stype, description=desc,
                latitude=lat, longitude=lon,
                volume_ml=vol, weight_g=wt, depth_cm=depth,
            )
            print(f"  tube {barcode} — core {core_bc} @ {depth}cm")

    print(f"\nDone. {len(BOXES)} boxes, {len(CORES)} cores, {len(TUBES)} tubes.")


def cmd_rename_user(args):
    if len(args) != 2:
        print("Usage: python manage.py rename-user <username> <new-username>")
        sys.exit(1)
    username, new_username = args
    from sampling.db import get_db
    from sampling.repositories.user_repository import UserRepository
    with get_db() as db:
        repo = UserRepository(db)
        user = repo.get_by_username(username)
        if not user:
            print(f"Error: user '{username}' not found")
            sys.exit(1)
        if repo.get_by_username(new_username):
            print(f"Error: user '{new_username}' already exists")
            sys.exit(1)
        repo.rename(user["id"], new_username)
    print(f"User '{username}' renamed to '{new_username}'.")


def cmd_delete_user(args):
    if len(args) != 1:
        print("Usage: python manage.py delete-user <username>")
        sys.exit(1)
    username = args[0]
    from sampling.db import get_db
    from sampling.repositories.user_repository import UserRepository
    with get_db() as db:
        repo = UserRepository(db)
        if not repo.get_by_username(username):
            print(f"Error: user '{username}' not found")
            sys.exit(1)
    confirm = input(f"Delete user '{username}'? Type YES to confirm: ")
    if confirm.strip() != "YES":
        print("Aborted.")
        sys.exit(0)
    with get_db() as db:
        repo = UserRepository(db)
        user = repo.get_by_username(username)
        repo.delete(user["id"])
    print(f"User '{username}' deleted.")


def cmd_reset_db(args):
    drop_all = "all" in args
    if drop_all:
        msg = "This will drop ALL tables including users. Type YES to confirm: "
    else:
        msg = "This will drop all tables except users. Type YES to confirm: "
    confirm = input(msg)
    if confirm.strip() != "YES":
        print("Aborted.")
        sys.exit(0)
    from sampling.db import get_db
    with get_db() as db:
        tables = [
            "tube_history", "box_history", "core_history",
            "tubes", "boxes", "cores", "locations",
            "schema_migrations",
        ]
        if drop_all:
            tables.append("users")
        for table in tables:
            db.execute(f"DROP TABLE IF EXISTS {table}")
    suffix = "" if drop_all else " Users preserved."
    print(f"Tables dropped.{suffix} Run seed to repopulate.")


COMMANDS = {
    "create-user": cmd_create_user,
    "list-users":  cmd_list_users,
    "rename-user": cmd_rename_user,
    "delete-user": cmd_delete_user,
    "seed":        cmd_seed,
    "reset-db":    cmd_reset_db,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(f"Available commands: {', '.join(COMMANDS)}")
        sys.exit(1)
    COMMANDS[sys.argv[1]](sys.argv[2:])
