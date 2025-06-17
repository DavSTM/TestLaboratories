from airtable_client import get_all_records
from remind.remind_base import send_telegram, extract_user_id


def main():
    """
    Напоминание в Документы - Ознакомление
    """
    personnel = {p["id"]: p for p in get_all_records("Персонал - Перечень")}
    print(f"📋 Загружено {len(personnel)} сотрудников")

    records = get_all_records("Документы - Ознакомление")
    print(f"📑 Обрабатывается {len(records)} записей")

    total_sent = 0

    for entry in records:
        fields = entry.get("fields", {})
        doc_number = fields.get("ID")

        to_ack_ids = fields.get("Ознакомлены - ID", [])  # linked records (person IDs)
        signed_users = fields.get("Ознакомлены - Подписи", [])  # Users (collaborators)

        signed_user_ids = {
            u.get("id") for u in signed_users if isinstance(u, dict) and "id" in u
        }
        for person_id in to_ack_ids:
            person = personnel.get(person_id)
            if not person:
                continue

            user_id = extract_user_id(person)
            tg_id = person.get("fields", {}).get("Telegram ID")

            if not user_id or not tg_id:
                continue
            if user_id in signed_user_ids:
                continue  # уже ознакомлен

            msg = f"🖊 Пожалуйста, ознакомьтесь с документом №{doc_number}"
            code = send_telegram(tg_id, msg)
            if code == 200:
                print(f"✅ {tg_id}: отправлено")
                total_sent += 1
            else:
                print(f"⚠️ {tg_id}: ошибка {code}")

    print(f"\n🎉 Всего отправлено: {total_sent} напоминаний")


if __name__ == "__main__":
    main()
