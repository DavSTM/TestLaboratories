from datetime import date

from flask import Blueprint, request, Response
from airtable_client import get_record, update_record, delete_record
from handlers.functions import get_records_by_transfer_id, person_confirm

doc_acknowledgement_ack_bp = Blueprint("document_acknowledgement_ack", __name__)


@doc_acknowledgement_ack_bp.route("/document_acknowledgement_acknowledge", methods=["POST"])
def document_change_agreed():
    """
    Ознакомление с документами в Документы - Ознакомление
    """
    (temp_record_id, temp_record, temp_fields,
     base_record_id, base_record, base_fields,
     user_email) = get_records_by_transfer_id("Документы - Ознакомление", booSame=True)

    person_confirm("Документы - Ознакомление", temp_record_id, base_record_id, base_record,
                   "Ознакомлены - ID", "Ознакомлены - Подписи",
                   "Ознакомлены - Дата", user_email, booSame=True)

    return "✅ Обработка завершена"
