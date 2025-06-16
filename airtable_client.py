import os, requests
from dotenv import load_dotenv
from flask import jsonify

load_dotenv()

API_KEY = os.environ.get("AIRTABLE_API_KEY")
BASE_ID = os.environ.get("AIRTABLE_BASE_ID")
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}


def get_record(table, record_id):
    url = f"https://api.airtable.com/v0/{BASE_ID}/{table}/{record_id}"
    return requests.get(url, headers=HEADERS).json()


def get_all_records(table):
    url = f"https://api.airtable.com/v0/{BASE_ID}/{table}"
    records = []
    offset = None

    while True:
        params = {"offset": offset} if offset else {}
        response = requests.get(url, headers=HEADERS, params=params)
        data = response.json()
        records.extend(data.get("records", []))
        offset = data.get("offset")
        if not offset:
            break
    return records


def create_record(table, fields):
    url = f"https://api.airtable.com/v0/{BASE_ID}/{table}"
    return requests.post(url, headers=HEADERS, json={"fields": fields}).json()


def update_record(table, record_id, fields):
    url = f"https://api.airtable.com/v0/{BASE_ID}/{table}/{record_id}"
    return requests.patch(url, headers=HEADERS, json={"fields": fields}).json()


def delete_record(table, record_id):
    url = f"https://api.airtable.com/v0/{BASE_ID}/{table}/{record_id}"
    return requests.delete(url, headers=HEADERS).json()


def check_role(record, roles):
    result = False

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

    return jsonify({"result": result})
