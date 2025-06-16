import os, requests
from dotenv import load_dotenv
from flask import jsonify, request, Response

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
