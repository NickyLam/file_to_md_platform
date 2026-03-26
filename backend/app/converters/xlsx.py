from pathlib import Path
from zipfile import BadZipFile, ZipFile

from xml.etree import ElementTree as ET

from backend.app.converters.base import ConversionResult


SHEET_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"


def _escape_cell(value: str) -> str:
    return value.replace("|", "\\|")


def _read_shared_strings(archive: ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []

    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    values: list[str] = []
    for item in root.findall(f".//{{{SHEET_NS}}}si"):
        text_parts = [node.text or "" for node in item.findall(f".//{{{SHEET_NS}}}t")]
        values.append("".join(text_parts))
    return values


def _load_sheet_targets(archive: ZipFile) -> list[tuple[str, str]]:
    if "xl/workbook.xml" not in archive.namelist():
        sheet_names = sorted(
            name
            for name in archive.namelist()
            if name.startswith("xl/worksheets/") and name.endswith(".xml")
        )
        return [
            (Path(sheet_name).stem.replace("sheet", "Sheet "), sheet_name)
            for sheet_name in sheet_names
        ]

    workbook_root = ET.fromstring(archive.read("xl/workbook.xml"))
    rels_root = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    relationships = {
        rel.attrib["Id"]: rel.attrib["Target"]
        for rel in rels_root.findall(f".//{{{PKG_REL_NS}}}Relationship")
    }

    targets: list[tuple[str, str]] = []
    for sheet in workbook_root.findall(f".//{{{SHEET_NS}}}sheet"):
        name = sheet.attrib.get("name", "Sheet")
        rel_id = sheet.attrib.get(f"{{{REL_NS}}}id")
        if not rel_id:
            continue
        target = relationships.get(rel_id)
        if not target:
            continue
        targets.append((name, f"xl/{target}"))
    return targets


def _cell_text(cell: ET.Element, shared_strings: list[str]) -> str:
    cell_type = cell.attrib.get("t")
    if cell_type == "inlineStr":
        node = cell.find(f".//{{{SHEET_NS}}}t")
        return (node.text or "").strip() if node is not None else ""

    value_node = cell.find(f"./{{{SHEET_NS}}}v")
    value = (value_node.text or "").strip() if value_node is not None else ""

    if cell_type == "s" and value.isdigit():
        index = int(value)
        if 0 <= index < len(shared_strings):
            return shared_strings[index]
        return ""
    return value


def _sheet_rows(sheet_xml: bytes, shared_strings: list[str]) -> list[list[str]]:
    root = ET.fromstring(sheet_xml)
    rows: list[list[str]] = []

    for row in root.findall(f".//{{{SHEET_NS}}}sheetData/{{{SHEET_NS}}}row"):
        values: list[str] = []
        for cell in row.findall(f"./{{{SHEET_NS}}}c"):
            values.append(_cell_text(cell, shared_strings))
        while values and values[-1] == "":
            values.pop()
        if values:
            rows.append(values)

    return rows


def _table_markdown(rows: list[list[str]]) -> str:
    column_count = max(len(row) for row in rows)
    normalized = [row + [""] * (column_count - len(row)) for row in rows]
    header = normalized[0]
    if all(not value for value in header):
        header = [f"Column {index + 1}" for index in range(column_count)]
    divider = ["---"] * column_count
    body = normalized[1:]

    lines = [
        f"| {' | '.join(_escape_cell(value) for value in header)} |",
        f"| {' | '.join(divider)} |",
    ]
    lines.extend(f"| {' | '.join(_escape_cell(value) for value in row)} |" for row in body)
    return "\n".join(lines)


def convert_xlsx(source_path: Path) -> ConversionResult:
    try:
        with ZipFile(source_path) as archive:
            shared_strings = _read_shared_strings(archive)
            targets = _load_sheet_targets(archive)
            sections: list[str] = []

            for sheet_name, target in targets:
                rows = _sheet_rows(archive.read(target), shared_strings)
                if not rows:
                    continue
                sections.append(f"## Sheet: {sheet_name}\n\n{_table_markdown(rows)}")
    except (BadZipFile, KeyError) as exc:
        return ConversionResult(markdown="", warnings=(f"xlsx parse warning: {exc}",))

    if not sections:
        return ConversionResult(markdown="", warnings=("xlsx workbook contains no tabular rows",))

    return ConversionResult(markdown="\n\n".join(sections))
