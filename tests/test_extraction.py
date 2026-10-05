import io

import pytest

from pyxtxt import xtxt
from pyxtxt.estrattori import estrattori

RTF_SOURCE = r"{\rtf1\ansi{\fonttbl\f0\fswiss Helvetica;}\f0\pard Hello {\b RTF} world.\par}"
TEX_SOURCE = "\\documentclass{article}\n\\begin{document}\n\\section{Intro}\nHello \\textbf{LaTeX}.\n\\end{document}\n"
MD_SOURCE = "# Title\n\nSome **bold** text\n\n- item\n"


def test_plain_text_from_bytes():
    assert xtxt(b"just some plain text") == "just some plain text"


def test_missing_file_returns_none(tmp_path):
    assert xtxt(str(tmp_path / "does-not-exist.txt")) is None


def test_unsupported_type_returns_none():
    assert xtxt(b"\x00\x01\x02\x03" * 64) is None


def test_markdown_file(tmp_path):
    pytest.importorskip("markdown")
    pytest.importorskip("bs4")
    path = tmp_path / "doc.md"
    path.write_text(MD_SOURCE)
    text = xtxt(str(path))
    assert "Title" in text and "bold" in text
    assert "**" not in text and "#" not in text


def test_markdown_buffer_uses_name_hint():
    pytest.importorskip("markdown")
    pytest.importorskip("bs4")
    buffer = io.BytesIO(MD_SOURCE.encode())
    buffer.name = "notes.md"
    text = xtxt(buffer)
    assert "**" not in text and "Title" in text


def test_rtf_file(tmp_path):
    pytest.importorskip("striprtf")
    path = tmp_path / "doc.rtf"
    path.write_text(RTF_SOURCE)
    text = xtxt(str(path))
    assert "\\rtf1" not in text
    assert "Hello RTF world." in text


def test_latex_file(tmp_path):
    pytest.importorskip("pylatexenc")
    path = tmp_path / "doc.tex"
    path.write_text(TEX_SOURCE)
    text = xtxt(str(path))
    assert "\\documentclass" not in text
    assert "LaTeX" in text


def test_corrupted_pdf_returns_none_not_string(tmp_path):
    pytest.importorskip("pymupdf")
    path = tmp_path / "broken.pdf"
    path.write_bytes(b"%PDF-1.4\n garbage")
    assert xtxt(str(path)) is None


def test_pdf_text(tmp_path):
    fitz = pytest.importorskip("pymupdf")
    path = tmp_path / "doc.pdf"
    doc = fitz.open()
    doc.new_page().insert_text((72, 72), "Hello PDF")
    doc.save(str(path))
    assert "Hello PDF" in xtxt(str(path))


def test_xlsx_is_not_truncated(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    path = tmp_path / "big.xlsx"
    wb = openpyxl.Workbook()
    for i in range(500):
        wb.active.append([i, f"row{i}"])
    wb.save(str(path))
    text = xtxt(str(path))
    assert "0 | row0" in text
    assert "499 | row499" in text


def test_xlsx_row_limit_is_still_available(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    from pyxtxt.estrattori.xlsx import xtxt_xlsx

    wb = openpyxl.Workbook()
    for i in range(50):
        wb.active.append([i])
    buffer = io.BytesIO()
    wb.save(buffer)
    text = xtxt_xlsx(buffer, max_rows_per_sheet=10)
    assert "9" in text.splitlines() and "10" not in text.splitlines()


def test_docx_text(tmp_path):
    docx = pytest.importorskip("docx")
    path = tmp_path / "doc.docx"
    document = docx.Document()
    document.add_paragraph("Hello DOCX")
    document.save(str(path))
    assert "Hello DOCX" in xtxt(str(path))


def test_html_text():
    pytest.importorskip("bs4")
    text = xtxt(b"<html><body><p>Visible paragraph</p></body></html>")
    assert "Visible paragraph" in text and "<p>" not in text


def test_ollama_ocr_takes_precedence_over_easyocr():
    """Extractor modules load in sorted order, so ocr_ollama always overrides ocr."""
    pytest.importorskip("ollama")
    pytest.importorskip("PIL")
    assert estrattori["image/png"].__module__.endswith("ocr_ollama")
