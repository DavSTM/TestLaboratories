from datetime import datetime

from flask import Blueprint, request, Response
from airtable_client import get_record, update_record, delete_record, get_all_records
from handlers.functions import get_records_by_transfer_id, person_confirm

doc_change_notes_bp = Blueprint("document_change_notes", __name__)


@doc_change_notes_bp.route("/document_change_notes", methods=["POST"])
def document_change_notes():
    """
    Замечания и предложения в Документы - Введение и изменения
    """
    (temp_record_id, temp_record, temp_fields,
     base_record_id, base_record, base_fields,
     user_email) = get_records_by_transfer_id("Документы - Введение и изменения", booSame=True)


    notes_new = temp_fields.get("Замечания и предложения")
    notes_old = base_fields.get("Замечания и предложения", '')
    personnel = get_all_records("Персонал - Перечень")
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    person_name = ''
    for person in personnel:
        if user_email == person.get("fields", {}).get("Электронная почта"):
            person_name = person.get("fields", {}).get("Фамилия, имя")
            break
    notes_add = notes_old + f"[{person_name} - {timestamp}]:\n{notes_new}\n\n"

    updated_fields = {
        "Замечания и предложения": notes_add,
    }
    update_record("Документы - Введение и изменения",
                  record_id=base_record_id, fields=updated_fields)

    delete_record("Документы - Введение и изменения", temp_record_id)

    return Response("✅ Обновлено", status=200)
