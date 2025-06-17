from flask import Blueprint, request, Response
from airtable_client import get_record, update_record, delete_record
from handlers.functions import get_records_by_transfer_id, person_confirm

ack_bp = Blueprint("ack", __name__)


@ack_bp.route("/orders_acknowledge", methods=["POST"])
def orders_acknowledge():
    (temp_record_id, temp_record, temp_fields,
     base_record_id, base_record, base_fields,
     user_email) = get_records_by_transfer_id("Журнал распоряжений", booSame=True)

    person_confirm("Журнал распоряжений", base_record_id, base_record,
                   "Исполнители - ID", "Ознакомлены - Подписи",
                   "Ознакомлены - Дата", user_email, booSame=True)

    person_confirm("Журнал распоряжений", base_record_id, base_record,
                   "Распоряжение выдал - ID", "Утверждаю - Подпись",
                   "Утверждаю - Дата", user_email, booSame=True)
    return "✅ Обработка завершена"
