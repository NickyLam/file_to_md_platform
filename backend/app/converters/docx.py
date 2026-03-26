from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile

from backend.app.converters.base import ConversionResult


WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": WORD_NS}


def _heading_prefix(style_value: str) -> str:
    suffix = "".join(char for char in style_value if char.isdigit())
    level = int(suffix) if suffix else 1
    level = max(1, min(level, 6))
    return "#" * level


def convert_docx(source_path: Path) -> ConversionResult:
    warnings: list[str] = []
    try:
        with ZipFile(source_path) as archive:
            document_xml = archive.read("word/document.xml")
    except (BadZipFile, KeyError) as exc:
        return ConversionResult(markdown="", warnings=(f"docx parse warning: {exc}",))

    root = ET.fromstring(document_xml)
    lines: list[str] = []
    heading_used = False

    for paragraph in root.findall(".//w:p", NS):
        text_parts = [node.text for node in paragraph.findall(".//w:t", NS) if node.text]
        line = "".join(text_parts).strip()
        if not line:
            continue

        style = paragraph.find("./w:pPr/w:pStyle", NS)
        if style is not None:
            style_value = style.attrib.get(f"{{{WORD_NS}}}val", "")
            if style_value.lower().startswith("heading"):
                lines.append(f"{_heading_prefix(style_value)} {line}")
                heading_used = True
                continue

        if not heading_used:
            lines.append(f"# {line}")
            heading_used = True
            continue

        lines.append(line)

    if not lines:
        warnings.append("docx document contains no textual paragraphs")

    return ConversionResult(markdown="\n\n".join(lines), warnings=tuple(warnings))
