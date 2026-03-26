from __future__ import annotations

import zipfile
from pathlib import Path

from backend.app.api.tasks import create_task, task_store
from backend.app.converters.docx import convert_docx
from backend.app.converters.pdf import convert_pdf
from backend.app.converters.xlsx import convert_xlsx
from backend.app.services.storage import StorageService
from backend.app.worker import process_task


def _write_docx(path: Path, paragraphs: list[str]) -> None:
    body = "".join(
        f"<w:p><w:r><w:t>{text}</w:t></w:r></w:p>" for text in paragraphs
    )
    document = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>{body}</w:body>
</w:document>
"""
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", document)


def _write_xlsx(path: Path, rows: list[list[str]]) -> None:
    xml_rows = []
    for row_index, row in enumerate(rows, start=1):
        cells = []
        for col_index, value in enumerate(row, start=1):
            cell_ref = f"{chr(64 + col_index)}{row_index}"
            cells.append(
                f'<c r="{cell_ref}" t="inlineStr"><is><t>{value}</t></is></c>'
            )
        xml_rows.append(f"<row r=\"{row_index}\">{''.join(cells)}</row>")

    sheet = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <sheetData>{rows}</sheetData>
</worksheet>
""".format(rows="".join(xml_rows))
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("xl/worksheets/sheet1.xml", sheet)


def test_docx_converter_returns_markdown(tmp_path: Path) -> None:
    source = tmp_path / "sample.docx"
    _write_docx(source, ["Document Title", "Body text"])

    result = convert_docx(source)

    assert result.markdown.startswith("# Document Title")
    assert "Body text" in result.markdown
    assert result.warnings == ()


def test_pdf_converter_extracts_embedded_text(tmp_path: Path) -> None:
    source = tmp_path / "sample.pdf"
    source.write_bytes(b"%PDF-1.4\n1 0 obj\n(Hello PDF) Tj\nendobj\n")

    result = convert_pdf(source)

    assert result.markdown.startswith("# sample")
    assert "Hello PDF" in result.markdown


def test_xlsx_converter_renders_markdown_table(tmp_path: Path) -> None:
    source = tmp_path / "sample.xlsx"
    _write_xlsx(source, [["Name", "Value"], ["Alpha", "1"]])

    result = convert_xlsx(source)

    assert "| Name | Value |" in result.markdown
    assert "| Alpha | 1 |" in result.markdown


def test_storage_round_trip(tmp_path: Path) -> None:
    storage = StorageService(tmp_path / "storage")

    markdown_path = storage.write_markdown("task123", "# Example")
    artifact_path = storage.write_artifact("task123", "payload.bin", b"abc")

    assert markdown_path.read_text(encoding="utf-8") == "# Example"
    assert storage.read_markdown("task123") == "# Example"
    assert artifact_path.read_bytes() == b"abc"


def test_worker_routes_conversion_and_updates_task_store(tmp_path: Path) -> None:
    task_store.clear()
    source = tmp_path / "sample.docx"
    _write_docx(source, ["Work Item", "Converted body"])
    task = create_task(file_name="sample.docx", file_bytes=source.read_bytes())
    storage = StorageService(tmp_path / "storage")

    updated = process_task(task.task_id, source, storage)

    assert updated.status == "success"
    assert task_store[task.task_id].status == "success"
    assert storage.read_markdown(task.task_id).startswith("# Work Item")

