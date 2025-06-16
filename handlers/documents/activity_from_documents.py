from flask import Blueprint, request, Response
from airtable_client import get_record, create_record, delete_record
from handlers.functions import check_role

doc_create_bp = Blueprint("doc_create", __name__)


@doc_create_bp.route("/document_create", methods=["POST"])
def activity_from_documents():
    """
    При добавлении нового документа в Документы, если статус "Актуальный",
    то добавляется запись в Документы - Активность
    :return:
    """
    data = request.json
    temp_id = data.get("recordId")

    if not temp_id:
        return Response("❌ Нет recordId", status=400)

    base_rec = get_record("Документы", temp_id)
    base_fields = base_rec.get("fields", {})
    has_permission = check_role(base_rec, ['R.02', 'R.17'])

    if has_permission and base_fields.get("Статус") == "Актуальный":
        fields = {
            "Лаборатория": base_fields.get("Лаборатория"),
            "ID документа": [base_fields.get("id", '')],
            "Дата": base_fields.get("Дата введения"),
            "Вид активности": "Актуализация",
            "Auto": True
        }

        create_record("Документы - Активность", fields)
        return Response("✅ Запись создана", status=200)
    else:
        delete_record("Документы", temp_id)
        return Response("❌ Нет прав — запись удалена", status=403)
