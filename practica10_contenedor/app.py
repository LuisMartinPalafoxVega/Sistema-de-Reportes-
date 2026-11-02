"""Aplicación web contenedorizada para consultar reportes de colonias."""

from __future__ import annotations

import os
from datetime import datetime, timezone

import boto3
from flask import Flask, jsonify, request


app = Flask(__name__)
TABLE_NAME = os.getenv("TABLE_NAME", "ReportesColoniasP07")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"


def read_reports(limit: int) -> list[dict]:
    if DEMO_MODE:
        return [
            {
                "id_reporte": "DEMO-P10-001",
                "categoria": "Alumbrado público",
                "estado": "Pendiente",
                "fecha_creacion": datetime.now(timezone.utc).isoformat(),
                "titulo": "Lámpara sin funcionar",
            }
        ][:limit]

    table = boto3.resource("dynamodb", region_name=AWS_REGION).Table(TABLE_NAME)
    result = table.scan(Limit=limit)
    items = result.get("Items", [])
    items.sort(key=lambda item: str(item.get("fecha_creacion", "")), reverse=True)
    return items


@app.get("/health")
def health():
    return jsonify({"ok": True, "service": "sistema-reportes", "container": True})


@app.get("/reportes")
def reportes():
    try:
        limit = min(max(int(request.args.get("limit", "20")), 1), 20)
    except ValueError:
        return jsonify({"ok": False, "error": "limit debe ser un entero entre 1 y 20"}), 400

    try:
        items = read_reports(limit)
    except Exception as exc:  # pragma: no cover - diagnostic response for deployment
        app.logger.exception("No se pudieron consultar los reportes")
        return jsonify({"ok": False, "error": str(exc), "table": TABLE_NAME}), 503

    return jsonify({
        "ok": True,
        "table": TABLE_NAME,
        "count": len(items),
        "items": items,
        "mode": "demo" if DEMO_MODE else "dynamodb",
    })


if __name__ == "__main__":
    app.run(host=os.getenv("HOST", "0.0.0.0"), port=int(os.getenv("PORT", "8080")))
