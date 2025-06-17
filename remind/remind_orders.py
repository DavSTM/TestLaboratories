from airtable_client import get_all_records
from remind.remind_base import send_telegram, extract_user_id


def main():
    """
    Напоминание о Журнале распоряжений
    """
    personnel = {p["id"]: p for p in get_all_records("Персонал - Перечень")}
    print(f"📋 Загружено {len(personnel)} сотрудников")

    journal = get_all_records("Журнал распоряжений")
    print(f"📑 Обрабатывается {len(journal)} распоряжений")

    total_sent = 0

    for entry in journal:
        fields = entry.get("fields", {})
        record_number = fields.get("ID")

        performers = fields.get("Исполнители - ID", [])  # list of record_ids
        issuer_id_list = fields.get("Распоряжение выдал - ID", [])
        issuer_id = (
            issuer_id_list[0]
            if isinstance(issuer_id_list, list) and issuer_id_list
            else None
        )

        signed_performers = fields.get("Ознакомлены - Подписи", [])
        signed_issuer = fields.get("Утверждаю - Подпись", [])

        # user_id'ы подписавшихся исполнителей
        signed_performer_ids = {
            u.get("id") for u in signed_performers if isinstance(u, dict) and "id" in u
        }
        # user_id'ы подписавшего утверждающего
        signed_issuer_ids = {
            u.get("id") for u in signed_issuer if isinstance(u, dict) and "id" in u
        }

        # Проверка исполнителей
        for person_id in performers:
            person = personnel.get(person_id)
            if not person:
                continue
            user_id = extract_user_id(person)
            tg_id = person.get("fields", {}).get("Telegram ID")
            if not user_id or not tg_id:
                continue
            if user_id in signed_performer_ids:
                continue

            msg = f"🖊 Пожалуйста, ознакомьтесь с распоряжением №{record_number}"
            code = send_telegram(tg_id, msg)
            if code == 200:
                print(f"✅ {tg_id}: отправлено")
                total_sent += 1
            else:
                print(f"⚠️ {tg_id}: ошибка {code}")

        # Проверка утверждающего
        if issuer_id:
            person = personnel.get(issuer_id)
            if person:
                user_id = extract_user_id(person)
                tg_id = person.get("fields", {}).get("Telegram ID")
                if user_id and tg_id and user_id not in signed_issuer_ids:
                    msg = f"🖊 Пожалуйста, утвердите распоряжение №{record_number}"
                    code = send_telegram(tg_id, msg)
                    if code == 200:
                        print(f"✅ {tg_id}: отправлено")
                        total_sent += 1
                    else:
                        print(f"⚠️ {tg_id}: ошибка {code}")

    print(f"\n🎉 Всего отправлено: {total_sent} напоминаний")


if __name__ == "__main__":
    main()
