from flask import Blueprint, request, Response
from airtable_client import get_record, update_record, delete_record

ack_bp = Blueprint("ack", __name__)


@ack_bp.route("/orders_acknowledge", methods=["POST"])
def orders_acknowledge():
    """
    Обработка временной записи:
    - Получает Created By и Переданный ID.
    - Находит основную запись.
    - Если пользователь есть среди Исполнителей → добавляет в Ознакомлены.
    - Если пользователь выдал распоряжение → добавляет в Утверждаю.
    - Удаляет временную запись.
    """
    data = request.json
    temp_id = data.get("recordId")

    if not temp_id:
        return Response("❌ Нет recordId", status=400)

    temp_record = get_record("Журнал распоряжений", temp_id)
    if not temp_record:
        return Response(f"❌ Временная запись {temp_id} не найдена", status=404)

    temp_fields = temp_record.get("fields", {})
    base_record_id = temp_fields.get("Переданный ID")
    created_by_user = temp_fields.get("Created By") or {}

    if not base_record_id or not created_by_user:
        return Response("❌ Отсутствует 'Переданный ID' или 'Created By'", status=400)

    user_email = created_by_user.get("email")
    if not user_email:
        return Response("❌ Не указан email пользователя", status=400)

    # Получаем основную запись
    base_record = get_record("Журнал распоряжений", base_record_id)
    if not base_record:
        return Response(f"❌ Основная запись {base_record_id} не найдена", status=404)

    base_fields = base_record.get("fields", {})
    performer_ids = base_fields.get("Исполнители", [])
    issuer_id = base_fields.get("Распоряжение выдал")
    acknowledged_users = base_fields.get("Ознакомлены", [])
    approved_user = base_fields.get("Утверждаю")

    updated_fields = {}
    user_ack_obj = None
    user_appr_obj = None

    # Проверяем исполнителей
    for person_id in performer_ids:
        person = get_record("Персонал", person_id)
        if not person:
            continue
        person_fields = person.get("fields", {})
        if person_fields.get("Электронная почта") == user_email:
            user_ack_obj = person_fields.get("User")
            break

    # Проверяем выдавших распоряжение
    for person_id in issuer_id:
        person = get_record("Персонал", person_id)
        if not person:
            continue
        person_fields = person.get("fields", {})
        if person_fields.get("Электронная почта") == user_email:
            user_appr_obj = person_fields.get("User")
            break

    # Добавляем в "Ознакомлены"
    if user_ack_obj:
        user_id = user_ack_obj.get("id")
        acknowledged_ids = [u.get("id") for u in acknowledged_users if isinstance(u, dict)]
        if user_id and user_id not in acknowledged_ids:
            acknowledged_users.append(user_ack_obj)
            updated_fields["Ознакомлены"] = acknowledged_users

    # Добавляем в "Утверждаю"
    if user_appr_obj:
        user_id = user_appr_obj.get("id")
        approved_user_id = approved_user.get("id") if isinstance(approved_user, dict) else None

        if user_id and user_id != approved_user_id:
            updated_fields["Утверждаю"] = user_appr_obj

    # Обновление записи
    if updated_fields:
        update_record(
            table="Журнал распоряжений",
            record_id=base_record_id,
            fields=updated_fields
        )

    # Удаление временной записи
    delete_record("Журнал распоряжений", temp_id)

    return "✅ Обработка завершена"
