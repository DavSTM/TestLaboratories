from flask import Blueprint, jsonify
from airtable_client import get_record, get_all_records

test_bp = Blueprint("test", __name__)


@test_bp.route("/test", methods=["GET"])
def test():
    roles = ["R.01", "R.17"]
    result = False
    record = get_record("Документы", "recZh6hTUe9fSfgBe")

    created_by = record.get("fields", {}).get("Created By")
    laboratory = record.get("fields", {}).get("Лаборатория")

    personnel = get_all_records("Персонал")

    role_ids = []
    for person in personnel:
        if (created_by["email"] == person.get("fields", {}).get("Электронная почта")
                and laboratory == person.get("fields", {}).get("Лаборатория")):
            role_ids = person.get("fields", {}).get("Коды ролей")
            break

    role_names = []
    for rid in role_ids:
        role_record = get_record("Персонал (Роли)", rid)
        code = role_record.get("fields", {}).get("Код роли")
        if code:
            role_names.append(code)

    if any(role in role_names for role in roles):
        result = True

    print(record)
    return jsonify({"result": result})
