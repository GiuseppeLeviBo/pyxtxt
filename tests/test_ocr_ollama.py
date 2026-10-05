"""Ollama OCR logic, with the Ollama client replaced by fakes (no server needed)."""
import io

import pytest

pytest.importorskip("ollama")
PIL_Image = pytest.importorskip("PIL.Image")

import pyxtxt.estrattori.ocr_ollama as ocr_ollama  # noqa: E402


@pytest.fixture(autouse=True)
def default_config():
    ocr_ollama.reset_ollama_config()
    yield
    ocr_ollama.reset_ollama_config()


def _png_bytes():
    buffer = io.BytesIO()
    PIL_Image.new("RGB", (10, 10), "white").save(buffer, "PNG")
    return buffer.getvalue()


def test_unreachable_server_does_not_try_fallback_models(monkeypatch):
    calls = []

    def unreachable(**kwargs):
        calls.append(kwargs["model"])
        raise ConnectionError("Failed to connect to Ollama")

    monkeypatch.setattr(ocr_ollama.ollama, "generate", unreachable)
    assert ocr_ollama.xtxt_image_ocr_ollama(io.BytesIO(_png_bytes())) == ""
    assert calls == ["gemma3:4b"]


def test_with_confidence_uses_the_configured_context(monkeypatch):
    prompts = []

    def fake_generate(**kwargs):
        prompts.append(kwargs["prompt"])
        return {"response": "Patient ID 12345, exam date 2024-01-02."}

    monkeypatch.setattr(ocr_ollama.ollama, "generate", fake_generate)
    ocr_ollama.set_ollama_config(context="xray")
    text, confidence = ocr_ollama.xtxt_image_with_confidence(io.BytesIO(_png_bytes()))
    assert "X-ray" in prompts[0]
    assert text.startswith("Patient ID") and confidence > 0


def test_ocr_and_confidence_variants_send_the_same_prompt(monkeypatch):
    prompts = []

    def fake_generate(**kwargs):
        prompts.append(kwargs["prompt"])
        return {"response": "Invoice 42: total 10.50 EUR, due 2024-03-01."}

    monkeypatch.setattr(ocr_ollama.ollama, "generate", fake_generate)
    ocr_ollama.set_ollama_config(context="medical", language="italian")
    ocr_ollama.xtxt_image_ocr_ollama(io.BytesIO(_png_bytes()), mode="describe")
    ocr_ollama.xtxt_image_with_confidence(io.BytesIO(_png_bytes()), mode="describe")
    assert len(prompts) == 2 and prompts[0] == prompts[1]


def test_hallucination_keywords_match_whole_words():
    score = ocr_ollama._calculate_confidence_score
    neutral = score("The science section lists 12 titles.", "ocr")
    assert score("The romance section lists 12 titles.", "ocr") == neutral
    assert score("An Egyptian papyrus with 12 lines.", "ocr") < score("An ordinary receipt with 12 lines.", "ocr")


def test_xtxt_reports_unreachable_server_as_failure(monkeypatch):
    from pyxtxt import ExtractionError, xtxt

    def unreachable(**kwargs):
        raise ConnectionError("Failed to connect to Ollama")

    monkeypatch.setattr(ocr_ollama.ollama, "generate", unreachable)
    assert xtxt(_png_bytes()) is None
    with pytest.raises(ExtractionError) as excinfo:
        xtxt(_png_bytes(), raise_errors=True)
    assert isinstance(excinfo.value.__cause__, ConnectionError)


def test_public_helpers_keep_returning_empty_results_on_errors(monkeypatch):
    def unreachable(**kwargs):
        raise ConnectionError("Failed to connect to Ollama")

    monkeypatch.setattr(ocr_ollama.ollama, "generate", unreachable)
    assert ocr_ollama.xtxt_image_describe(io.BytesIO(_png_bytes())) == ""
    assert ocr_ollama.xtxt_image_with_confidence(io.BytesIO(_png_bytes())) == ("", 0.0)


def test_all_models_failing_is_an_error_for_xtxt(monkeypatch):
    from pyxtxt import ExtractionError, xtxt

    def model_missing(**kwargs):
        raise ocr_ollama.ollama.ResponseError(f"model '{kwargs['model']}' not found")

    monkeypatch.setattr(ocr_ollama.ollama, "generate", model_missing)
    with pytest.raises(ExtractionError, match="No Ollama model could process the image"):
        xtxt(_png_bytes(), raise_errors=True)
