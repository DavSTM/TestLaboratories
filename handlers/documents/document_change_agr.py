from datetime import date

from flask import Blueprint, request, Response
from airtable_client import get_record, update_record, delete_record
from handlers.functions import get_records_by_transfer_id, person_confirm

doc_change_agr_bp = Blueprint("document_change_agr", __name__)


@doc_change_agr_bp.route("/document_change_agreed", methods=["POST"])
def document_change_agreed():
    """
    Согласование введенных или измененных документов
    """
    (temp_record_id, temp_record, temp_fields,
     base_record_id, base_record, base_fields,
     user_email) = get_records_by_transfer_id("Документы - Введение и изменения", booSame=True)


    person_confirm("Документы - Введение и изменения", temp_record_id, base_record_id, base_record,
                   "Согласовано - ID", "Согласовано - Подписи",
                   "Согласовано - Дата", user_email, booSame=True)

    person_confirm("Документы - Введение и изменения", temp_record_id, base_record_id, base_record,
                   "Утверждаю - ID", "Утверждаю - Подпись", "Утверждаю - Дата",
                   user_email, booSame=True)

    return Response("✅ Подписано", status=200)
