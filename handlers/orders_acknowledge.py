from flask import Blueprint, request, Response
from airtable_client import get_record, update_record, delete_record

ack_bp = Blueprint("ack", __name__)

@ack_bp.route("/orders_acknowledge", methods=["POST"])
def orders_acknowledge():
    data = request.json
    temp_id = data.get("recordId")  # ID записи, только что добавленной формой

    if not temp_id:
        return Response("❌ Нет recordId", status=400)

    temp_rec = get_record("Журнал распоряжений", temp_id)
    fields = temp_rec.get("fields", {})
    base_id = fields.get("Переданный ID")
    user = fields.get("Распоряжение выдал", [{}])
    user_email = user.get("email")
    if not base_id or not user_email:
        return Response(f"❌ Отсутствует email {user} или переданный ID", status=400)

    base_rec = get_record("Журнал распоряжений", base_id)
    base_fields = base_rec.get("fields", {})
    performers_ids = base_fields.get("Исполнители", [])
    signatures = base_fields.get("Подписи", [])

    # Проверка: email отправителя есть в "Исполнителях"
    match = []
    for person_id in performers_ids:
        person = get_record("Персонал", person_id)
        if person.get("fields", {}).get("Электронная почта") == user_email:
            user_ava = person.get("fields", {}).get("User")
            if user_ava:
                match.append(user_ava)


    if match:
        for perf in match:
            if user_email not in [u.get("email") for u in signatures]:
                signatures.append(perf)

        update_record(
            table="Журнал распоряжений",
            record_id=base_id,
            fields={
                "Подписи": signatures
            }
        )

    # Удаляем временную запись, в любом случае
    delete_record("Журнал распоряжений", temp_id)

    return f"✅ Обработка завершена"
