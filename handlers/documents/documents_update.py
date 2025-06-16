from flask import Blueprint, request, Response
from airtable_client import get_record, create_record, delete_record, check_role, update_record

doc_update_bp = Blueprint("doc_update", __name__)


@doc_update_bp.route("/document_update", methods=["POST"])
def document_update():
    data = request.json
    temp_id = data.get("recordId")  # ID записи, только что добавленной формой

    if not temp_id:
        return Response("❌ Нет recordId", status=400)

    temp_rec = get_record("_Документы", temp_id)
    temp_fields = temp_rec.get("fields", {})

    doc_refs = temp_fields.get("_Document") or []
    if not doc_refs:
        return Response("❌ Нет ссылки на Документы", status=400)
    base_rec = get_record("Документы", doc_refs[0])
    base_fields = base_rec.get("fields", {}) if base_rec else {}

    has_permission_02 = check_role(temp_rec, ['R.02'])
    has_permission_17 = check_role(temp_rec, ['R.17'])
    del_file = temp_fields.get("Удалить файлы")
    del_record = temp_fields.get("Delete")

    if (has_permission_02
            or (has_permission_17
                and temp_fields.get("Лаборатория") != "All")):
        if del_record:
            fields = {
                "Status": "Deleted"
            }
            update_record("Документы", base_rec.get("id"), fields)
            return Response("Запись в Документы удалена", status=200)

        fields = {
            "Лаборатория": temp_fields.get("Лаборатория"),
            "Дата введения": temp_fields.get("Дата введения"),
            "Дата утверждения": temp_fields.get("Дата утверждения"),
            "Обозначение документа": temp_fields.get("Обозначение документа"),
            "Оригинал": temp_fields.get("Оригинал"),
            "Наименование документа": temp_fields.get("Наименование документа"),
            "Номер редакции": temp_fields.get("Номер редакции"),
            "Краткое содержание": temp_fields.get("Краткое содержание"),
            "Вид документа": temp_fields.get("Вид документа"),
            "Категория документа": temp_fields.get("Категория документа"),
            "НД": temp_fields.get("НД"),
            "Легал": temp_fields.get("Легал"),
            "Носитель": temp_fields.get("Носитель"),
            "Язык": temp_fields.get("Язык"),
            "Местоположение": temp_fields.get("Местоположение"),
            "URL": temp_fields.get("URL"),
            "Откуда поступил": temp_fields.get("Откуда поступил"),
            "Взамен документа": temp_fields.get("Взамен документа"),
            "Заменен на": temp_fields.get("Заменен на"),
            "Срок действия": temp_fields.get("Срок действия"),
            "Источник актуализации": temp_fields.get("Источник актуализации"),
            "Примечания": temp_fields.get("Примечания"),
            "Уровень доступа": temp_fields.get("Уровень доступа"),
            "Ответственный за хранение": temp_fields.get("Ответственный за хранение")
        }

        if del_file:
            fields["Файлы"] = []
        else:
            existing_files = base_fields.get("Файлы") or []
            new_files_raw = temp_fields.get("Файлы") or []
            new_files = [
                {"url": f.get("url"), "filename": f.get("filename")}
                for f in new_files_raw
                if isinstance(f, dict) and f.get("url")
            ]

            fields["Файлы"] = existing_files + new_files

        update_record("Документы", doc_refs[0], fields)
        return Response("✅ Запись обновлена", status=200)
    else:
        delete_record("_Документы", temp_id)
        return Response("❌ Нет прав — запись удалена", status=403)


def prepare_files_field(base_fields, temp_fields, del_file=False):
    if del_file:
        return []

    # Получаем текущие файлы (из основной записи)
    existing_files = base_fields.get("Файлы") or []

    # Получаем новые файлы (из временной записи)
    new_files_raw = temp_fields.get("Файлы") or []

    # Очищаем только нужные поля: url + filename
    new_files = [
        {"url": f.get("url"), "filename": f.get("filename")}
        for f in new_files_raw
        if isinstance(f, dict) and f.get("url")
    ]

    return existing_files + new_files
