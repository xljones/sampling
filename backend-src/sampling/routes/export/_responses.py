import csv
import io
import json
from datetime import datetime, timezone
from typing import Any

from flask import Response, request


def _safe(value: str) -> str:
    """Sanitise a value for use in a filename."""
    return "".join(c if c.isalnum() or c in "-_." else "_" for c in str(value))


def respond(
    data: list[dict[str, Any]],
    fields: list[str],
    basename: str,
) -> Response:
    fmt = request.args.get("format", "csv")
    if fmt == "tsv":
        return _tsv_response(data, fields, basename)
    if fmt == "geojson":
        return _geojson_response(data, fields, basename)
    return _csv_response(data, fields, basename)


def _csv_response(
    data: list[dict[str, Any]],
    fields: list[str],
    basename: str,
) -> Response:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fields, extrasaction="ignore", lineterminator="\r\n")
    writer.writeheader()
    writer.writerows(data)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
    return Response(
        buf.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{basename}-{ts}.csv"'},
    )


def _tsv_response(
    data: list[dict[str, Any]],
    fields: list[str],
    basename: str,
) -> Response:
    buf = io.StringIO()
    writer = csv.DictWriter(
        buf,
        fieldnames=fields,
        extrasaction="ignore",
        delimiter="\t",
        lineterminator="\r\n",
    )
    writer.writeheader()
    writer.writerows(data)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
    return Response(
        buf.getvalue(),
        mimetype="text/tab-separated-values",
        headers={"Content-Disposition": f'attachment; filename="{basename}-{ts}.tsv"'},
    )


def json_response(
    data: list[dict[str, Any]],
    basename: str,
) -> Response:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
    return Response(
        json.dumps(data, indent=2, default=str),
        mimetype="application/json",
        headers={"Content-Disposition": f'attachment; filename="{basename}-{ts}.json"'},
    )


def _geojson_response(
    data: list[dict[str, Any]],
    fields: list[str],
    basename: str,
) -> Response:
    field_set = set(fields)
    coord_fields = {"latitude", "longitude"}
    prop_fields = [f for f in fields if f not in coord_fields]
    features = []
    for row in data:
        lat = row.get("latitude")
        lon = row.get("longitude")
        if lat is None or lon is None:
            continue
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {f: row.get(f) for f in prop_fields if f in field_set},
            }
        )
    collection = {"type": "FeatureCollection", "features": features}
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
    return Response(
        json.dumps(collection, indent=2, default=str),
        mimetype="application/geo+json",
        headers={"Content-Disposition": f'attachment; filename="{basename}-{ts}.geojson"'},
    )
