from flask import Flask, request
from handlers import process_record, transfer_doc

app = Flask(__name__)

@app.route("/")
def home():
    return "🟢 Сервер работает."

@app.route("/process", methods=["GET"])
def process():
    record_id = request.args.get("recordId")
    return process_record.handle(record_id)

@app.route("/transfer", methods=["POST"])
def transfer():
    return transfer_doc.handle()
