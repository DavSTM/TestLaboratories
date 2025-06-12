from flask import request, Response
from airtable_client import get_record, create_record, delete_record

def handle():
    data = request.json
    update_id = data.get("recordId")
    if not update_id:
        return Response("❌ Нет recordId", 400)

    record = get_record("_Update_Документы", update_id)
    fields = record.get("fields", {})

    if "Роль" in fields.get("Разрешённые", []):
        # переносим запись
        create_record("Документы", fields)
        return "✅ Запись перенесена", 200
    else:
        delete_record("_Update_Документы", update_id)
        return "❌ Недостаточно прав, запись удалена", 403
