"""Error reporting: None by default, exceptions with raise_errors=True, messages via logging."""
import subprocess
import sys
import textwrap

import pytest

import pyxtxt
from pyxtxt import ExtractionError, UnsupportedFormatError, xtxt

UNSUPPORTED_BYTES = b"\x00\x01\x02\x03" * 64


def test_failure_returns_none_and_logs_a_warning(tmp_path, caplog):
    with caplog.at_level("WARNING", logger="pyxtxt"):
        assert xtxt(str(tmp_path / "missing.pdf")) is None
    assert any(record.name == "pyxtxt.core" and "File opening error" in record.getMessage()
               for record in caplog.records)


def test_raise_errors_missing_file(tmp_path):
    with pytest.raises(ExtractionError) as excinfo:
        xtxt(str(tmp_path / "missing.pdf"), raise_errors=True)
    assert isinstance(excinfo.value.__cause__, FileNotFoundError)


def test_raise_errors_unsupported_type():
    with pytest.raises(UnsupportedFormatError):
        xtxt(UNSUPPORTED_BYTES, raise_errors=True)


def test_raise_errors_text_mode_file_object(tmp_path):
    path = tmp_path / "doc.txt"
    path.write_text("hello")
    with open(path) as f, pytest.raises(ExtractionError):
        xtxt(f, raise_errors=True)


def test_raise_errors_corrupted_pdf(tmp_path):
    pytest.importorskip("pymupdf")
    path = tmp_path / "broken.pdf"
    path.write_bytes(b"%PDF-1.4\n garbage")
    assert xtxt(str(path)) is None
    with pytest.raises(ExtractionError) as excinfo:
        xtxt(str(path), raise_errors=True)
    assert excinfo.value.__cause__ is not None


def test_raise_errors_invalid_docx():
    pytest.importorskip("docx")
    import io

    buffer = io.BytesIO(b"not a zip archive")
    buffer.mimeType = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    buffer.name = "fake.docx"
    with pytest.raises(ExtractionError, match="not a ZIP"):
        xtxt(buffer, raise_errors=True)


def test_file_without_text_returns_empty_string_not_none(tmp_path):
    fitz = pytest.importorskip("pymupdf")
    path = tmp_path / "blank.pdf"
    doc = fitz.open()
    doc.new_page()
    doc.save(str(path))
    assert xtxt(str(path), raise_errors=True).strip() == ""


def test_xtxt_from_url_errors(monkeypatch):
    requests = pytest.importorskip("requests")

    def refuse(url, **kwargs):
        raise requests.ConnectionError("no network in tests")

    monkeypatch.setattr(requests, "get", refuse)
    assert pyxtxt.xtxt_from_url("https://example.invalid/doc.pdf") is None
    with pytest.raises(ExtractionError):
        pyxtxt.xtxt_from_url("https://example.invalid/doc.pdf", raise_errors=True)


def _run_python(code):
    return subprocess.run([sys.executable, "-c", textwrap.dedent(code)], capture_output=True, text=True)


def test_library_prints_nothing_by_default():
    result = _run_python(
        f"""
        from pyxtxt import xtxt
        assert xtxt("/does/not/exist.pdf") is None
        assert xtxt({UNSUPPORTED_BYTES!r}) is None
        """
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == "" and result.stderr == ""


def test_messages_visible_when_logging_is_configured():
    result = _run_python(
        """
        import logging
        logging.basicConfig(level=logging.INFO)
        from pyxtxt import xtxt
        xtxt("/does/not/exist.pdf")
        """
    )
    assert result.returncode == 0, result.stderr
    assert "WARNING:pyxtxt.core:File opening error" in result.stderr


def test_available_formats_alias():
    assert pyxtxt.xtxt_available_formats is pyxtxt.extxt_available_formats
    assert "text/plain" in pyxtxt.xtxt_available_formats()
