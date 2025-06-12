from flask import Blueprint, request, Response
from airtable_client import get_record, update_record, delete_record

ack_bp = Blueprint("ack", __name__)

@ack_bp.route("/acknowledge", methods=["POST"])
def acknowledge():
    data = request.json
    temp_id = data.get("recordId")  # ID записи, только что добавленной формой

    if not temp_id:
        return Response("❌ Нет recordId", status=400)

    temp_rec = get_record("Журнал распоряжений", temp_id)
    fields = temp_rec.get("fields", {})
    base_id = fields.get("Переданный ID")
    user = fields.get("Кто отправил", [{}])[0]
    user_email = user.get("email")

    if not base_id or not user_email:
        return Response("❌ Отсутствует email или переданный ID", status=400)

    base_rec = get_record("Журнал распоряжений", base_id)
    base_fields = base_rec.get("fields", {})
    performers_ids = base_fields.get("Исполнители", [])
    signatures = base_fields.get("Подписи", [])

    # Проверка: email отправителя есть в "Исполнителях"
    match = False
    for person_id in performers_ids:
        person = get_record("Персонал", person_id)
        if person.get("fields", {}).get("Электронная почта") == user_email:
            match = True
            break

    if match:
        if user_email not in signatures:
            signatures.append(user_email)
            update_record("Журнал распоряжений", base_id, {
                "Подписи": signatures
            })

    # Удаляем временную запись, в любом случае
    delete_record("Журнал распоряжений", temp_id)

    return "✅ Обработка завершена"
