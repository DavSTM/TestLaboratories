from remind_base import get_all_records, send_telegram, extract_user_id

def main():
    personnel = {p["id"]: p for p in get_all_records("Персонал")}
    print(f"📋 Загружено {len(personnel)} сотрудников")

    activity = get_all_records("Персонал - Активность")
    print(f"📑 Обрабатывается {len(activity)} записей активности")

    total_sent = 0

    for entry in activity:
        fields = entry.get("fields", {})
        activity_id = fields.get("ID")

        # Списки record_id из "Персонал"
        whom_ids = fields.get("Персонал ID", [])
        bywhom_ids = fields.get("Кем проведено ID", [])

        # Подписавшиеся — user.id
        signed_whom = [
            u.get("id") for u in fields.get("Подписи (кого)", [])
            if isinstance(u, dict) and "id" in u
        ]
        signed_bywhom = [
            u.get("id") for u in fields.get("Подписи (кем)", [])
            if isinstance(u, dict) and "id" in u
        ]

        # Проверка по каждому из 2х списков
        for group, ids, signed, label in [
            ("Персонал ID", whom_ids, signed_whom, "Подписи (кого)"),
            ("Кем проведено ID", bywhom_ids, signed_bywhom, "Подписи (кем)")
        ]:
            for person_id in ids:
                person = personnel.get(person_id)
                if not person:
                    continue

                user_id = extract_user_id(person)

                if user_id and user_id not in signed:
                    tg_id = person.get("fields", {}).get("Telegram ID")
                    if tg_id:
                        msg = (f"🖊 Пожалуйста, подпишитесь в {label} в журнале Персонал (Активность) №{activity_id}")
                        code = send_telegram(tg_id, msg)
                        if code == 200:
                            print(f"✅ {tg_id}: отправлено")
                            total_sent += 1
                        else:
                            print(f"⚠️ {tg_id}: ошибка {code}")

    print(f"\n🎉 Всего отправлено: {total_sent} напоминаний")

if __name__ == "__main__":
    main()
