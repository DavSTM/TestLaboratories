from flask import Blueprint, Response
from airtable_client import update_record
from handlers.functions import check_role, get_records_by_transfer_id

doc_act_bp = Blueprint("doc_activity", __name__)


@doc_act_bp.route("/document_activity", methods=["POST"])
def document_activity():
    (temp_record_id, temp_record, temp_fields,
     base_record_id, base_record, base_fields,
     user_email) = get_records_by_transfer_id("Документы - Активность", booSame=True)

    has_permission = check_role(temp_record, ['R.02', 'R.17'])

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

        for doc in base_record_id:
            update_record("Документы", doc, fields)
        return Response("✅ Запись обновлена", status=200)
    else:
        return Response("❌ Нет прав", status=403)
