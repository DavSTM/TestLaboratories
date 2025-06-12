from flask import Response
from airtable_client import get_record

def handle(record_id):
    if not record_id:
        return Response("❌ Нет recordId", status=400)

    record = get_record("Персонал", record_id)
    roles = record.get("fields", {}).get("Роли", [])

    if "R.17" in roles:
        return "✅ Роль R.17 подтверждена"
    else:
        return Response("❌ Роль R.17 отсутствует", status=403)
