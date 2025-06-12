from flask import Blueprint, request, Response
from airtable_client import get_record

role_bp = Blueprint("role", __name__)

@role_bp.route("/check-role", methods=["GET"])
def check_role():
    record_id = request.args.get("recordId")
    if not record_id:
        return Response("❌ Нет recordId", status=400)

    record = get_record("Персонал", record_id)
    # Получить коды ролей в виде record_id
    role_ids = record.get("fields", {}).get("Коды ролей", [])

    role_names = []
    for rid in role_ids:
        role_record = get_record("Персонал (Роли)", rid)
        code = role_record.get("fields", {}).get("Код роли")
        if code:
            role_names.append(code)

    if "R.17" in role_names:
        return "✅ Роль R.17 подтверждена"
    else:
        return Response("❌ Роль R.17 отсутствует", status=403)
