from flask import Blueprint, request, Response
from airtable_client import get_record, update_record, check_role

doc_act_bp = Blueprint("doc_create", __name__)


@doc_act_bp.route("/document_activity", methods=["POST"])
def document_activity():
    data = request.json
    temp_id = data.get("recordId")  # ID записи, только что добавленной формой

    if not temp_id:
        return Response("❌ Нет recordId", status=400)

    temp_rec = get_record("Документы - Активность", temp_id)
    temp_fields = temp_rec.get("fields", {})
    base_ids = temp_rec.get("ID документа")
    has_permission = check_role(temp_rec, ['R.02', 'R.17'])

    if has_permission:
        activity_type = temp_fields.get("Вид активности")
        activity_dict = {
            'Перевод в "Актуальный" (Статус)': "Актуальный",
            'Статус в "Скоро истечет" (Статус)': "Скоро истечет",
            'Перевод в "Справочный" (Статус)': "Справочный",
            'Сдача в архив (Статус)': "Архив",
            'Уничтожение (Статус)': "Уничтожен",
            'Приобрести (Статус)': "Приобрести"
        }

        fields = {
            "Вид активности": activity_dict[activity_type],
        }

        for doc in base_ids:
            update_record("Документы", doc, fields)
        return Response("✅ Запись обновлена", status=200)
    else:
        return Response("❌ Нет прав", status=403)
