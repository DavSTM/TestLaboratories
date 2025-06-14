from flask import Blueprint, request, Response
from airtable_client import get_record, create_record, delete_record, check_role

doc_create_bp = Blueprint("doc_create", __name__)


@doc_create_bp.route("/document_create", methods=["POST"])
def document_create():
    data = request.json
    temp_id = data.get("recordId")  # ID записи, только что добавленной формой

    if not temp_id:
        return Response("❌ Нет recordId", status=400)

    temp_rec = get_record("Документы", temp_id)
    has_permission = check_role(temp_id, "Документы", ['R.17'])

    if has_permission:
        fields = {
            "Лаборатория": temp_rec.get("fields", {}).get("Лаборатория"),
            "ID документа": [temp_rec.get("id", '')],
            "Дата": temp_rec.get("fields", {}).get("Дата введения"),
            "Вид активности": "Актуализация",
        }
        create_record("Документы - Активность", fields)
        return Response("✅ Запись создана", status=200)
    else:
        delete_record("Документы", temp_id)
        return Response("❌ Нет прав — запись удалена", status=403)
