from datetime import date

from flask import request, Response
from airtable_client import get_record, update_record, delete_record, get_all_records


def check_role(record, roles):
    result = False

    created_by = record.get("fields", {}).get("Created By")
    laboratory = record.get("fields", {}).get("Лаборатория")

    personnel = get_all_records("Персонал - Перечень")

    role_ids = []
    for person in personnel:
        if created_by["email"] == person.get("fields", {}).get(
            "Электронная почта"
        ) and laboratory == person.get("fields", {}).get("Лаборатория"):
            role_ids = person.get("fields", {}).get("Коды ролей")
            break

    role_names = []
    for rid in role_ids:
        role_record = get_record("Персонал - Роли", rid)
        code = role_record.get("fields", {}).get("Код роли")
        if code:
            role_names.append(code)

    if any(role in role_names for role in roles):
        result = True

    return result


def get_records_by_transfer_id(temp_table, base_table=None, booSame=False):
    data = request.json
    temp_record_id = data.get("recordId")
    if not temp_record_id:
        return Response("❌ Нет recordId", status=400)

    temp_record = get_record(temp_table, temp_record_id)
    if not temp_record:
        return Response(f"❌ Временная запись {temp_record_id} не найдена", status=404)

    temp_fields = temp_record.get("fields", {})
    base_record_id = temp_fields.get("Переданный ID")
    if not base_record_id:
        return Response("❌ Отсутствует 'Переданный ID'", status=400)

    if booSame:
        base_record = get_record(temp_table, base_record_id)
    else:
        base_record = get_record(base_table, base_record_id)

    if not base_record:
        return Response(f"❌ Основная запись {base_record_id} не найдена", status=404)
    base_fields = base_record.get("fields", {})

    created_by_user = temp_fields.get("Created By") or {}

    if not created_by_user:
        return Response("❌ Отсутствует 'Created By'", status=400)

    user_email = created_by_user.get("email")
    if not user_email:
        return Response("❌ Не указан email пользователя", status=400)

    return (
        temp_record_id,
        temp_record,
        temp_fields,
        base_record_id,
        base_record,
        base_fields,
        user_email,
    )


def person_confirm(
    table,
    temp_record_id,
    base_record_id,
    base_record,
    personnel_id,
    personnel_signs,
    personnel_signs_dates,
    created_by_user_email,
    booSame=False,
):

    base_fields = base_record.get("fields", {})
    ack_user_rec = base_fields.get(personnel_id, [])
    ack_users = base_fields.get(personnel_signs, [])
    ack_users_dates = base_fields.get(personnel_signs_dates, "")
    today_str = date.today().strftime("%d.%m.%Y")

    updated_fields = {}
    user_obj = None
    user_name = None
    # Проверяем искомых
    for person_id in ack_user_rec:
        person = get_record("Персонал - Перечень", person_id)
        if not person:
            continue
        person_fields = person.get("fields", {})
        if person_fields.get("Электронная почта") == created_by_user_email:
            user_obj = person_fields.get("User")
            user_name = person_fields.get("Фамилия, имя")
            break

    # Добавляем в искомых
    if user_obj:
        user_id = user_obj.get("id")
        ack_users_ids = [u.get("id") for u in ack_users if isinstance(u, dict)]
        if user_id and user_id not in ack_users_ids:
            ack_users.append(user_obj)
            updated_fields[personnel_signs] = ack_users
            updated_fields[personnel_signs_dates] = (
                ack_users_dates + f"{user_name} - {today_str}\n"
            )
    # Обновление записи
    if updated_fields:
        update_record(table=table, record_id=base_record_id, fields=updated_fields)

    if booSame:
        # Удаление временной записи
        delete_record(table, temp_record_id)

    return "✅ Обработка завершена"
