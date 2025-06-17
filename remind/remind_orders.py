from airtable_client import get_all_records
from remind.remind_base import send_telegram, extract_user_id

def main():
    # Кэшируем сотрудников
    personnel = {p["id"]: p for p in get_all_records("Персонал")}
    print(f"📋 Загружено {len(personnel)} сотрудников")

    journal = get_all_records("Журнал распоряжений")
    print(f"📑 Обрабатывается {len(journal)} распоряжений")

    total_sent = 0

    for entry in journal:
        fields = entry.get("fields", {})
        record_number = fields.get("ID")  # Номер распоряжения

        performers = fields.get("Исполнители - ID", [])              # list of record_ids
        issuer_id = fields.get("Распоряжение выдал - ID", [])
        signed_users = fields.get("Ознакомлены - Подписи", [])                # list of User-objects

        # Преобразуем подписавшихся в set user_id
        signed_user_ids = {
            u.get("id") for u in signed_users if isinstance(u, dict) and "id" in u
        }

        # Формируем список сотрудников, которым нужно отправить напоминание
        pending_person_ids = set(performers)
        if issuer_id:
            pending_person_ids.add(issuer_id[0])
        for person_id in pending_person_ids:
            person = personnel.get(person_id)
            if not person:
                continue

            user_id = extract_user_id(person)
            if not user_id or user_id in signed_user_ids:
                continue  # уже подписался или нет User

            tg_id = person.get("fields", {}).get("Telegram ID")
            if not tg_id:
                continue

            msg = f"🖊 Пожалуйста, ознакомьтесь с распоряжением №{record_number}"
            code = send_telegram(tg_id, msg)
            if code == 200:
                print(f"✅ {tg_id}: отправлено")
                total_sent += 1
            else:
                print(f"⚠️ {tg_id}: ошибка {code}")

    print(f"\n🎉 Всего отправлено: {total_sent} напоминаний")

if __name__ == "__main__":
    main()
