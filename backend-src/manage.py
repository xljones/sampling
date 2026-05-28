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
        users = db.execute("SELECT id, username, created_at FROM users ORDER BY id").fetchall()
    if not users:
        print("No users.")
    for u in users:
        print(f"  [{u[0]}] {u[1]}  (created {u[2]})")


def cmd_seed(_):
    from sampling.db import get_db, run_migrations
    from sampling.repositories.box_repository import BoxRepository
    from sampling.repositories.tube_repository import TubeRepository

    run_migrations()

    BOXES = [
        # (barcode, name, location_name, notes)
        ("BX-001", "North Sea Core A",    "Southampton - Lab A", "Long piston core, 2023 cruise"),
        ("BX-002", "North Sea Core B",    "Southampton - Lab A", "Gravity core, 2023 cruise"),
        ("BX-003", "North Sea Core C",    "Southampton - Lab A", None),
        ("BX-004", "Thames Est. Core 1",  "Southampton - Lab B", "Intertidal flat, spring tide"),
        ("BX-005", "Thames Est. Core 2",  "Southampton - Lab B", "Subtidal channel margin"),
        ("BX-006", "Norfolk Broads TH-1", "Southampton - Lab A", "Hickling Broad, 4m water depth"),
        ("BX-007", "Norfolk Broads TH-2", "Southampton - Lab A", "Barton Broad"),
        ("BX-008", "Norfolk Broads TH-3", "Southampton - Lab A", None),
        ("BX-009", "Severn Est. SE-01",   "In transit",          "Goldcliff mudflat transect"),
        ("BX-010", "Severn Est. SE-02",   "In transit",          None),
        ("BX-011", "Loch Etive LE-1",     "Tromsø – Lab",       "Fjordic basin, 145m depth"),
        ("BX-012", "Loch Etive LE-2",     "Tromsø – Lab",       "Mid-basin"),
        ("BX-013", "Loch Lomond LL-1",    "Tromsø – Lab",       "Deep basin core"),
        ("BX-014", "Humber Est. HE-1",    "Southampton - Lab B", "Spurn Point vicinity"),
        ("BX-015", "Solent Core SL-1",    "Southampton - Lab A", "Western Solent, 12m depth"),
    ]

    TUBES = [
        # barcode, box_barcode, date, site, lat, lon, type, description, vol_ml, wt_g, depth_cm
        ("T-0001", "BX-001", "2023-07-14", "North Sea Block 49/5",   56.82, 2.41,  "Sediment",      "Olive-grey silty clay",          45.0, 98.2,   5.0),
        ("T-0002", "BX-001", "2023-07-14", "North Sea Block 49/5",   56.82, 2.41,  "Sediment",      "Olive-grey silty clay",          45.0, 97.1,  25.0),
        ("T-0003", "BX-001", "2023-07-14", "North Sea Block 49/5",   56.82, 2.41,  "Sediment",      "Sandy layer, possible turbidite", 40.0, 102.5,  50.0),
        ("T-0004", "BX-001", "2023-07-14", "North Sea Block 49/5",   56.82, 2.41,  "Sediment",      "Dark organic-rich layer",         38.0,  89.3,  80.0),
        ("T-0005", "BX-002", "2023-07-15", "North Sea Block 49/5",   56.83, 2.43,  "Sediment",      "Foram-rich foraminiferal ooze",   50.0, 110.0,  10.0),
        ("T-0006", "BX-002", "2023-07-15", "North Sea Block 49/5",   56.83, 2.43,  "Sediment",      "Foram-rich foraminiferal ooze",   50.0, 108.4,  30.0),
        ("T-0007", "BX-002", "2023-07-15", "North Sea Block 49/5",   56.83, 2.43,  "Sand",          "Coarse sand, IRD present",        42.0,  95.0,  60.0),
        ("T-0008", "BX-003", "2023-07-16", "North Sea Block 49/5",   56.80, 2.38,  "Sediment",      "Homogeneous grey clay",           44.0,  96.1,  15.0),
        ("T-0009", "BX-003", "2023-07-16", "North Sea Block 49/5",   56.80, 2.38,  "Sediment",      "Laminated clay-silt",             44.0,  94.7,  45.0),
        ("T-0010", "BX-003", "2023-07-16", "North Sea Block 49/5",   56.80, 2.38,  "Sediment",      "Bioturbated silty clay",          43.0,  93.8,  90.0),
        ("T-0011", "BX-004", "2022-09-03", "Thames Estuary, Canvey", 51.52, 0.60,  "Organic",       "Peat layer, dark brown fibrous",  30.0,  52.4,   8.0),
        ("T-0012", "BX-004", "2022-09-03", "Thames Estuary, Canvey", 51.52, 0.60,  "Sediment",      "Blue-grey estuarine clay",        48.0, 103.2,  22.0),
        ("T-0013", "BX-004", "2022-09-03", "Thames Estuary, Canvey", 51.52, 0.60,  "Sediment",      "Blue-grey estuarine clay",        47.0, 101.5,  40.0),
        ("T-0014", "BX-004", "2022-09-03", "Thames Estuary, Canvey", 51.52, 0.60,  "Sand",          "Tidal flat sand, shell fragments", 35.0,  88.9,  60.0),
        ("T-0015", "BX-005", "2022-09-04", "Thames Estuary, Canvey", 51.50, 0.58,  "Sediment",      "Silty clay with organic flecks",  46.0,  99.0,  12.0),
        ("T-0016", "BX-005", "2022-09-04", "Thames Estuary, Canvey", 51.50, 0.58,  "Sediment",      "Silty clay with organic flecks",  45.0,  97.3,  35.0),
        ("T-0017", "BX-005", "2022-09-04", "Thames Estuary, Canvey", 51.50, 0.58,  "Organic",       "Buried saltmarsh peat",           28.0,  48.1,  55.0),
        ("T-0018", "BX-006", "2021-04-20", "Hickling Broad, Norfolk",52.76, 1.56,  "Sediment",      "Lake marl, white calcareous",     40.0,  72.3,   5.0),
        ("T-0019", "BX-006", "2021-04-20", "Hickling Broad, Norfolk",52.76, 1.56,  "Organic",       "Gyttja, dark organic lake mud",   38.0,  68.5,  20.0),
        ("T-0020", "BX-006", "2021-04-20", "Hickling Broad, Norfolk",52.76, 1.56,  "Organic",       "Gyttja, dark organic lake mud",   37.0,  67.1,  40.0),
        ("T-0021", "BX-006", "2021-04-20", "Hickling Broad, Norfolk",52.76, 1.56,  "Peat",          "Reed peat, brown fibrous",        32.0,  55.8,  65.0),
        ("T-0022", "BX-007", "2021-04-22", "Barton Broad, Norfolk",  52.74, 1.53,  "Sediment",      "Grey silty clay with diatoms",    41.0,  80.2,  10.0),
        ("T-0023", "BX-007", "2021-04-22", "Barton Broad, Norfolk",  52.74, 1.53,  "Organic",       "Dark gyttja",                     39.0,  71.4,  30.0),
        ("T-0024", "BX-007", "2021-04-22", "Barton Broad, Norfolk",  52.74, 1.53,  "Peat",          "Fen peat",                        31.0,  53.2,  55.0),
        ("T-0025", "BX-008", "2021-04-23", "Barton Broad, Norfolk",  52.75, 1.54,  "Sediment",      "Calcareous mud",                  40.0,  78.9,   8.0),
        ("T-0026", "BX-008", "2021-04-23", "Barton Broad, Norfolk",  52.75, 1.54,  "Organic",       "Organic-rich clay",               39.0,  73.6,  25.0),
        ("T-0027", "BX-008", "2021-04-23", "Barton Broad, Norfolk",  52.75, 1.54,  "Peat",          "Basal peat, woody fragments",     30.0,  51.0,  50.0),
        ("T-0028", "BX-009", "2023-03-10", "Goldcliff, Severn Est.", 51.56, -2.90, "Sediment",      "Laminated estuarine clay",        49.0, 106.3,   6.0),
        ("T-0029", "BX-009", "2023-03-10", "Goldcliff, Severn Est.", 51.56, -2.90, "Organic",       "Submerged forest peat",           27.0,  46.2,  18.0),
        ("T-0030", "BX-009", "2023-03-10", "Goldcliff, Severn Est.", 51.56, -2.90, "Sediment",      "Red-brown alluvial clay",         48.0, 104.1,  35.0),
        ("T-0031", "BX-009", "2023-03-10", "Goldcliff, Severn Est.", 51.56, -2.90, "Sediment",      "Red-brown alluvial clay",         47.0, 102.8,  55.0),
        ("T-0032", "BX-010", "2023-03-11", "Goldcliff, Severn Est.", 51.55, -2.91, "Sediment",      "Grey estuarine clay",             48.0, 105.0,  10.0),
        ("T-0033", "BX-010", "2023-03-11", "Goldcliff, Severn Est.", 51.55, -2.91, "Sand",          "Intertidal sand layer",           36.0,  84.5,  28.0),
        ("T-0034", "BX-010", "2023-03-11", "Goldcliff, Severn Est.", 51.55, -2.91, "Sediment",      "Grey estuarine clay",             47.0, 103.3,  48.0),
        ("T-0035", "BX-011", "2020-08-05", "Loch Etive, Argyll",     56.47, -5.23, "Sediment",      "Dark laminated fjord sediment",   46.0, 100.7,   3.0),
        ("T-0036", "BX-011", "2020-08-05", "Loch Etive, Argyll",     56.47, -5.23, "Sediment",      "Varved clay, annual laminae",     45.0,  98.9,  20.0),
        ("T-0037", "BX-011", "2020-08-05", "Loch Etive, Argyll",     56.47, -5.23, "Sediment",      "Varved clay, annual laminae",     44.0,  97.4,  50.0),
        ("T-0038", "BX-011", "2020-08-05", "Loch Etive, Argyll",     56.47, -5.23, "Sand",          "Event layer, coarse sand",        38.0,  92.0,  85.0),
        ("T-0039", "BX-012", "2020-08-06", "Loch Etive, Argyll",     56.45, -5.20, "Sediment",      "Olive-grey silty clay",           45.0,  99.2,   7.0),
        ("T-0040", "BX-012", "2020-08-06", "Loch Etive, Argyll",     56.45, -5.20, "Sediment",      "Olive-grey silty clay",           44.0,  97.8,  30.0),
        ("T-0041", "BX-012", "2020-08-06", "Loch Etive, Argyll",     56.45, -5.20, "Organic",       "Organic-rich layer",              36.0,  68.3,  60.0),
        ("T-0042", "BX-013", "2019-06-18", "Loch Lomond, Stirling",  56.08, -4.65, "Sediment",      "Grey glaciolacustrine clay",      47.0, 101.5,  10.0),
        ("T-0043", "BX-013", "2019-06-18", "Loch Lomond, Stirling",  56.08, -4.65, "Sediment",      "Grey glaciolacustrine clay",      46.0, 100.2,  35.0),
        ("T-0044", "BX-013", "2019-06-18", "Loch Lomond, Stirling",  56.08, -4.65, "Sediment",      "Diamict, possible till",          50.0, 118.4,  70.0),
        ("T-0045", "BX-013", "2019-06-18", "Loch Lomond, Stirling",  56.08, -4.65, "Sediment",      "Diamict, possible till",          50.0, 117.1, 100.0),
        ("T-0046", "BX-014", "2022-05-12", "Spurn Point, Humber",    53.58, 0.12,  "Sediment",      "Estuarine silty clay",            47.0, 102.0,   5.0),
        ("T-0047", "BX-014", "2022-05-12", "Spurn Point, Humber",    53.58, 0.12,  "Sand",          "Fluvial sand, cross-bedded",      34.0,  82.3,  22.0),
        ("T-0048", "BX-014", "2022-05-12", "Spurn Point, Humber",    53.58, 0.12,  "Sediment",      "Grey estuarine clay",             46.0, 100.8,  42.0),
        ("T-0049", "BX-014", "2022-05-12", "Spurn Point, Humber",    53.58, 0.12,  "Organic",       "Rootlet bed, reworked peat",      26.0,  43.5,  62.0),
        ("T-0050", "BX-015", "2023-11-08", "Western Solent, Hants",  50.76, -1.52, "Sediment",      "Pale grey calcareous mud",        44.0,  96.5,   4.0),
        ("T-0051", "BX-015", "2023-11-08", "Western Solent, Hants",  50.76, -1.52, "Sediment",      "Pale grey calcareous mud",        44.0,  95.8,  18.0),
        ("T-0052", "BX-015", "2023-11-08", "Western Solent, Hants",  50.76, -1.52, "Sand",          "Shelly coarse sand",              37.0,  87.2,  38.0),
        ("T-0053", "BX-015", "2023-11-08", "Western Solent, Hants",  50.76, -1.52, "Sediment",      "Grey silty clay",                 45.0,  98.1,  58.0),
    ]

    DEFAULT_LOCATIONS = [
        "Tromsø – Lab",
        "Southampton - Lab A",
        "Southampton - Lab B",
        "In transit",
    ]

    with get_db() as db:
        box_repo = BoxRepository(db)
        tube_repo = TubeRepository(db)
        box_ids = {}

        for loc_name in DEFAULT_LOCATIONS:
            exists = db.execute("SELECT 1 FROM locations WHERE name=?", (loc_name,)).fetchone()
            if not exists:
                db.execute("INSERT INTO locations (name) VALUES (?)", (loc_name,))
                print(f"  location: {loc_name}")

        locs = {r["name"]: r["id"] for r in db.execute("SELECT id, name FROM locations").fetchall()}

        for barcode, name, loc_name, notes in BOXES:
            if box_repo.get_by_barcode(barcode):
                print(f"  skip box {barcode} (already exists)")
                continue
            box = box_repo.create(barcode, name, locs.get(loc_name), notes)
            box_ids[barcode] = box["id"]
            print(f"  box {barcode} — {name}")

        for (barcode, box_bc, date, site, lat, lon,
             stype, desc, vol, wt, depth) in TUBES:
            if tube_repo.get_by_barcode(barcode):
                print(f"  skip tube {barcode} (already exists)")
                continue
            box_id = box_ids.get(box_bc)
            if box_id is None:
                existing = box_repo.get_by_barcode(box_bc)
                box_id = existing["id"] if existing else None
            tube_repo.create(
                barcode, box_id=box_id, collection_date=date,
                site_name=site, latitude=lat, longitude=lon,
                sample_type=stype, description=desc,
                volume_ml=vol, weight_g=wt, depth_cm=depth,
            )
            print(f"  tube {barcode} — {site} @ {depth}cm")

    print(f"\nDone. {len(BOXES)} boxes, {len(TUBES)} tubes.")


def cmd_reset_db(_):
    confirm = input("This will delete all boxes, tubes, and history (users kept). Type YES to confirm: ")
    if confirm.strip() != "YES":
        print("Aborted.")
        sys.exit(0)
    from sampling.db import get_db
    with get_db() as db:
        db.execute("DELETE FROM tube_history")
        db.execute("DELETE FROM box_history")
        db.execute("DELETE FROM tubes")
        db.execute("DELETE FROM boxes")
        db.execute("DELETE FROM sqlite_sequence WHERE name IN ('tubes','boxes','tube_history','box_history')")
    print("Database reset. Users preserved.")


COMMANDS = {
    "create-user": cmd_create_user,
    "list-users":  cmd_list_users,
    "seed":        cmd_seed,
    "reset-db":    cmd_reset_db,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(f"Available commands: {', '.join(COMMANDS)}")
        sys.exit(1)
    COMMANDS[sys.argv[1]](sys.argv[2:])
