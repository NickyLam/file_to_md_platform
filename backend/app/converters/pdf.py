import re
from pathlib import Path

from backend.app.converters.base import ConversionResult


PDF_TEXT_RE = re.compile(r"\((?P<text>(?:\\.|[^\\()])*)\)\s*T[Jj]")


def _decode_pdf_literal(raw_text: str) -> str:
    decoded: list[str] = []
    index = 0
    while index < len(raw_text):
        char = raw_text[index]
        if char == "\\" and index + 1 < len(raw_text):
            index += 1
            escaped = raw_text[index]
            if escaped in {"\\", "(", ")"}:
                decoded.append(escaped)
            elif escaped == "n":
                decoded.append("\n")
            else:
                decoded.append(escaped)
        else:
            decoded.append(char)
        index += 1
    return "".join(decoded)


def convert_pdf(source_path: Path) -> ConversionResult:
    raw_text = source_path.read_bytes().decode("latin-1", errors="ignore")
    matches = [
        _decode_pdf_literal(match.group("text")).strip()
        for match in PDF_TEXT_RE.finditer(raw_text)
    ]
    visible_lines = [line for line in matches if any(char.isalnum() for char in line)]

    if not visible_lines:
        return ConversionResult(
            markdown=f"# {source_path.stem}\n\n(plain-text extraction unavailable)",
            warnings=("unable to extract structured pdf text",),
        )

    markdown = f"# {source_path.stem}\n\n" + "\n\n".join(visible_lines)
    return ConversionResult(markdown=markdown)
