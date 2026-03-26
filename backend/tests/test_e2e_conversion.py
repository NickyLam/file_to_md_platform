from pathlib import Path
from zipfile import ZipFile

from backend.app.api.tasks import create_task, task_store
from backend.app.services.storage import StorageService
from backend.app.worker import process_task


def _write_docx(path: Path, text: str) -> None:
    document = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body><w:p><w:r><w:t>{text}</w:t></w:r></w:p></w:body>
</w:document>
"""
    with ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", document)


def _write_xlsx(path: Path, title: str, value: str) -> None:
    sheet = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <sheetData>
    <row r="1">
      <c r="A1" t="inlineStr"><is><t>{title}</t></is></c>
      <c r="B1" t="inlineStr"><is><t>Value</t></is></c>
    </row>
    <row r="2">
      <c r="A2" t="inlineStr"><is><t>{value}</t></is></c>
      <c r="B2" t="inlineStr"><is><t>1</t></is></c>
    </row>
  </sheetData>
</worksheet>
"""
    with ZipFile(path, "w") as archive:
        archive.writestr("xl/worksheets/sheet1.xml", sheet)


def _write_pdf(path: Path, text: str) -> None:
    path.write_bytes(f"%PDF-1.4\n1 0 obj\n({text}) Tj\nendobj\n".encode("latin1"))


def test_end_to_end_conversion_for_supported_types(tmp_path: Path) -> None:
    task_store.clear()
    storage = StorageService(tmp_path / "storage")

    cases = [
        ("sample.docx", "docx", _write_docx, "Doc Title"),
        ("sample.pdf", "pdf", _write_pdf, "Pdf Body"),
        ("sample.xlsx", "xlsx", _write_xlsx, "Name"),
    ]

    for filename, file_type, writer, value in cases:
        source = tmp_path / filename
        if file_type == "docx":
            writer(source, value)
        elif file_type == "pdf":
            writer(source, value)
        else:
            writer(source, value, "Row")

        task = create_task(file_name=filename, file_bytes=source.read_bytes())
        updated = process_task(task.task_id, source, storage)

        assert updated.status in {"success", "success_with_warnings"}
        assert storage.read_markdown(task.task_id)

