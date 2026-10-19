"""CRUD demo for Practice 07 using the EC2 instance profile, never static keys."""

from __future__ import annotations

import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

import boto3
from boto3.dynamodb.conditions import Attr, Key


REGION = os.getenv("AWS_REGION", "us-east-1")
TABLE_NAME = os.getenv("P07_TABLE_NAME", "ReportesColoniasP07")
USER_INDEX = "usuario_id-fecha_creacion-index"
STATE_INDEX = "estado-fecha_creacion-index"

dynamodb = boto3.resource("dynamodb", region_name=REGION)
table = dynamodb.Table(TABLE_NAME)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def print_json(label: str, value: Any) -> None:
    print(f"\n=== {label} ===")
    print(json.dumps(value, ensure_ascii=False, indent=2, default=str))


def create_report(item: dict[str, Any]) -> dict[str, Any]:
    table.put_item(
        Item=item,
        ConditionExpression=Attr("id_reporte").not_exists(),
        ReturnConsumedCapacity="TOTAL",
    )
    return item


def get_report(report_id: str) -> dict[str, Any] | None:
    response = table.get_item(
        Key={"id_reporte": report_id},
        ConsistentRead=True,
        ReturnConsumedCapacity="TOTAL",
    )
    return response.get("Item")


def list_reports_by_user(user_id: str) -> dict[str, Any]:
    return table.query(
        IndexName=USER_INDEX,
        KeyConditionExpression=Key("usuario_id").eq(user_id),
        ScanIndexForward=False,
        ReturnConsumedCapacity="INDEXES",
    )


def list_reports_by_state(state: str) -> dict[str, Any]:
    return table.query(
        IndexName=STATE_INDEX,
        KeyConditionExpression=Key("estado").eq(state),
        ScanIndexForward=False,
        ReturnConsumedCapacity="INDEXES",
    )


def query_state_until_visible(state: str, report_id: str) -> dict[str, Any]:
    """GSI reads are eventually consistent, so retry briefly for the demo."""
    result: dict[str, Any] = {}
    for _ in range(10):
        result = list_reports_by_state(state)
        if any(item.get("id_reporte") == report_id for item in result.get("Items", [])):
            return result
        time.sleep(0.5)
    return result


def update_report_state(report_id: str, state: str) -> dict[str, Any]:
    response = table.update_item(
        Key={"id_reporte": report_id},
        UpdateExpression="SET #estado = :estado, fecha_actualizacion = :actualizado",
        ExpressionAttributeNames={"#estado": "estado"},
        ExpressionAttributeValues={":estado": state, ":actualizado": now_iso()},
        ConditionExpression=Attr("id_reporte").exists(),
        ReturnValues="ALL_NEW",
        ReturnConsumedCapacity="TOTAL",
    )
    return response["Attributes"]


def delete_report(report_id: str) -> dict[str, Any] | None:
    response = table.delete_item(
        Key={"id_reporte": report_id},
        ReturnValues="ALL_OLD",
        ReturnConsumedCapacity="TOTAL",
    )
    return response.get("Attributes")


def scan_by_state_inefficiently(state: str, limit: int = 100) -> dict[str, Any]:
    """Scan reads records before applying its filter; Limit bounds this demo."""
    return table.scan(
        FilterExpression=Attr("estado").eq(state),
        Limit=limit,
        ReturnConsumedCapacity="TOTAL",
    )


def run_demo() -> None:
    report_id = f"P07-DEMO-{uuid.uuid4().hex[:10]}"
    created = now_iso()
    item = {
        "id_reporte": report_id,
        "usuario_id": "USUARIO#1",
        "estado": "Pendiente",
        "fecha_creacion": created,
        "fecha_actualizacion": created,
        "categoria": "Alumbrado público",
        "titulo": "Prueba CRUD P07",
        "descripcion": "Registro ficticio temporal para validar DynamoDB.",
        "direccion": "Colonia Centro",
        "latitud": Decimal("25.7892000"),
        "longitud": Decimal("-108.9855000"),
    }

    print(f"Región: {REGION} | Tabla: {TABLE_NAME} | ID: {report_id}")
    print_json("CREATE - PutItem", create_report(item))
    print_json("READ - GetItem por id_reporte", get_report(report_id))

    user_result = list_reports_by_user("USUARIO#1")
    print_json("READ - Query por usuario usando el índice", {
        "items": user_result.get("Items", []),
        "count": user_result.get("Count"),
        "scanned_count": user_result.get("ScannedCount"),
        "consumed_capacity": user_result.get("ConsumedCapacity"),
    })

    print_json("UPDATE - UpdateItem estado a En proceso",
               update_report_state(report_id, "En proceso"))
    print_json("READ - Query principal por estado usando el índice",
               query_state_until_visible("En proceso", report_id))

    scan_result = scan_by_state_inefficiently("En proceso", limit=100)
    print_json("SCAN - búsqueda ineficiente (máximo 100 elementos)", {
        "items": scan_result.get("Items", []),
        "count": scan_result.get("Count"),
        "scanned_count": scan_result.get("ScannedCount"),
        "consumed_capacity": scan_result.get("ConsumedCapacity"),
        "note": "Scan lee elementos y después filtra; Limit acota esta demostración.",
    })
    print_json("DELETE - DeleteItem", delete_report(report_id))


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] != "demo":
        print("Uso: python crud_reportes.py demo")
        raise SystemExit(2)
    run_demo()
