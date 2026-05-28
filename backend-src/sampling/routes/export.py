import csv
import io
from flask import Blueprint, Response
from flask_login import login_required
from sampling.db import get_db
from sampling.repositories.box_repository import BoxRepository
from sampling.repositories.tube_repository import TubeRepository

bp = Blueprint("export", __name__)

_TUBE_FIELDS = [
    "barcode", "box_barcode", "box_name", "collection_date", "site_name",
    "latitude", "longitude", "sample_type", "description",
    "volume_ml", "weight_g", "depth_cm", "created_at", "updated_at",
]
_BOX_FIELDS = ["barcode", "name", "location", "notes", "tube_count", "created_at"]


@bp.get("/api/export/tubes")
@login_required
def export_tubes():
    with get_db() as db:
        data = TubeRepository(db).export_all()
    return _csv_response(data, _TUBE_FIELDS, "tubes.csv")


@bp.get("/api/export/boxes")
@login_required
def export_boxes():
    with get_db() as db:
        data = BoxRepository(db).export_all()
    return _csv_response(data, _BOX_FIELDS, "boxes.csv")


def _csv_response(data, fields, filename):
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fields, extrasaction="ignore", lineterminator="\r\n")
    writer.writeheader()
    writer.writerows(data)
    return Response(
        buf.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
