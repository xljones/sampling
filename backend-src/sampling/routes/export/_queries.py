from collections import defaultdict
from typing import Any

from sampling.repositories.box_repository import BoxRepository
from sampling.repositories.core_repository import CoreRepository

from ._fields import BOX_WITH_TUBES_FIELDS, CORE_WITH_TUBES_FIELDS


def parse_ids(raw: str) -> list[int] | None:
    if not raw:
        return None
    try:
        return [int(x) for x in raw.split(",") if x.strip()]
    except ValueError:
        return None


def build_box_with_tubes_rows(
    db: Any, box_id: int | None = None, ids: list[int] | None = None
) -> list[dict[str, Any]]:
    repo = BoxRepository(db)
    boxes = repo.export_flat(box_id=box_id, ids=ids)
    if not boxes:
        return []
    tubes = repo.export_tubes_for_boxes([b["id"] for b in boxes])

    tubes_by_box: dict[int, list] = defaultdict(list)
    for t in tubes:
        tubes_by_box[t["box_id"]].append(t)

    _null: dict[str, Any] = {f: None for f in BOX_WITH_TUBES_FIELDS}
    result = []
    for box in boxes:
        row = dict(_null)
        row.update(
            row_type="box",
            box_barcode=box["barcode"],
            box_name=box["name"],
            box_location=box["location"],
            box_notes=box["notes"],
            box_tube_count=box["tube_count"],
            box_created_at=box["created_at"],
        )
        result.append(row)
        for t in tubes_by_box[box["id"]]:
            row = dict(_null)
            row.update(
                row_type="tube",
                box_barcode=box["barcode"],
                tube_barcode=t["barcode"],
                tube_sample_date=t["sample_date"],
                tube_site_name=t["site_name"],
                tube_latitude=t["latitude"],
                tube_longitude=t["longitude"],
                tube_sample_type=t["sample_type"],
                tube_description=t["description"],
                tube_volume_ml=t["volume_ml"],
                tube_weight_g=t["weight_g"],
                tube_depth_cm=t["depth_cm"],
                tube_created_at=t["created_at"],
                tube_updated_at=t["updated_at"],
            )
            result.append(row)
    return result


def build_box_json(
    db: Any, box_id: int | None = None, ids: list[int] | None = None
) -> list[dict[str, Any]]:
    repo = BoxRepository(db)
    boxes = repo.export_flat(box_id=box_id, ids=ids)
    if not boxes:
        return []
    tubes = repo.export_tubes_for_boxes([b["id"] for b in boxes])

    tubes_by_box: dict[int, list] = defaultdict(list)
    for t in tubes:
        tubes_by_box[t["box_id"]].append({k: v for k, v in t.items() if k != "box_id"})

    return [
        {
            "barcode": b["barcode"],
            "name": b["name"],
            "location": b["location"],
            "notes": b["notes"],
            "tube_count": b["tube_count"],
            "created_at": b["created_at"],
            "tubes": tubes_by_box[b["id"]],
        }
        for b in boxes
    ]


def build_core_with_tubes_rows(
    db: Any, core_id: int | None = None, ids: list[int] | None = None
) -> list[dict[str, Any]]:
    repo = CoreRepository(db)
    cores = repo.export_flat(core_id=core_id, ids=ids)
    if not cores:
        return []
    tubes = repo.export_tubes_for_cores([c["id"] for c in cores])

    tubes_by_core: dict[int, list] = defaultdict(list)
    for t in tubes:
        tubes_by_core[t["core_id"]].append(t)

    _null: dict[str, Any] = {f: None for f in CORE_WITH_TUBES_FIELDS}
    result = []
    for core in cores:
        row = dict(_null)
        row.update(
            row_type="core",
            core_barcode=core["barcode"],
            core_name=core["name"],
            core_location=core["location"],
            core_site_name=core["site_name"],
            core_latitude=core["latitude"],
            core_longitude=core["longitude"],
            core_collection_date=core["collection_date"],
            core_depth_cm=core["depth_cm"],
            core_collector=core["collector"],
            core_sample_type=core["sample_type"],
            core_owner=core["owner"],
            core_notes=core["notes"],
            core_tube_count=core["tube_count"],
            core_box_count=core["box_count"],
            core_created_at=core["created_at"],
            core_updated_at=core["updated_at"],
        )
        result.append(row)

        by_box: dict = {}
        for t in tubes_by_core[core["id"]]:
            key = t["box_id"]
            if key not in by_box:
                by_box[key] = []
            by_box[key].append(t)

        for box_id_key, box_tubes in by_box.items():
            first = box_tubes[0]
            if box_id_key is not None:
                row = dict(_null)
                row.update(
                    row_type="box",
                    core_barcode=core["barcode"],
                    box_barcode=first["box_barcode"],
                    box_name=first["box_name"],
                )
                result.append(row)
            for t in box_tubes:
                row = dict(_null)
                row.update(
                    row_type="tube",
                    core_barcode=core["barcode"],
                    box_barcode=t["box_barcode"],
                    tube_barcode=t["barcode"],
                    tube_sample_date=t["sample_date"],
                    tube_site_name=t["site_name"],
                    tube_latitude=t["latitude"],
                    tube_longitude=t["longitude"],
                    tube_sample_type=t["sample_type"],
                    tube_description=t["description"],
                    tube_volume_ml=t["volume_ml"],
                    tube_weight_g=t["weight_g"],
                    tube_depth_cm=t["depth_cm"],
                    tube_created_at=t["created_at"],
                    tube_updated_at=t["updated_at"],
                )
                result.append(row)
    return result


def build_core_json(
    db: Any, core_id: int | None = None, ids: list[int] | None = None
) -> list[dict[str, Any]]:
    repo = CoreRepository(db)
    cores = repo.export_flat(core_id=core_id, ids=ids)
    if not cores:
        return []
    tubes = repo.export_tubes_for_cores([c["id"] for c in cores])

    tubes_by_core: dict[int, list] = defaultdict(list)
    for t in tubes:
        tubes_by_core[t["core_id"]].append(t)

    result = []
    for core in cores:
        by_box: dict[int | None, dict] = {}
        for t in tubes_by_core[core["id"]]:
            key = t["box_id"]
            if key not in by_box:
                by_box[key] = {"barcode": t["box_barcode"], "name": t["box_name"], "tubes": []}
            by_box[key]["tubes"].append(
                {
                    "barcode": t["barcode"],
                    "sample_date": t["sample_date"],
                    "site_name": t["site_name"],
                    "latitude": t["latitude"],
                    "longitude": t["longitude"],
                    "sample_type": t["sample_type"],
                    "description": t["description"],
                    "volume_ml": t["volume_ml"],
                    "weight_g": t["weight_g"],
                    "depth_cm": t["depth_cm"],
                    "created_at": t["created_at"],
                    "updated_at": t["updated_at"],
                }
            )
        result.append(
            {
                "barcode": core["barcode"],
                "name": core["name"],
                "location": core["location"],
                "site_name": core["site_name"],
                "latitude": core["latitude"],
                "longitude": core["longitude"],
                "collection_date": core["collection_date"],
                "depth_cm": core["depth_cm"],
                "collector": core["collector"],
                "sample_type": core["sample_type"],
                "owner": core["owner"],
                "notes": core["notes"],
                "tube_count": core["tube_count"],
                "box_count": core["box_count"],
                "created_at": core["created_at"],
                "updated_at": core["updated_at"],
                "boxes": [v for k, v in by_box.items() if k is not None],
                "unboxed_tubes": by_box[None]["tubes"] if None in by_box else [],
            }
        )
    return result
