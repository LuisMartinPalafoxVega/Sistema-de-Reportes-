"""Práctica 09: API pública de solo lectura para ReportesColoniasP07.

La función usa el rol de ejecución de Lambda para consultar DynamoDB. No expone
operaciones de escritura o borrado, por lo que el endpoint público no puede
modificar datos del proyecto.
"""

import json
import os
from decimal import Decimal

import boto3


TABLE_NAME = os.environ.get("TABLE_NAME", "ReportesColoniasP07")
REGION = os.environ.get("AWS_REGION", "us-east-1")
table = boto3.resource("dynamodb", region_name=REGION).Table(TABLE_NAME)


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super().default(obj)


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json; charset=utf-8",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body, ensure_ascii=False, cls=DecimalEncoder),
    }


def lambda_handler(event, context):
    """Devuelve hasta 20 reportes sin permitir escritura."""
    params = event.get("queryStringParameters") or {}
    try:
        limit = min(max(int(params.get("limit", "20")), 1), 20)
    except ValueError:
        return response(400, {"error": "limit debe ser un entero entre 1 y 20"})

    result = table.scan(Limit=limit)
    items = result.get("Items", [])
    items.sort(key=lambda item: str(item.get("fecha_creacion", "")), reverse=True)
    return response(200, {
        "ok": True,
        "table": TABLE_NAME,
        "count": len(items),
        "items": items,
    })
