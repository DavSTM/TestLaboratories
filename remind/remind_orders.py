from remind_base import get_all_records, send_telegram, extract_user_id

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
        performers = fields.get("Исполнители", [])  # record IDs из Персонал
        signatures = fields.get("Подписи", [])      # User объекты

        # Получаем список user.id из Подписи
        signed_user_ids = [
            user["id"] for user in signatures
            if isinstance(user, dict) and "id" in user
        ]

        missing = []

        for performer_id in performers:
            person = personnel.get(performer_id)
            if not person:
                continue

            user_id = extract_user_id(person)

            if user_id and user_id not in signed_user_ids:
                tg_id = person.get("fields", {}).get("Telegram ID")
                if tg_id:
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
